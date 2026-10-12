"""CE-15 sabotage table (sabotage rule, CLAUDE.md): break what each adoption-kit test guards; every
run must go red.

Run from the repo root: `<interpreter> tools/sabotage_ce15.py`. It restores every file it touches,
byte for byte. The patterns are exact source text from 2026-10-12b; when the text moves, a pattern
stops matching and the script stops with an AssertionError naming it, rather than passing quietly.
Each run gets a fresh bytecode cache (PYTHONPYCACHEPREFIX), so a same-length sabotage never runs a
stale .pyc. G-T5 (mutation per criterion, CE-14) replaces this hand table.
"""
import os, pathlib, subprocess, sys, tempfile

PY_EXE = sys.executable
BS = "src/context_engine/bootstrap.py"
KIT = "src/context_engine/kit/"
FW = "docs/framework/FRAMEWORK.md"
T = "tests/test_kit.py"
CF = "src/context_engine/config.py"
WK = "src/context_engine/working.py"
LG = "src/context_engine/ledger.py"
S = [
    ("no-overwrite", BS, "        if (root / dst).exists():\n            skipped.append(dst)", "        if False:\n            skipped.append(dst)", T + " -k never_overwrites"),
    ("no-overwrite", BS, "        if BEGIN in old:", "        if False:", T + " -k never_overwrites"),
    ("crlf-kept", BS, 'add.replace("\\n", "\\r\\n") if "\\r\\n" in old else add', "add", T + " -k never_overwrites"),
    ("dry-run", BS, "    if not dry_run:\n        for rel", "    if True:\n        for rel", T + " -k dry_run"),
    ("config-differs", BS, "        if target.read_text(encoding=\"utf-8\").replace(\"\\r\\n\", \"\\n\") != cfg:", "        if False:", T + " -k different_context"),
    ("prefix-own-kind", BS, "text, n = section.subn(lambda m: f'{m.group(1)}\"{prefix}\"', text, count=1)", "text, n = re.subn(r'^prefix = \"[^\"]*\"', f'prefix = \"{prefix}\"', text, count=1, flags=re.MULTILINE)", T + " -k prefix_override"),
    ("schema", KIT + "context.toml.template", "lock_timeout = 30.0 ", "# lock_timeout = 30.0 ", T + " -k names_every_key"),
    ("schema", KIT + "context.toml.template", "extra_dirs = []\n", "", T + " -k names_every_key"),
    ("provenance", KIT + "context.toml.template", "NEXT = 5                     # provenance: JUDGEMENT, engine default; wrong if", "NEXT = 5                     # engine default; if", T + " -k names_every_key"),
    ("ledger-skeleton", KIT + "docs/ledger/session-log.md", "---\n", "--\n", T + " -k empty_ledger"),
    ("drift-6.6", KIT + "contract.md", "it keeps the session's own context and tokens down", "it keeps the session's context and tokens down", T + " -k verbatim"),
    ("drift-6.6", KIT + "contract.md", "- that task agent pushes the work down again", "- that agent pushes the work down again", T + " -k verbatim"),
    ("drift-6.6", KIT + "contract.md", "  Never fan out with fable: it wastes tokens.", "  Avoid fanning out with fable.", T + " -k verbatim"),
    ("pin", KIT + "contract.md", "framework: 0.5\n", "framework: draft\n", T + " -k marked_and_pins"),
    ("leak-kit", KIT + "contract.md", "- Never reuse or renumber an id.", "- Never reuse or renumber an id (DEC-7).", T + " -k carry_none"),
    ("leak-kit", KIT + "README.md", "repo, at the pinned ref; copy it", "repo (spike/FINDINGS.md), at the pinned ref; copy it", T + " -k carry_none"),
    ("leak-fw", FW, "fallback is a runbook section (P16). Not built yet (CE-18).", "fallback is a runbook section (P16). Board task: CE-18.", T + " -k carry_none"),
    ("leak-fw", FW, "  `context.toml`, with the defaults in §10); or", "  `context.toml`; this repo uses `US`, `DEC`, `AC-21`); or", T + " -k carry_none"),
    # the CLI/MCP wiring, the config refusal and the first banner
    ("cli-no-config", "src/context_engine/cli.py", "return o.fn(o.target(args.root), ", "return o.fn(ops.Engine(args.root), ", T + " -k bootstraps_with_init"),
    ("mcp-no-config", "src/context_engine/mcp.py", "            e = o.target(root)  #", "            e = ops.Engine(root)  #", T + " -k mcp_init"),
    ("cli-op", "src/context_engine/cli.py", '    ("init", None): "init",\n', "", "tests/test_mcp.py -k every_cli_subcommand"),
    ("runbook", "docs/runbooks/manual-mode.md", "### context-engine init\n", "### init by hand\n", "tests/test_runbook.py"),
    ("cfg-engine", CF, '    _known("[engine]", engine, ENGINE_KEYS)\n', "", T + " -k unknown_key"),
    ("cfg-working", CF, '    _known("[working]", w, Working.__dataclass_fields__)\n', "", T + " -k unknown_key"),
    ("cfg-kinds", CF, '        _known(f"[kinds.{name}]", k, KIND_KEYS)\n', "", T + " -k unknown_key"),
    ("cfg-over-refuse", CF, '    _known("[working]", w, Working.__dataclass_fields__)', '    _known("[working]", w, ("ledger",))', T + " -k own_config_still_loads"),
    ("banner-none-read", WK, "return L.find_banner(path.read_bytes()", "return L.read_banner(path.read_bytes()", T + " -k bootstraps_with_init"),
    ("banner-seen-none", WK, "if (now.sha if now else L.NO_BANNER) != seen_hash:", "if now and now.sha != seen_hash:", T + " -k first_banner"),
    ("banner-place", LG, "start = end = first.start() if first else len(norm)", "start = end = 0 if first else len(norm)", T + " -k first_banner"),
    ("banner-show", "src/context_engine/ops.py", 'return 0, f"banner none hash {L.NO_BANNER}', 'return 0, f"no banner ({L.NO_BANNER})', T + " -k first_banner"),
]
ok = True
for name, f, old, new, sel in S:
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
            r = subprocess.run(args, capture_output=True, text=True, timeout=300, env={**os.environ, "PYTHONPYCACHEPREFIX": cache})
        last = [l for l in r.stdout.splitlines() if "passed" in l or "failed" in l or "error" in l][-1:]
        red = r.returncode != 0
        ok &= red
        print(f"{name:16} {'RED ' if red else 'GREEN!'} {old.strip().splitlines()[0][:50]!r:55} -> {last}")
    finally:
        p.write_bytes(orig)
print("ALL RED" if ok else "SOME SABOTAGE STAYED GREEN")
sys.exit(0 if ok else 1)
