#!/usr/bin/env bash
# Step-0 spike driver (Git Bash). Copies project/ to a temp dir and runs headless Claude Code
# against it: run A (positive), control B (CTX_PY unset), control C (SessionStart hook removed).
# Outputs land in $TEMP/ce-spike; transcribe them into runs/<date>/ and FINDINGS.md.
set -u
here=$(cd "$(dirname "$0")" && pwd)
T=$(cygpath -m "$TEMP")/ce-spike
rm -rf "$T"; mkdir -p "$T"; cp -r "$here/project/." "$T/"; cd "$T"
export CTX_PY=C:/Users/user/anaconda3/envs/context-engine/python.exe
export CTX_PROBE_SERVER=$(cygpath -m "$here/probe_server.py")

export CTX_PROBE_LOG="$T/calls.log"
claude -p 'Do exactly these three steps and then report. (1) Call the mcp__probe__ping tool with caller="main". (2) Use your subagent tool (Agent/Task) to launch one general-purpose subagent with the instruction: "Call the mcp__probe__ping tool with caller=\"subagent\" and return its exact output." (3) Look at your context: if it contains a line starting with PROBE-WORD, give that word; otherwise say PROBE-WORD NONE. Final answer: three lines, the main ping output, the subagent ping output, the probe word.' \
  --model haiku --allowedTools "mcp__probe__ping" "Agent" "Task" > run_A.out 2> run_A.err

export CTX_PROBE_LOG="$T/calls_B.log"
( unset CTX_PY; claude -p 'Call the mcp__probe__ping tool with caller="controlB". If the tool is not available or fails, say exactly TOOL-UNAVAILABLE and nothing else.' \
  --model haiku --allowedTools "mcp__probe__ping" > run_B.out 2> run_B.err )

cp .claude/settings.json settings_with_hook.json
printf '{ "enabledMcpjsonServers": ["probe"] }\n' > .claude/settings.json
claude -p 'If your context contains a line starting with PROBE-WORD, reply with that word only; otherwise reply exactly PROBE-WORD NONE.' \
  --model haiku > run_C.out 2> run_C.err
cp settings_with_hook.json .claude/settings.json
echo "outputs in $T"
