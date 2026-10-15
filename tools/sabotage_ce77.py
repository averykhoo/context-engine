"""CE-77 sabotage table (sabotage rule, CLAUDE.md): break what each plugin test guards; every run
must go red.

Run from the repo root, with PYTHONPATH naming this tree's src in a worktree:
`<interpreter> tools/sabotage_ce77.py [row ...]` (every row, or the named ones). It restores
every file it touches, byte for byte. The patterns are exact source text from 2026-10-14g (the quote rows from 2026-10-15a); when
the text moves, a pattern stops matching and the script stops with an AssertionError naming it, rather than passing quietly. Each run gets a
fresh bytecode cache (PYTHONPYCACHEPREFIX), so a same-length sabotage never runs a stale .pyc.
"""
import os, pathlib, subprocess, sys, tempfile

PY_EXE = sys.executable
L = "plugin/scripts/ce-engine"
T = "tests/test_plugin.py"
SK = "plugin/skills/"
S = [
    # the manifests
    ("hook-cmd", "plugin/hooks/hooks.json", '"command": "git",', '"command": "sh",', T + " -k exec_form"),
    ("hook-path", "plugin/hooks/hooks.json", "/scripts/ce-engine", "/scripts/ce_engine", T + " -k runs_orient_with"),
    ("mcp-mode", "plugin/.mcp.json", '"${CLAUDE_PROJECT_DIR}", "mcp"]', '"${CLAUDE_PROJECT_DIR}", "orient"]', T + " -k exec_form"),
    ("market-src", ".claude-plugin/marketplace.json", '"source": "./plugin"', '"source": "./plugins"', T + " -k marketplace"),
    ("lf-attr", ".gitattributes", "plugin/scripts/* text eol=lf\n", "", T + " -k lf_line_endings"),
    ("lf-cr", L, "#!/bin/sh\n", "#!/bin/sh\r\n", T + " -k lf_line_endings"),
    # the launcher
    ("git-env", L, "unset GIT_DIR GIT_WORK_TREE", "unset GIT_WORK_TREE", T + " -k clean_git_environment"),
    ("cd-root", L, 'cd "$root" || exit 1\n', "", T + " -k clean_git_environment"),
    ("no-toml", L, 'if [ ! -f "$root/context.toml" ]; then', "if false; then", T + " -k does_nothing_where"),
    ("dedupe", L, "      exit 0\n    fi\n  done\nfi", "      :\n    fi\n  done\nfi", T + " -k never_runs_twice"),
    ("dedupe-loose", L, "grep -Eq '\"command\"[[:space:]]*:[[:space:]]*\".*context_engine.*orient'", "grep -Eq 'context_engine.*orient'", T + " -k never_runs_twice"),
    ("loud-stdout", L, '    say "orient did not run: $where. Run orient by hand and tell the owner; to fix, $fix."\n', '    say "orient did not run: $where. Run orient by hand and tell the owner; to fix, $fix." >&2\n', T + " -k says_so_in_the_sessions_context"),
    ("pointer-check", L, '  [ -n "$py" ] && [ -f "$py" ] || py=\n', "", T + " -k says_so_in_the_sessions_context"),
    # the venv the test makes is Scripts/python.exe on Windows, bin/python elsewhere
    ("layout-venv", L, ' "$dir/env/Scripts/python.exe"; do', "; do", T + " -k pinned_env_inside") if os.name == "nt" else
    ("layout-venv", L, 'for c in "$dir/env/bin/python" ', "for c in ", T + " -k pinned_env_inside"),
    ("mcp-module", L, 'exec "$py" -m context_engine.mcp --root "$root"', 'exec "$py" -m context_engine --root "$root" orient', T + " -k serves_the_repos_engine"),
    ("mcp-root", L, 'exec "$py" -m context_engine.mcp --root "$root"', 'cd "$OLDPWD"; exec "$py" -m context_engine.mcp', T + " -k serves_the_repos_engine"),
    ("mcp-loud", L, '  say "the MCP server did not start: $where. To fix, $fix." >&2\n  exit 1', '  exit 0', T + " -k the_server_fails"),
    # the skills
    ("skill-name", SK + "pause/SKILL.md", "name: pause\n", "name: pausing\n", T + " -k valid_frontmatter"),
    ("skill-key", SK + "intake/SKILL.md", "\ndescription: Use the moment", "\ndescripton: Use the moment", T + " -k valid_frontmatter"),
    ("skill-first-line", SK + "resume/SKILL.md", "---\nname: resume\n", "\n---\nname: resume\n", T + " -k valid_frontmatter"),
    ("skill-pointer", SK + "housekeeping/SKILL.md", "§ Housekeeping\n", "§ House keeping\n", T + " -k points_at_runbook"),
    ("heading-renamed", "src/context_engine/kit/docs/runbooks/procedures.md", "## Pause (§6.4)\n", "## Pausing (§6.4)\n", T + " -k points_at_runbook"),
    ("skill-missing", SK + "push-and-ci/SKILL.md", "Runbook: `docs/runbooks/procedures.md` § Push and CI\n", "Runbook: `kit/README.md` § Hook\n", T + " -k but_session_start"),
    ("skill-copies", SK + "clean-close/SKILL.md", "What sessions miss here, word for word", "| 1 | Lint | x |\n\nWhat sessions miss here, word for word", T + " -k copy_no_runbook_rows"),
    # the quotes (2026-10-15a): a skill line drifts from its section, or the section from the skill
    ("quote-skill-drift", SK + "pause/SKILL.md", "every uncommitted path and the deferred steps;", "every uncommitted path and its deferred steps;", T + " -k word_for_word"),
    ("quote-row-drift", "src/context_engine/kit/docs/runbooks/procedures.md", "It only watches: no fix, no re-run, no cancel, no push", "It only watches: no fix, no re-run, no push", T + " -k word_for_word"),
    ("quote-order", SK + "intake/SKILL.md", "- Record the words **verbatim, now** ... Write the words", "- Write the words ... Record the words **verbatim, now** ... Write the words", T + " -k word_for_word"),
    ("quote-other-list", SK + "resume/SKILL.md", "- the record, not memory,", "* the record, not memory,", T + " -k word_for_word"),
    ("quote-no-list", SK + "reconcile-foreign-commits/SKILL.md", "\n- Humans are never required to follow the procedures: the next agent session absorbs the cost.\n- with the author as its actor (`human:<id>`)\n- A human", "\nHumans are never required to follow the procedures: the next agent session absorbs the cost.\nwith the author as its actor (`human:<id>`)\nA human", T + " -k word_for_word"),
    # init beside the plugin
    ("init-skip", "src/context_engine/bootstrap.py", '    elif settings == "skip":  # no hook from init', '    elif False:  # no hook from init', T + " -k skip_settings_writes_no_hook"),
]
ok = True
for name, f, old, new, sel in S:
    if sys.argv[1:] and name not in sys.argv[1:]:  # named rows only
        continue
    p = pathlib.Path(f)
    orig = p.read_bytes()
    text = orig.decode("utf-8")
    crlf = "\r\n" in text
    norm = text.replace("\r\n", "\n")
    assert norm.count(old) == 1, (name, f, old[:60])
    try:
        bad = norm.replace(old, new)
        p.write_bytes((bad.replace("\n", "\r\n") if crlf else bad).encode("utf-8"))
        path, *k = sel.split(" -k ")
        args = [PY_EXE, "-m", "pytest", "-q", "-p", "no:cacheprovider", path] + (["-k", k[0]] if k else [])
        with tempfile.TemporaryDirectory() as cache:
            r = subprocess.run(args, capture_output=True, text=True, timeout=600, env={**os.environ, "PYTHONPYCACHEPREFIX": cache})
        last = [l for l in r.stdout.splitlines() if "passed" in l or "failed" in l or "error" in l][-1:]
        red = r.returncode != 0
        ok &= red
        print(f"{name:16} {'RED ' if red else 'GREEN!'} {old.strip().splitlines()[0][:50]!r:55} -> {last}", flush=True)
    finally:
        p.write_bytes(orig)
print("ALL RED" if ok else "SOME SABOTAGE STAYED GREEN")
sys.exit(0 if ok else 1)
