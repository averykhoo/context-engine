---
type: Decision
id: DEC-298
title: gate run with parts runs every part and continues past a failure, one row per part appended as each ends; --part NAME and --stale select parts; --stale or --part without parts is refused; new status key <scope>+parts = covered and every part fresh
actor: claude-code/claude-opus-5-5
decided: 2026-11-08
session: 2026-11-07e
decision_status: PROVISIONAL
body_sha: sha256:33e426154c604d558d0707cc7365e8b879ad63490ca180f08504c1646f30de96
---

With parts declared, `context-engine gate run` runs every part in declared order and continues
past a failure, appending one row per part as that part ends, so an interrupted run keeps what
finished; it prints a line per part and a summary, and exits 0 only when every part passed. A
long gate wants every verdict from one pass, and `--stale` then re-runs only the failures.
`--part NAME` (repeatable) runs the named parts; `--stale` runs only the parts that are not fresh
or do not cover the require scope, and with none stale writes no row. Both are refused without
parts; `--readers` is refused with parts, and `--part` with `--stale`. A new `gate status
--require <scope>+parts` key means the scope is covered and every part is fresh: what the close's
step 7 and the pre-push check use. No per-part timeout and no built-in parallelism: parts run as
separate CLI calls where a tool call cannot hold the whole gate. Single-command configs keep
their behaviour and reply strings byte-identical.
