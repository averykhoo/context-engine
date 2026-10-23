# How the record engine carries out the framework

LIVING. This is the engine's side of the rules in `docs/framework/FRAMEWORK.md`: how the engine
does what the framework requires, where that is more than the framework needs a user to know.
The rule itself is in FRAMEWORK (cited by section here); every step done by hand is
`docs/runbooks/manual-mode.md`; why a rule is as it is lives in its decision or task. Moved here
from FRAMEWORK.md when it was cut to what a user needs (CE-93, DEC-49); the text before that is
`docs/framework/FRAMEWORK-v0.5-2026-10-23.md`.

## Commits (FRAMEWORK §5.5 rule 4)

The code is `src/context_engine/commit.py`; `commit.py::commit` makes every commit, the engine's
own and the session's (`context-engine commit`).

**Why milestones, not every write** (DEC-36, CE-55): a commit per write grew history by a commit
per board edit and cost every write a git process under the engine lock, for writes that cost
little to lose. What a milestone commits is what is costly to lose or must be at HEAD now.

**Why the session's own lines, not every uncommitted line** (CE-125, which replaced CE-45's
sweep as the default): the commit is derived from the op log against HEAD, not from what this
process remembers, so every write of this session still uncommitted goes in. Taking every other
session's lines too, as CE-45 did, committed one live session's half-done work under another's
name, and put a dead session's lines into the next session's first commit unasked (the adhoc
trial's feedback). Which other lines still go in, and why:
- a line naming a file the commit carries: that file holds its write, and G-W7 fails at HEAD
  without the line. The decision index is generated from every decision, so carrying it
  carries every decision's line, or G-D6 fails;
- a line that does not parse: it names no session.

The message and reply name whose lines those were (`including op lines that <key> left
uncommitted`); lines left out are named in the reply (`left uncommitted: <n> op lines of
<key>`). `--sweep` takes every line, for a session the owner or housekeeping knows is dead.

**The partial op log** (`commit.py::_commit_partial`): when lines stay out, the op log at HEAD
is HEAD's own lines plus the lines taken, in working order. The commit builds it in a temporary
index (`GIT_INDEX_FILE`: HEAD's tree, the paths as they are in the tree, that op log as a blob),
runs `git commit` on that index, so hooks run, then sets the real index's entries for those paths
to what was committed, as `git commit --only` does. The working op log is never rewritten. The
order on disk and at HEAD can differ while lines stay out; once none does, a commit carries the
working file whole and the two converge. Before the first commit every line goes in: there is no
op log at HEAD to build on.

**By path, under the lock:** `git commit --only` on those paths leaves what another session
staged or left untracked exactly as it was, and a `git add` of a new file is taken back if the
commit fails. The lock is held from an operation's first write to its commit, so no other write
lands between them and the commit never reads a half-finished operation. A slow hook holds the
lock for as long as it runs, so another session's write can time out on the lock meanwhile; it
refuses before it writes anything.

**When it cannot commit**, the write stands and the reply says `not committed: <why>`, naming
the by-hand commit: a merge, rebase, cherry-pick, revert or bisect in progress; a detached HEAD;
`GIT_DIR`, `GIT_INDEX_FILE` or a similar variable set (inside a git hook, where a commit would go
to that repo or index; `commit.py::GIT_ENV` lists them); `context.toml` not tracked by the
enclosing repo (a target inside an unrelated repo, or a new repo before its kit is committed);
the op log gitignored, or missing lines HEAD has; a record it would carry whose frontmatter does
not parse (a hand edit in progress, which it would commit as it stands); a refusing hook; git
refusing the repo; a `.git` directory present but no git executable. Only a target in no git
work tree at all commits nothing and says nothing (the session's own `commit` refuses there). A
named file that git ignores is left out, and the reply names it.

**A refusal after a write:** a milestone that refuses after a write commits that write too,
since the op log at HEAD must not lag the files it names, and the refusal says what became of
it; a close's `Closes:` is added only once its write is made, so a refused close never claims the
item closed. A write that is not a milestone stays uncommitted until the next commit, refused or
not. An operation that fails with an error other than a refusal can leave a partial change,
which the next commit carries as it stands, named nowhere: lint then reports what is wrong with
it.

**Older config:** `[engine] commit = true` reads as `"milestones"` and `false` as `"off"` (CE-45's
spelling).

**`init`** writes the kit's files, not records: it logs nothing and commits nothing, and the
session commits what it wrote.

## Pre-write lint of the banner and the ledger entry (FRAMEWORK §5.5 rule 2)

`banner.set` runs lint's own G-D1, G-D5 and G-D8 functions on the note as it would be, and
refuses a failure the stored note does not already have, naming the guard's remedy; a session
close or pause checks its ledger entry the same way (CE-63).

## The engine lock (FRAMEWORK §5.5 rule 5)

One file lock per repo (`lock.py::FileLock`, at `[engine] lockfile`), not yet keyed on the tree
hash as rule 5 and G-V3 ask, and gate and background-agent runs take no lock yet (CE-135).
`[engine] lock_timeout` is how long the lock may stay with one holder before a
waiting write is refused, not how long a caller may wait: each holder writes a fresh token, and a
waiter that sees it change restarts its deadline (CE-87).

## Foreign-commit ranges (FRAMEWORK §6.10 item 2)

`ledger.py::foreign_commits` computes the list. A start head no longer in HEAD's history
(rebased away) is dropped, and a session whose own start head is dropped reconciles up to HEAD.
Two cases can then report a commit twice, though none is skipped: a session's own start head
rebased away (its range and the next one's overlap), and a merged side branch (a start head on
the branch is not on the first-parent line the next baseline is taken from); the `kind: foreign`
entry, once written, keeps a named commit out. Before any earlier entry records a start head,
the baseline is the newest commit touching the ledger that this session did not make; at that
switch-over a foreign commit can be skipped once, the bug the start heads remove (CE-65). A
session that records its start head and dies before reconciling leaves its range unreconciled.

## The MCP server (FRAMEWORK §8.0.2)

Each MCP tool and its CLI subcommand look the operation up in `ops.py::OPS` and call the same
function. Whether a `/clear` leaves the server process running is UNVERIFIED: it cannot be
tested headless (the spike findings record it), so a session begins with `session.start`, never
with the process.

## The run ledger's ids (FRAMEWORK §8.5 G-V1)

`gate.py::scope_id` hashes a scope over the tracked and untracked, not ignored, files its globs
match. A run records each id that did not move while it ran, and counts for nothing only when
every id moved, so a concurrent write voids only the ids it touched. The commit refusal checks the
scope, not its readers: their id moves on every engine write, any session's, and a commit of a
code path does not commit what they re-check. The ledger is gitignored, or it would sit inside
the id it records.
