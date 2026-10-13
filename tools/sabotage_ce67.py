"""CE-67 sabotage table (DEC-11): break what each CI-parity guard protects; every run must go red,
and red for the reason the row names. The checker is CE-49's (`tools/sabotage_ce49.py::run`).

Run from the repo root: `<interpreter> tools/sabotage_ce67.py [row-number ...]` (no numbers: every
row). It restores every file it touches, byte for byte. The patterns are exact source text from
2026-10-13d; when the code moves, a pattern stops matching and the script stops with an
AssertionError naming it.

These rows run on the owner's Windows machine. Row 1 goes red only where git has a system or global
config (Git for Windows ships one); rows 3's red is the Windows text-mode `\\r\\n`. The Linux half of
the evidence is `tools/linux_gate.py` itself: red on 39e09ca with CI's exact three failures, green
on the fix (docs/evidence/ci-divergence-2026-10-13.md).
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from sabotage_ce49 import run  # noqa: E402

CONF = "tests/conftest.py"
TC = "tests/test_commit.py"
LG = "tools/linux_gate.py"
PORT = "tests/test_portability.py"
GITCFG = "test_git_in_a_test_reads_no_system_or_global_config"
PATCH = "test_no_test_patches_an_attribute_of_a_standard_library_module"
TRAIL = "test_the_session_commit_keeps_its_trailer_block_and_adds_session_to_it"
LGT = "test_the_local_linux_gate_runs_the_workflow_s_steps_on_its_runner_s_shape"
CI = "tests/test_ci.py -k local_linux_gate"

# (file, pattern, replacement, pytest selection, the tests that must fail (and only those), reason)
S = [
 # tests read no machine git config
 (CONF, '    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")\n    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(empty))', "    pass",
  f"{PORT} -k reads_no_system", [GITCFG], "scopes <="),
 # a test patching the time module itself, as 39e09ca's lock test did
 (TC, '    monkeypatch.setattr(C, "time", types.SimpleNamespace(**{**vars(time), "sleep": lambda s: (waits.append(s), lock.unlink(missing_ok=True))}))',
  '    monkeypatch.setattr(C.time, "sleep", lambda s: (waits.append(s), lock.unlink(missing_ok=True)))',
  f"{PORT} -k patches_an_attribute", [PATCH], "hits == []"),
 # the trailer referee in text mode, as 39e09ca's was
 (TC, 'input=msg.encode("utf-8"), capture_output=True, check=True)\n    return p.stdout.decode("utf-8").splitlines()',
  'input=msg, capture_output=True, text=True, check=True)\n    return p.stdout.splitlines()',
  f"{TC} -k keeps_its_trailer", [TRAIL], 'trailers(mrepo) == ["Closes: CE-1 continued"'),
 # the local Linux gate drifts from CI
 (LG, "        \" && printf '[safe]\\\\n\\\\tdirectory = *\\\\n' >> /etc/gitconfig\",", '        "",', CI, [LGT], "directory = *"),
 (LG, "INSTALL = 'python -m pip install -q -e \".[dev]\"'", "INSTALL = 'python -m pip install -q -e .'", CI, [LGT], "== runs"),
 (LG, 'return spec.removeprefix(">=").strip()', 'return "3.13"', CI, [LGT], "lg.floor() == floor"),
 (LG, '        f"git -c advice.detachedHead=false checkout -q {sha}",\n', "", CI, [LGT], 'script.index("clone")'),
 (LG, 'RUNNER = "ubuntu:24.04"', 'RUNNER = "python:3.12-slim"', CI, [LGT], 'lg.RUNNER.startswith("ubuntu:")'),
]


if __name__ == "__main__":
    only = {int(a) for a in sys.argv[1:]}
    ok = True
    for n, row in enumerate(S, 1):
        if only and n not in only:
            continue
        red, why = run(*row)
        ok &= red
        print(f"{n:2} {'RED ' if red else 'NOT RED!'} {row[0].rsplit('/', 1)[-1]:16} {row[1].strip().splitlines()[0][:50]!r:54} -> {why}", flush=True)
    print("ALL RED" if ok else "SOME ROWS ARE NOT RED FOR THEIR REASON")
