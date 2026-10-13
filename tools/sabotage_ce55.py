"""CE-55 sabotage table (DEC-11): break what each test of the commit policy (FRAMEWORK §5.5 rule
4: the engine commits at milestones, DEC-36), the task close's commit and `context-engine commit`
guards; every run must go red, and red for the reason the row names.

Run from the repo root: `<interpreter> tools/sabotage_ce55.py [row-number ...]` (no numbers: every
row). It restores every file it touches, byte for byte. The patterns are exact source text from
2026-10-13c; when the code moves, a pattern stops matching and the script stops with an
AssertionError naming it, rather than passing quietly. G-T5 (mutation per criterion) replaces this
hand table. The checker is CE-49's (`tools/sabotage_ce49.py::verdict`), reused as it stands.

A row counts as red only when (1) pytest exits 1 with a test failed (not a collection error, not
"no tests ran"), (2) every test that failed is one the row names, and each one it names failed,
and (3) the row's reason is in a failing statement pytest marks with `>` or in the first `E`
line of a failure.

Each run gets a fresh bytecode cache (PYTHONPYCACHEPREFIX): a same-length sabotage written in the
same second as the previous restore would otherwise run the stale .pyc (seen 2026-10-08d).
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from sabotage_ce49 import run  # noqa: E402  (the checker: CE-49's, unchanged)

CF = "src/context_engine/config.py"
ST = "src/context_engine/store.py"
WK = "src/context_engine/working.py"
CM = "src/context_engine/commit.py"
CL = "src/context_engine/cli.py"
OP = "src/context_engine/ops.py"
T = "tests/test_commit.py"
WALK = "test_the_milestones_are_dec_36s_and_every_other_write_rides_along"
CLOSE = "test_a_task_close_commits_with_closes_its_body_and_what_rode_along"
LONG = "test_a_long_close_message_is_cut_in_the_title_and_kept_whole_in_the_body"
REFUSED = "test_a_close_refused_after_its_write_commits_the_write_without_closes"
SPENT = "test_a_milestones_settings_are_spent_by_its_own_commit_or_refusal"
POLICY = "test_the_policy_reads_its_three_values_and_ce_45s_bools"
UNKNOWN = "test_an_unknown_policy_refuses_naming_the_three"
UPGRADED = "test_an_upgraded_repo_saying_commit_true_commits_at_milestones"
CARRIES = "test_the_session_commit_carries_its_paths_with_the_op_log_and_the_records_it_names"
TRAIL = "test_the_session_commit_keeps_its_trailer_block_and_adds_session_to_it"
DIRS = "test_the_session_commit_takes_directories_and_absolute_paths"
PARSE = "test_a_milestone_never_commits_a_record_whose_frontmatter_does_not_parse"
REF = "test_the_session_commit_refuses_what_it_cannot_commit_and_commits_nothing"
OUT = "test_the_session_commit_outside_git_refuses"
CLI = "test_the_session_commit_through_the_cli_and_the_mcp_tool"
KIT = "test_a_new_repo_commits_its_kit_through_the_session_commit"
OFF = "test_commit_off_leaves_every_commit_but_a_pauses_to_the_session"
PAUSE = "test_pause_open_records_branch_and_dirty_paths_from_git_and_commits_only_itself"
W = T + " -k milestones_are"
NR = "DID NOT RAISE"
RX = "Regex pattern did not match"
ALL = "committed == MILESTONES"


def k(expr: str) -> str:
    return f"{T} -k {expr}"


MILESTONE_OPS = ["session_close", "session_pause", "close", "ask_answer", "baton_add", "record_new", "amend", "retire", "supersede", "banner_set"]

# (file, pattern, replacement, pytest selection, the tests that must fail (and only those), reason)
S = [
 # the policy: its values, CE-45's bools, a typo refused
 (CF, 'COMMIT_BOOLS = {True: "milestones", False: "off"}', 'COMMIT_BOOLS = {True: "every-write", False: "off"}', k("policy_reads or upgraded"), [f"{POLICY}[True-milestones]", UPGRADED], "load(tmp_path).commit == policy"),
 (CF, "    if commit not in COMMIT_POLICIES:", "    if False:", k("unknown_policy"), [UNKNOWN], NR),
 # when the store commits: a milestone's mark, spent every time; the policy's three cases
 (ST, "        milestone, self.commit_milestone = self.commit_milestone, False", "        milestone = self.commit_milestone", k("settings_are_spent"), [SPENT], "count(mrepo) == before"),
 (ST, "            self.commit_milestone = True\n", "            pass\n", W, [WALK], ALL),
 (ST, '(milestone and policy == "milestones")', '(policy == "milestones")', W, [WALK], ALL),
 (ST, '(milestone and policy == "milestones")', "milestone", k("commit_off"), [f"{OFF}[off]", f"{OFF}[False]"], "count(repo) == before"),
 (ST, '        self._lead.append(f"{op} {rec_id}")', "        pass", k("close_commits_with_closes"), [CLOSE], "Ops: close CE-1"),
 # every milestone is one: drop the mark from each and the walk sees it ride along
 # (a session close left to ride is carried by the next session's pause, whose line then names it)
 *[(WK, f"    @_milestone\n    def {name}(self, ", f"    def {name}(self, ", W, [WALK], 'line.endswith(f"; committed' if name == "session_close" else ALL) for name in MILESTONE_OPS],
 # and the walk sees an operation made a milestone that DEC-36 lets ride, the writing-nothing ones included
 (WK, "    def reindex(self, *, session: str, actor: str) -> str:", "    @_milestone\n    def reindex(self, *, session: str, actor: str) -> str:", W, [WALK], ALL),
 (WK, "    def expire_batons(self, *, session: str, actor: str = HOUSEKEEPER) -> str:", "    @_milestone\n    def expire_batons(self, *, session: str, actor: str = HOUSEKEEPER) -> str:", W, [WALK], ALL),
 # the task close's commit: Closes:, set after the write; its body, title and Ops line
 (WK, '        self.store.commit_trailers = [f"Closes: {rid}"]', "        self.store.commit_trailers = []", k("close_commits_with_closes"), [CLOSE], 'trailers(mrepo) == ["Closes: CE-1"'),
 (WK, '        changes = {"state": "closed", "status": "deprecated", "closed": session, "moved": session}\n',
      '        changes = {"state": "closed", "status": "deprecated", "closed": session, "moved": session}\n        self.store.commit_trailers = [f"Closes: {rid}"]\n', k("close_refused_after"), [REFUSED], "Closes:"),
 (WK, "        self.store.commit_body = ", '        self.store.commit_body = "" if True else ', k("close_commits_with_closes"), [CLOSE], "sabotage in msg"),
 (WK, "        self.store.commit_title = title\n", "", k("close_commits_with_closes"), [CLOSE], 'msg.splitlines()[0] == "CE-1: close; done in abc1234"'),
 (WK, "    if len(line) <= limit:", "    if True:", k("long_close"), [LONG], "len(title) <= C.TITLE_MAX"),
 (OP, "    return 0, e.close(id, msg, body=body, **c.kw)", "    return 0, e.close(id, msg, **c.kw)", k("close_commits_with_closes"), [CLOSE], "sabotage in msg"),
 (CM, '    elif len(parts) > 1:\n        paras.append(_fit("Ops: ", parts, OPS_MAX))', '    elif False:\n        paras.append(_fit("Ops: ", parts, OPS_MAX))', k("close_commits_with_closes"), [CLOSE], "Ops: close CE-1"),
 (CM, "*(k for k in lead if k in keys), ", "", k("close_commits_with_closes"), [CLOSE], "Ops: close CE-1"),
 # the session's own message: Session: where git reads it, once, and only a trailer counts
 (CM, '            paras[-1] += f"\\nSession: {session}"', '            paras.append(f"Session: {session}")', k("keeps_its_trailer or carries_its_paths"), [TRAIL, CARRIES], "trailers(mrepo) =="),
 (CM, "    if not session_trailers(text):", "    if True:", k("keeps_its_trailer"), [TRAIL], 'count("Session:") == 1'),
 (CM, "    while tail > 1 and _is_trailers(paras[tail - 1]):", "    while False:", k("keeps_its_trailer or carries_its_paths"), [TRAIL, CARRIES], "trailers(mrepo) =="),
 (CM, " or ln[:1].isspace()", "", k("keeps_its_trailer"), [TRAIL], 'trailers(mrepo) == ["Closes: CE-1"'),
 (CM, 'for ln in paras[-1].split("\\n") if ln.startswith("Session:")]', 'for ln in "\\n".join(paras).split("\\n") if ln.startswith("Session:")]', k("keeps_its_trailer"), [TRAIL], "in trailers(mrepo)"),
 (CM, "    if len(paras) < 2 or not _is_trailers(paras[-1]):", "    if len(paras) < 2:", k("keeps_its_trailer"), [TRAIL], "trailer names"),
 # what `commit` refuses
 (WK, "        if not message.strip():", "        if False:", k("refuses_what"), [f"{REF}[no-message]"], NR),
 (WK, "        other = [k for k in C.session_trailers(message) if k != session]", "        other = []", k("refuses_what"), [f"{REF}[other-session]"], NR),
 (WK, '        if rel in (".", ""):', "        if False:", k("refuses_what"), [f"{REF}[whole-repo]"], RX),
 (WK, '        if not raw or raw.startswith(":"):', "        if not raw:", k("refuses_what"), [f"{REF}[magic]"], RX),
 (WK, "else self.root / q).resolve().relative_to(self.root).as_posix()", "else self.root / q).resolve().as_posix()", k("refuses_what and outside"), [f"{REF}[outside]"], RX),
 (CM, '        if code == "!!":\n            return Outcome(note=f"{rel} is gitignored;', '        if False:\n            return Outcome(note=f"{rel} is gitignored;', k("refuses_what"), [f"{REF}[ignored]"], RX),
 (CM, "        if any(n in c.stdout for n in NOTHING):", "        if False:", k("refuses_what"), [f"{REF}[unchanged]"], RX),
 (CM, 'return Outcome(note=f"nothing to commit: {oplog} has no line HEAD lacks, and no path was given") if text is not None else Outcome()', "return Outcome()", k("refuses_what"), [f"{REF}[nothing]"], RX),
 (CM, "    if c.returncode != 0:\n        _unstage(git, tmp, untracked)\n        if any(", "    if c.returncode != 0:\n        if any(", k("refuses_what"), [f"{REF}[missing]"], "?? a.py"),
 (CM, '\n        return Outcome(note=f"{root} is in no git work tree") if asked else Outcome()', "\n        return Outcome()", k("outside_git"), [OUT], RX),
 # what `commit` carries: a new file, a directory's new files, a fresh repo's kit; what it counts
 (CM, '        if code == "??" and (root / rel).is_file():', "        if False:", k("carries_its_paths"), [CARRIES], "did not match"),
 (CM, "        elif (root / rel).is_dir():", "        elif False:", k("takes_directories"), [DIRS], "<= set(files_at(mrepo))"),
 (CM, '        paths = [x.strip("\\n") for x in shown.split("\\0") if x.strip("\\n")]', "        pass", k("takes_directories"), [DIRS], 'line == f"committed'),
 (CM, "    if fresh and CONFIG not in given and (", "    if fresh and (", k("kit_through"), [KIT], "context.toml is not committed"),
 # a swept record that does not parse stops the commit (INV-42)
 (CM, "                okf.read_head(root / rel)", "                pass", k("frontmatter_does_not_parse"), [PARSE], "does not parse"),
 # a pause leaves out of its list what its own commit carries (INV-45)
 (WK, "            if path not in carried:", "            if True:", "tests/test_working.py -k pause_open_records", [PAUSE], 'set(rec.doc.get("uncommitted")) =='),
 # the CLI: -F without a BOM, -m paragraphs, --body-file, the verb
 (CL, 'return path.read_text(encoding="utf-8-sig")', 'return path.read_text(encoding="utf-8")', k("cli_and_the_mcp"), [CLI], 'startswith("CE-1: from a file'),
 (CL, "    except UnicodeDecodeError:\n", "    except LookupError:\n", k("cli_and_the_mcp"), [CLI], "UnicodeDecodeError"),
 (CL, '"\\n\\n".join(a["message"])', '" ".join(a["message"])', k("cli_and_the_mcp"), [CLI], 'startswith("CE-1: two'),
 (CL, '        a["body"] = _read(a["body_file"])', "        pass", k("cli_and_the_mcp"), [CLI], "Sabotage: a -> test_b red"),
 (CL, '    ("commit", None): "commit",\n', "", "tests/test_mcp.py -k every_cli_subcommand", ["test_every_cli_subcommand_is_one_operation_and_every_operation_one_tool"], "_cli_subcommands() == set(cli.CLI_OPS)"),
]


if __name__ == "__main__":
    only = {int(a) for a in sys.argv[1:]}
    ok = True
    for n, row in enumerate(S, 1):
        if only and n not in only:
            continue
        red, why = run(*row)
        ok &= red
        print(f"{n:2} {'RED ' if red else 'NOT RED!'} {row[0].rsplit('/', 1)[-1]:11} {row[1].strip().splitlines()[0][:50]!r:54} -> {why}", flush=True)
    print("ALL RED" if ok else "SOME ROWS ARE NOT RED FOR THEIR REASON")
