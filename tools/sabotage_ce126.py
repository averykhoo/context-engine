"""CE-126 sabotage table (DEC-11, 2026-11-08, session 2026-11-07e): break what each test of
tests/test_lanes.py guards (AC-197, the lanes of DEC-84); every run must go red, and the line it
prints says why.

Run from the repo root: `<interpreter> tools/sabotage_ce126.py`. It restores every file it
touches, byte for byte. The patterns are exact source lines from 2026-11-08; when the code moves,
a pattern stops matching and the script stops with an AssertionError naming it, rather than
passing quietly. Each run gets a fresh bytecode cache (PYTHONPYCACHEPREFIX), as in sabotage_ce2.py.
"""
import os, pathlib, re, subprocess, sys, tempfile

PY_EXE = sys.executable
CM = "src/context_engine/commit.py"
ST = "src/context_engine/store.py"
OP = "src/context_engine/ops.py"
W = "src/context_engine/working.py"
MCP = "src/context_engine/mcp.py"
CLI = "src/context_engine/cli.py"
GD = "src/context_engine/guards.py"
T = "tests/test_lanes.py"
S = [
    # select: a commit takes its own session's lines of its own lane
    ("AC-197", CM, '            return o.get("session") == session and lane_ok(_lane(o))', '            return o.get("session") == session', T + " -k select_takes_by_session_and_lane"),
    ("AC-197", CM, '            return o.get("session") == session and lane_ok(_lane(o))', '            return o.get("session") == session', T + " -k leaves_the_coordinators_lines_out"),
    # an unparseable line's lane is read from its text
    ("CE-126", CM, "        m = LANE_FIELD.search(line)\n        return m.group(1) if m else None", "        return None", T + " -k unparseable_line_stays_with_its_lane"),
    # the op line carries `lane` right after `session`
    ("AC-197", ST, '            **({"lane": self.lane} if self.lane else {}),\n', "", T + " -k right_after_session"),
    ("AC-197", ST, '            "session": session,\n            **({"lane": self.lane} if self.lane else {}),\n            "actor": actor,\n',
     '            "session": session,\n            "actor": actor,\n            **({"lane": self.lane} if self.lane else {}),\n', T + " -k right_after_session"),
    # a coordinator's milestone takes only lines with no lane
    ("AC-197", ST, "lane=commit_mod.EVERY_LANE if every else self.lane)", "lane=commit_mod.EVERY_LANE)", T + " -k milestone_leaves_a_lanes_lines_out"),
    # the session's close, pause and pause record take every lane
    ("AC-197", W, "        self.store.commit_every_lane = True\n        self._check(key, actor)\n        summary", "        self._check(key, actor)\n        summary", T + "::test_the_session_close_and_pause_take_every_lane[close]"),
    ("AC-197", W, "        self.store.commit_every_lane = True\n        self._check(key, actor)\n        if not rows.strip() or not deferred", "        self._check(key, actor)\n        if not rows.strip() or not deferred", T + "::test_the_session_close_and_pause_take_every_lane[pause]"),
    ("AC-197", W, "carried = C.pending(self.root, self.store.config.oplog, session, lane=C.EVERY_LANE)", "carried = C.pending(self.root, self.store.config.oplog, session)", T + " -k pause_record_takes_every_lane"),
    ("AC-197", W, "            self.store.commit_every_lane = True\n        return f\"{rec.id}: pause recorded", "        return f\"{rec.id}: pause recorded", T + " -k pause_record_takes_every_lane"),
    # the coordinator's own ops refuse a lane; a lane is checked before anything is written
    ("AC-197", OP, "        if c.lane and self.name in COORDINATOR_ONLY:", "        if False:", T + " -k coordinators_own_ops_refuse_a_lane"),
    ("AC-197", OP, "        c.lane = check_lane(c.lane)\n", "", T + " -k checked_before_anything_is_written"),
    ("AC-197", ST, "    if not LANE_RE.fullmatch(v):", "    if not LANE_RE.match(v.split()[0]):", T + " -k checked_before_anything_is_written"),
    # the CLI and the MCP tools carry it; the MCP never remembers it
    ("CE-126", CLI, "ops.Caller(args.session, args.actor, args.agent)", "ops.Caller(args.session, args.actor)", T + " -k cli_carries_the_lane"),
    ("CE-126", MCP, ', kw.pop("agent", None))', ')\n        kw.pop("agent", None)', T + " -k mcp_tools_take_agent"),
    ("CE-126", MCP, ', kw.pop("agent", None))', ', kw.pop("agent", None) or os.environ.get("CE_AGENT"))', T + " -k mcp_tools_take_agent"),
    ("CE-126", MCP, "        if o.name not in ops.COORDINATOR_ONLY:  # a subagent's lane, per call (CE-126)\n", "        if True:\n", T + " -k mcp_tools_take_agent"),
    # G-W7 reds a malformed lane
    ("CE-126", GD, "    if lanes:\n", "    if False:\n", T + " -k g_w7_reds_a_malformed_lane"),
    # the replies and messages name a lane
    ("CE-126", CM, "    if not _any_lane(left):\n", "    if True:\n", T + " -k left_behind_names_a_lane"),
    ("CE-126", CM, '    return tuple(sorted({label(o.get("session"), _lane(o)) for o in lines if not _own(o, session, lane)}))',
     '    return tuple(sorted({str(o.get("session")) for o in lines if o.get("session") != session}))', T + " -k left_behind_names_a_lane"),
]
REASON = re.compile(r"^E\s+(.*)$", re.MULTILINE)
ok = True
for ac, f, old, new, sel in S:
    p = pathlib.Path(f)
    raw = p.read_bytes()  # restored byte for byte, whatever its line endings
    orig = raw.decode("utf-8").replace("\r\n", "\n")
    assert orig.count(old) == 1, (ac, f, old[:60])
    try:
        p.write_bytes(orig.replace(old, new).encode("utf-8"))
        path, *k = sel.split(" -k ")
        args = [PY_EXE, "-m", "pytest", "-q", "-p", "no:cacheprovider", path] + (["-k", k[0]] if k else [])
        with tempfile.TemporaryDirectory() as cache:
            r = subprocess.run(args, capture_output=True, text=True, timeout=300, env={**os.environ, "PYTHONPYCACHEPREFIX": cache})
        last = [l for l in r.stdout.splitlines() if "passed" in l or "failed" in l or "error" in l][-1:]
        why = (REASON.findall(r.stdout) or ["(no E line)"])[0][:150]
        ran = any("failed" in l for l in last)
        red = r.returncode != 0 and ran
        ok &= red
        print(f"{ac:6} {'RED ' if red else 'GREEN!'} {f.split('/')[-1]}: {old.strip().splitlines()[0][:50]!r} -> {last}\n         because: {why}")
    finally:
        p.write_bytes(raw)
print("ALL RED" if ok else "SOME SABOTAGE STAYED GREEN")
