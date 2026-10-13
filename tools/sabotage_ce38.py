"""CE-38 sabotage table (sabotage rule, CLAUDE.md): break what each bootloader test guards; every
run must go red.

Run from the repo root: `<interpreter> tools/sabotage_ce38.py`. It restores every file it touches,
byte for byte. The patterns are exact source text from 2026-10-13b; when the text moves, a pattern
stops matching and the script stops with an AssertionError naming it, rather than passing quietly.
Each run gets a fresh bytecode cache (PYTHONPYCACHEPREFIX), so a same-length sabotage never runs a
stale .pyc. G-T5 (mutation per criterion, CE-34) replaces this hand table.
"""
import os, pathlib, subprocess, sys, tempfile

PY_EXE = sys.executable
BS = "src/context_engine/bootstrap.py"
WK = "src/context_engine/working.py"
KIT = "src/context_engine/kit/"
TK = "tests/test_kit.py"
TW = "tests/test_working.py"
G_D0 = TW + " -k bootloader or import or inline_block or hand_edited or not_the_engines"
S = [
    # init (AC-57)
    ("boot-not-appended", BS, "    block = (KIT / BOOTLOADER).read_text(encoding=\"utf-8\")\n", "    block = (KIT / CONTRACT).read_text(encoding=\"utf-8\")\n", TK + " -k writes_the_bootloader"),
    ("contract-unwritten", BS, "        writes[CONTRACT_DEST] = (KIT / CONTRACT).read_text(encoding=\"utf-8\")\n", "        pass\n", TK + " -k writes_the_bootloader"),
    ("settings-clobber", BS, "    if (root / SETTINGS).exists():", "    if False:", TK + " -k existing_local_settings"),
    ("no-ignore", BS, "            writes[SETTINGS_IGNORE] = \"settings.local.json\\n\"\n", "            pass\n", TK + " -k writes_the_bootloader"),
    ("ignore-always", BS, "    if (root / SETTINGS).exists():  # it may hold", "    writes[SETTINGS_IGNORE] = \"settings.local.json\\n\"\n    if (root / SETTINGS).exists():  # it may hold", TK + " -k existing_local_settings"),
    ("ignore-unchecked", BS, "        elif \"settings.local.json\" not in ignore.read_bytes()", "        elif False and \"settings.local.json\" not in ignore.read_bytes()", TK + " -k rerun_finds_its_own_hook"),
    ("rerun-asks-again", BS, "        skipped.append(SETTINGS if has_hook(root / SETTINGS) else", "        skipped.append(SETTINGS if False else", TK + " -k rerun_finds_its_own_hook"),
    ("hook-any-command", BS, "    return any(\"-m context_engine\" in c and", "    return any(True or \"-m context_engine\" in c and", TK + " -k rerun_finds_its_own_hook"),
    ("hook-relative", BS, "--root \"{Path(root).resolve().as_posix()}\" orient'", "--root . orient'", TK + " -k runs_orient_through_a_shell"),
    ("hook-matcher", BS, "[{\"hooks\": [{\"type\": \"command\"", "[{\"matcher\": \"startup\", \"hooks\": [{\"type\": \"command\"", TK + " -k writes_the_bootloader"),
    ("inline-kept", BS, "            if found and found[1] is not None and IMPORT_RE.search(found[1]):\n", "            if True:\n", TK + " -k inline_kit_block"),
    ("boot-redone", BS, "            if found and found[1] is not None and IMPORT_RE.search(found[1]):\n", "            if False:\n", TK + " -k inline_kit_block"),
    # G-D0's bootloader half (AC-58)
    ("no-boot-check", WK, "        if block and block[0] == want:  # a block of another version is red above\n", "        if False:\n", G_D0),
    ("no-end-ok", WK, "        if body is None:\n            return [Failure(", "        if body is None:\n            return []\n            return [Failure(", TW + " -k hand_edited"),
    ("text-unchecked", WK, "        if body != K.bootloader_body():\n", "        if False:\n", TW + " -k inline_block or hand_edited"),
    ("root-relative", WK, "            p = path.parent / target  # Claude Code", "            p = self.root / target  # Claude Code", TW + " -k resolves_against"),
    ("missing-ok", WK, "            if not p.is_file():\n                fix = ", "            if False:\n                fix = ", TW + " -k missing_import_target"),
    ("mapped-remedy", WK, " if shown == K.CONTRACT_DEST else fix))", "))", TW + " -k resolves_against"),
    ("compare-off", WK, "            if have != want_text:\n", "            if False:\n", TW + " -k not_the_engines"),
    ("crlf-strict", WK, "                have = p.read_bytes().decode(\"utf-8-sig\").replace(\"\\r\\n\", \"\\n\")\n", "                have = p.read_bytes().decode(\"utf-8-sig\")\n", TW + " -k bootloader_importing"),
    ("utf8-crash", WK, "        except UnicodeDecodeError as e:\n            return [Failure(", "        except KeyError as e:\n            return [Failure(", TW + " -k not_utf8"),
    ("utf8-import-crash", WK, "            except UnicodeDecodeError:\n                have = None", "            except KeyError:\n                have = None", TW + " -k not_utf8"),
    # orient (AC-59)
    ("orient-last", WK, "            sections.insert(0, (\"Contract: fix this first\"", "            sections.append((\"Contract: fix this first\"", TW + " -k orient_leads"),
    ("orient-off-ignored", WK, "        if \"G-D0\" not in self.store.config.guards.off and (bad := self.lint_contract()):\n", "        if (bad := self.lint_contract()):\n", TW + " -k orient_leads"),
    # the kit texts (AC-33, AC-57)
    ("import-path", KIT + "bootloader.md", "@docs/framework/contract.md\n", "@docs/contract.md\n", TK + " -k imports_the_contract"),
    ("gate-inside", KIT + "bootloader.md", "<!-- context-engine kit 0.5 end -->\n\n## Gate\n\n`<this repo's own test command> && context-engine lint`, from the repo root.\n", "\n## Gate\n\n`<this repo's own test command> && context-engine lint`, from the repo root.\n<!-- context-engine kit 0.5 end -->\n", TK + " -k imports_the_contract"),
    ("key-kept", KIT + "contract.md", "keep it, do not run `session start` again", "run `session start` again", TK + " -k starts_a_session_alone"),
    ("claude-wins", KIT + "contract.md", "`CLAUDE.md` wins", "this file wins", TK + " -k starts_a_session_alone"),
    ("fallback-gone", KIT + "contract.md", "**a failing hook is silent**", "**the hook always runs**", TK + " -k starts_a_session_alone"),
    ("readme-hook", KIT + "README.md", "## Hook\n", "## The hook\n", TK + " -k existing_local_settings"),
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
        print(f"{name:18} {'RED ' if red else 'GREEN!'} {old.strip().splitlines()[0][:50]!r:55} -> {last}")
    finally:
        p.write_bytes(orig)
print("ALL RED" if ok else "SOME SABOTAGE STAYED GREEN")
sys.exit(0 if ok else 1)
