"""CE-18 sabotage table (DEC-11): break what each rollback test or guard protects; every run must
go red, for the reason named in its row.

Run from the repo root: `<interpreter> tools/sabotage_ce18.py`. Each row replaces one exact string
(it must occur exactly once, or the script stops naming it), runs the named tests with a fresh
bytecode cache (PYTHONPYCACHEPREFIX, CLAUDE.md § Sabotage rule), checks the run is red and its
output holds the row's reason, then puts the file's bytes back and checks they match.
"""
import hashlib, os, pathlib, subprocess, sys, tempfile

PY = sys.executable
T = "tests/test_rollback_recipe.py"
KIT_P = "src/context_engine/kit/docs/runbooks/procedures.md"
KP = KIT_P + "," + "docs/runbooks/procedures.md"  # both copies: the tests read the repo's, the kit test keeps them byte-equal
FW = "docs/framework/FRAMEWORK.md"
SK = "plugin/skills/rollback-and-close/SKILL.md"
S = [
    # the new tests
    ("trailer filter dropped", T, 'if key in keys.split(",")]', "]", T + "::test_the_trailer_finds_only_the_sessions_own_commits", "assert ["),
    ("touched range loses the first commit", T, 'TOUCHED = "git log --format=\'%h %(trailers:key=Session,valueonly)\' <first>^..HEAD', 'TOUCHED = "git log --format=\'%h %(trailers:key=Session,valueonly)\' <first>..HEAD', T + "::test_the_touched_query_tells_a_restore_from_a_revert_by_hunk", "assert ["),
    ("restore by checkout writes the index", T, 'RESTORE = "git restore --source=<first>^ --worktree -- <path>"', 'RESTORE = "git checkout <first>^ -- <path>"', T + "::test_a_restore_by_path_leaves_the_index_as_other_writers_staged_it", "the restore wrote the index"),
    ("restore from the commit itself keeps the created file", T, 'RESTORE = "git restore --source=<first>^ --worktree -- <path>"', 'RESTORE = "git restore --source=<first> --worktree -- <path>"', T + "::test_a_file_the_session_created_is_deleted_and_committed_by_path", "the restore left a file its source does not have"),
    ("commit -a instead of by path", T, '"commit", "-q", "-o", "-m", f"Roll back session {A}", "--", "new.txt"', '"commit", "-q", "-a", "-m", f"Roll back session {A}"', T + "::test_a_file_the_session_created_is_deleted_and_committed_by_path", "keep.txt"),
    ("patch taken against HEAD, not the commit", T, 'PATCH = "git diff --binary <c>^ <c> -- <path> > <patch>"', 'PATCH = "git diff --binary <c>^ HEAD -- <path> > <patch>"', T + "::test_a_disjoint_hunk_reverts_and_leaves_the_other_writers_line", "line 28 by B"),
    ("check replaced by apply --reject", T, 'CHECK = "git apply -R --check <patch>"', 'CHECK = "git apply -R --reject <patch>"', T + "::test_an_overlapping_hunk_is_refused_and_the_file_is_left_untouched", "a refused check changed the file"),
    ("runbook step 4 runs git checkout", KP, "`git restore --source=HEAD --worktree -- <path>` |", "`git restore --source=HEAD --worktree -- <path>`; `git checkout <first>^ -- <path>` |", T + "::test_no_step_of_the_rollback_runs_a_command_the_shared_tree_forbids", "git checkout"),
    ("runbook drops --worktree", KP, "`git restore --source=<first>^ --worktree -- <path>` (where", "`git restore --source=<first>^ -- <path>` (where", T + "::test_the_runbook_gives_the_commands_these_tests_run", "no longer gives"),
    # the existing guards, on the new text
    ("a step labelled 8", KP, "| 7 | Close as § Clean close:", "| 8 | Close as § Clean close:", "tests/test_runbook.py::test_every_framework_step_a_procedure_cites_exists", "step 8"),
    ("step 3 loses its banner set link", KP, "; [§ banner set](manual-mode.md#context-engine-banner-set) | a record's file", " | a record's file", "tests/test_runbook.py::test_every_procedure_step_names_an_existing_operation_and_its_by_hand_section", "manual-mode.md#context-engine-banner-set"),
    ("a pipe inside a step cell", KP, "| 5 | Run `<gate>` on the result;", "| 5 | Run `<gate>` a | b on the result;", "tests/test_runbook.py::test_every_procedure_step_names_an_existing_operation_and_its_by_hand_section", "got 6 cells"),
    ("map row left as not designed", KP, "| §6.13 Rollback and close | § Rollback and close |", "| §6.13 Rollback and close | not designed yet: no steps |", "tests/test_runbook.py::test_every_framework_procedure_has_a_procedures_section", "Rollback and close is not in the map"),
    ("§6.13 loses an item", FW, "\n5. **Run the gate on the result.**", "\n**Run the gate on the result.**", "tests/test_runbook.py::test_every_framework_step_a_procedure_cites_exists", "step 5"),
    ("skill points at no procedure", SK, "Runbook: `docs/runbooks/procedures.md` § Rollback and close", "Runbook: `docs/runbooks/procedures.md` § Pause", "tests/test_plugin.py::test_every_procedure_but_session_start_has_a_skill", "Rollback and close"),
    ("a skill quote changed by one word", SK, "- Commit by path, titled with no task id first", "- Commit by path, titled with no task name first", "tests/test_plugin.py::test_every_line_a_skill_adds_is_quoted_word_for_word_from_its_sections", "not word for word"),
    ("only the kit copy edited", KIT_P, "Undo by operation (step 3), by the op line", "Undo by operation (step 3), by each op line", "tests/test_kit.py::test_the_kit_runbooks_are_this_repos_runbooks", "procedures.md"),
    ("§6.13 says ritual", FW, "is the by-hand fallback, P16)", "is the ritual fallback, P16)", "tests/test_kit.py::test_no_living_framework_text_says_ritual", "ritual"),
    ("§6.13 cites a repo id", FW, "**Who decides:** a rollback discards work", "**Who decides** (US-13): a rollback discards work", "tests/test_kit.py::test_the_kit_and_framework_carry_none_of_this_repos_ids_or_paths", "US-13"),
]


def main() -> int:
    bad = []
    for why, path, old, new, test, reason in S:
        files = [pathlib.Path(x) for x in path.split(",")]
        saved = {p: p.read_bytes() for p in files}
        for p, data in saved.items():
            text = data.decode("utf-8")
            assert text.count(old) == 1, f"{why}: pattern occurs {text.count(old)} times in {p}: {old!r}"
            p.write_bytes(text.replace(old, new).encode("utf-8"))
        try:
            env = dict(os.environ, PYTHONPYCACHEPREFIX=tempfile.mkdtemp(prefix="ce18-pyc-"))
            r = subprocess.run([PY, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", test], capture_output=True, text=True, env=env)
            out = r.stdout + r.stderr
            red, right = r.returncode != 0, reason in out
        finally:
            for p, data in saved.items():
                p.write_bytes(data)
        for p, data in saved.items():
            assert hashlib.sha256(p.read_bytes()).digest() == hashlib.sha256(data).digest(), f"{why}: {p} not restored"
        print(f"{'RED ' if red and right else 'MISS'} {why} -> {test.split('::')[-1]}" + ("" if right else f" (reason {reason!r} not in output)"))
        if not (red and right):
            bad.append(why)
    print("all red for the right reason" if not bad else f"NOT RED: {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
