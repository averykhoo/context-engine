"""CE-78 sabotage table (DEC-11): break what each scoped-gate test and guard protects; every run
must go red, and red for the reason the row names. The checker is CE-49's
(`tools/sabotage_ce49.py::run`): a fresh bytecode cache per run, every file restored byte for byte.

Run from the repo root: `<interpreter> tools/sabotage_ce78.py [row-number ...]` (no numbers: every
row). The patterns are exact source text from 2026-10-14g (the F1 and F2 rows: 2026-10-15a);
when the code moves, a pattern stops matching and the script stops with an AssertionError naming
it.

The last rows break this repo's own [gate.scopes.code]: excluding a kept doc (docs/runbooks/)
makes the scope guard fail the tests that read it, which is how a fail-open exclusion is caught.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from sabotage_ce49 import run  # noqa: E402

GA = "src/context_engine/gate.py"
SG = "src/context_engine/scope_guard.py"
WK = "src/context_engine/working.py"
T = "tests/test_gate.py"
NR = "DID NOT RAISE"
ADD = "test_the_id_survives_git_add_and_git_commit_and_moves_on_an_edit"
DEL = "test_the_id_survives_a_commit_of_a_deletion_or_rename"
CTRL = "test_control_a_deletion_or_a_rename_does_move_the_id"
HAND = "test_manual_mode_s_by_hand_id_is_the_engine_s"
GREEN = "test_a_green_run_covers_its_scopes_until_a_file_in_scope_changes"
CMD = "test_a_row_counts_only_for_the_command_configured_now"
INC = "test_a_run_whose_files_change_while_it_runs_counts_for_nothing"
IGN = "test_the_run_ledger_is_gitignored_and_a_tracked_one_is_refused"
COMMIT = "test_commit_refuses_a_code_path_no_green_run_covers_and_takes_a_records_path"
DELC = "test_commit_refuses_a_deleted_code_path_too_and_checks_nothing_without_require"
READ = "test_readers_are_a_part_keyed_on_every_file_so_a_change_outside_the_scope_re_runs_only_them"
ONLY = "test_commit_checks_only_the_scope_so_an_engine_write_after_the_gate_run_does_not_refuse_it"
KEPT = "test_a_run_records_each_scope_whose_files_did_not_move_while_it_ran"
GUARD = "test_the_scope_guard_fails_a_test_that_reads_an_excluded_path_unless_it_is_a_reader[on]"
CI = "test_the_procedures_runbook_gives_ci_s_by_hand_fallback_and_the_contract_names_the_workflow"

# (file, pattern, replacement, pytest selection, the tests that must fail (and only those), reason)
S = [
 # the id: a pending deletion hashes as a committed one (zanzibar 2026-09-05b), and its control
 (GA, "        return None  # in the index, gone from the work tree", '        return b"absent"  # in the index, gone from the work tree',
  f"{T} -k survives or control or by_hand", [DEL, HAND], "code_id(repo) == pending"),
 (GA, '        h.update(rel.encode("utf-8", "surrogateescape") + b"\\0" + fp + b"\\0")', '        h.update(fp + b"\\0")',
  f"{T} -k survives or control or by_hand", [CTRL, HAND], "not in (start, deleted)"),
 # the id holds no commit (zanzibar GS-1)
 (GA, "    h = hashlib.sha256(scope.header())", '    h = hashlib.sha256(scope.header() + _git(root, "rev-parse", "HEAD"))',
  f"{T} -k survives or control or by_hand", [ADD, DEL, HAND], "git commit moved the id"),
 # a row covers only its own files, with the command configured now
 (GA, '        if row.get("scopes", {}).get(key) == here and row.get("status") in (PASSED, FAILED):', '        if row.get("status") in (PASSED, FAILED):',
  f"{T} -k green_run or readers_are", [GREEN, READ], "NOT covered"),
 (GA, ' and list(last.get("command", [])) == list(gate.command)', "",
  f"{T} -k command or red_run_after", [CMD], "code: NOT covered"),
 # a run whose files moved counts for nothing
 (GA, "    status = INCONSISTENT if not kept else PASSED if code == 0 else FAILED", "    status = PASSED if code == 0 else FAILED",
  f"{T} -k counts_for_nothing", [INC], "gate INCONSISTENT"),
 # ... and only the ids that moved count for nothing: the rest are recorded (F2, 2026-10-14g review)
 (GA, "    moved = sorted(k for k in before if before[k] != after.get(k))", "    moved = sorted(before) if after != before else []",
  f"{T} -k counts_for_nothing or did_not_move", [KEPT], "gate PASSED"),
 # the ledger is gitignored and untracked
 (GA, "    if not _ignored(root, gate.ledger) or gate.ledger in files(root):", "    if False:",
  f"{T} -k gitignored", [IGN], NR),
 # the commit refusal; it checks the scope alone, not its readers (F1, 2026-10-14g review)
 (WK, "        GATE.check_commit(self.root, self.store.config.gate, rels)", "        pass",
  f"{T} -k commit_refuses or commit_checks", [COMMIT, DELC, ONLY], NR),
 (GA, "    if not covering(rows, gate, scope.name, here):",
  '    if not covering(rows, gate, scope.name, here) or (scope.readers and not covering(rows, gate, f"{scope.name}+readers", scope_id(root, readers_scope(scope), listed))):',
  f"{T} -k commit_refuses or commit_checks", [ONLY], "Refusal: refused: src/a.py is in gate scope 'code'"),
 # `gate status --require <scope>+readers` checks the readers' part
 (GA, "    code, part = ok[name], ok[require] if plus else True", "    code, part = ok[name], True",
  f"{T} -k readers_are", [READ], '"code+readers: NOT covered" in text and "gate run --readers" in text, text'),
 # the scope guard: open, list, process
 (SG, "                if rel in self.excluded:", "                if False:",
  f"{T} -k scope_guard", [GUARD], "failed =="),
 (SG, "                if rel is not None and self.dirs.get(rel):", "                if False:",
  f"{T} -k scope_guard", [GUARD], "failed =="),
 (SG, "            if rel is not None and not outside:", "            if False:",
  f"{T} -k scope_guard", [GUARD], "failed =="),
 # this repo's code scope: excluding a doc a test reads makes the guard fail that test
 ("context.toml", '"README.md", "docs/charter.md", "docs/criteria.md"]', '"README.md", "docs/charter.md", "docs/criteria.md", "docs/runbooks/**"]',
  "tests/test_ci.py -k procedures_runbook", [CI], "scope guard"),
]


if __name__ == "__main__":
    only = {int(a) for a in sys.argv[1:]}
    ok = True
    for n, row in enumerate(S, 1):
        if only and n not in only:
            continue
        red, why = run(*row)
        ok &= red
        print(f"{n:2} {'RED ' if red else 'NOT RED!'} {row[0].rsplit('/', 1)[-1]:15} {row[1].strip().splitlines()[0][:50]!r:54} -> {why}", flush=True)
    print("ALL RED" if ok else "SOME ROWS ARE NOT RED FOR THEIR REASON")
