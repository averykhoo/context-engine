# Does `ulimit -u 200` cap processes in Git Bash on this machine? (2026-11-01, CE-110, DEC-131)

FROZEN 2026-11-01. The probe as it ran in session 2026-10-31a; it decided that rule 3 stays out of the owner's global CLAUDE.md (DEC-131).

Verdict: **ERRORS** (it cannot even be set; the readable value 256 is also not enforced, so there is no working cap).

Machine: Windows 11 Pro 10.0.26200, Git Bash (MSYS2). Measured 2026-11-01 through the Bash tool.

## 1. Baseline

Commands: `ulimit -u; ulimit -a; bash --version | head -1; uname -a`

```
ulimit -u: 256
core file size              (blocks, -c) unlimited
data seg size               (kbytes, -d) unlimited
file size                   (blocks, -f) unlimited
open files                          (-n) 3200
pipe size                (512 bytes, -p) 8
stack size                  (kbytes, -s) 2032
cpu time                   (seconds, -t) unlimited
max user processes                  (-u) 256
virtual memory              (kbytes, -v) unlimited
GNU bash, version 5.2.26(1)-release (x86_64-pc-msys)
MINGW64_NT-10.0-26200 DESKTOP-3RENS5H 3.4.10-87d57229.x86_64 2024-02-14 20:17 UTC x86_64 Msys
```

## 2. Setting the limit

Commands: `ulimit -u 200; echo "rc=$?"; ulimit -u` and the same with `ulimit -S -u 200`

```
/usr/bin/bash: line 1: ulimit: max user processes: cannot modify limit: Invalid argument
rc=1
256
/usr/bin/bash: line 1: ulimit: max user processes: cannot modify limit: Invalid argument
rc=1
256
```

Other values, `for v in 100 255 256 257 1000 unlimited; do ulimit -u $v 2>/dev/null; echo "ulimit -u $v rc=$? now=$(ulimit -u)"; done` (each also rc=1, value unchanged; even setting 256 to itself fails):

```
ulimit -u 100 rc=1 now=256
ulimit -u 255 rc=1 now=256
ulimit -u 256 rc=1 now=256
ulimit -u 257 rc=1 now=256
ulimit -u 1000 rc=1 now=256
ulimit -u unlimited rc=1 now=256
```

## 3. Sabotage probe (fork storm in one subshell)

Command (hard form, then the same with `ulimit -S -u 200`):

```
( ulimit -u 200 2>&1; echo "inner rc=$?"; for i in $(seq 300); do sleep 20 & done 2>&1; echo started=$(jobs -p | wc -l); kill $(jobs -p) 2>/dev/null; wait )
```

Output (identical for both forms):

```
/usr/bin/bash: line 1: ulimit: max user processes: cannot modify limit: Invalid argument
inner rc=1
started=300
```

Control, no ulimit call at all, 500 background `sleep 20`:

```
started=500
```

So 300 and 500 background processes were forked with no fork error, past both the requested 200 and the reported 256. The reported 256 is a constant that Cygwin/MSYS returns for `RLIMIT_NPROC`; it is not enforced.

## 4. Cleanup

`ps | grep sleep` after each probe showed nothing left running.

## Conclusion

`ulimit -u 200` fails with `Invalid argument` and changes nothing; if it were silenced (`2>/dev/null`) it would look like it worked. MSYS2 has no `RLIMIT_NPROC` enforcement, so rule 3 must NOT go into the global CLAUDE.md as a protection.

What would cap a fork storm on this machine: nothing in Git Bash. `.wslconfig` caps only the WSL VM (already 8GB + 2GB swap), and a Windows Job Object with an active-process limit would be the only real mechanism for native Windows processes, which no shell setting provides.
