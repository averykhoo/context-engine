"""A cross-process file lock that works on Windows and POSIX.

Each concurrent Claude Code session runs its own MCP server process (spike/FINDINGS.md), so
the engine's lock has to be held by the operating system, not by a Python object. The lock is
an OS byte-range lock on a lock file: it is released when the holder closes it or dies, so a
crashed process never leaves a stale lock behind.

The timeout is how long the lock may stay with one holder, not how long a caller may wait
(CE-87). The lock is not fair: a process that lets it go takes it back before a waiter's next
try, so under many back-to-back writes one waiter's wait is the sum of every other hold. Each
holder writes a fresh token after the locked byte, and a waiter that sees the token change
starts its deadline again: the lock is changing hands, so nobody is stuck.

Deliberately not handled: re-entrancy. The store takes the lock once per operation.
"""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path

from .errors import Refusal

if sys.platform == "win32":
    import msvcrt

    def _try_lock(fd: int) -> bool:
        os.lseek(fd, 0, os.SEEK_SET)
        try:
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
            return True
        except OSError:
            return False

    def _unlock(fd: int) -> None:
        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)

else:
    import fcntl

    def _try_lock(fd: int) -> bool:
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return True
        except OSError:
            return False

    def _unlock(fd: int) -> None:
        fcntl.flock(fd, fcntl.LOCK_UN)


TOKEN_AT, TOKEN_LEN = 1, 8  # after the locked byte 0: unlocked, so a waiter can read it


def _token(fd: int) -> bytes:
    os.lseek(fd, TOKEN_AT, os.SEEK_SET)
    return os.read(fd, TOKEN_LEN)


def _new_token(fd: int) -> None:
    os.lseek(fd, TOKEN_AT, os.SEEK_SET)
    os.write(fd, os.urandom(TOKEN_LEN // 2).hex().encode("ascii"))  # ASCII: a text-mode fd keeps it as is


class FileLock:
    def __init__(self, path: Path, timeout: float = 30.0, poll: float = 0.01):
        self.path = Path(path)
        self.timeout = timeout
        self.poll = poll
        self._fd: int | None = None

    def __enter__(self) -> "FileLock":
        self.path.parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(self.path, os.O_RDWR | os.O_CREAT, 0o644)
        deadline = time.monotonic() + self.timeout
        seen = _token(fd)
        while not _try_lock(fd):
            token = _token(fd)
            if token != seen:  # the lock changed hands since the last try: its holders are not stuck
                seen, deadline = token, time.monotonic() + self.timeout
            elif time.monotonic() > deadline:
                os.close(fd)
                raise Refusal(
                    f"the engine lock {self.path} was held for over {self.timeout:.0f}s",
                    "another engine process is writing; retry, and if it persists find the "
                    "process holding the lock file",
                )
            time.sleep(self.poll)
        _new_token(fd)
        self._fd = fd
        return self

    def __exit__(self, *exc) -> None:
        assert self._fd is not None
        try:
            _unlock(self._fd)
        finally:
            os.close(self._fd)
            self._fd = None
