"""The release notes' upgrade stamps (CE-240, FRAMEWORK §6.12, §8.0): each upgrade step opens
``**Upgrade (at <sha>):**``, naming the engine commit it is needed from, and the kit README's
"Steps by pin" lists every one with that commit's date, so a repo moving its pin selects its steps
by ancestry, not by a section's date (the F33 failure: a step missed because it sat in an older
section)."""

import re
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
NOTES = REPO / "docs" / "framework" / "RELEASE-NOTES.md"
README = REPO / "src" / "context_engine" / "kit" / "README.md"
STAMP = re.compile(r"\*\*Upgrade \(at ([0-9a-f]{7,40})\):\*\*")
FORM = "**Upgrade (at <sha>):**"
CODE_SPAN = re.compile(r"`[^`]+`")  # a span may wrap a line, so it takes newlines
HEX_REF = re.compile(r"`([0-9a-f]{7,40})`")
DATED_REF = re.compile(r"`([0-9a-f]{7,40})` \((\d{4}-\d{2}-\d{2})[,)]")


def bullets() -> list[str]:
    """Each top-level ``- `` bullet of the notes, its continuation lines included."""
    return [b for b in re.split(r"\n(?=- |## )", NOTES.read_text(encoding="utf-8")) if b.startswith("- ")]


def readme_section_4() -> str:
    text = README.read_text(encoding="utf-8")
    return text[text.index("## 4. Upgrade") : text.index("## 5.")]


def git(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(REPO), *args], capture_output=True, text=True, encoding="utf-8")


def test_every_upgrade_step_is_stamped_and_listed_by_pin():
    """CE-240: the header states the stamp form; every upgrade step outside a code span is a full
    stamp, one to a bullet; and every stamp is a backticked ref in kit README § 4 (Steps by pin)."""
    text = NOTES.read_text(encoding="utf-8")
    header = text[: text.index("\n## ")]
    assert FORM in header, f"the notes' header does not state the stamp form {FORM}"
    prose = CODE_SPAN.sub("", text)  # the header and a bullet may quote the form
    opened = re.findall(r"\*\*Upgrade\b", prose)
    stamps = STAMP.findall(prose)
    assert stamps and len(opened) == len(stamps), f"{len(opened) - len(stamps)} upgrade step(s) lack the stamp form {FORM}"
    for b in bullets():
        assert len(STAMP.findall(CODE_SPAN.sub("", b))) <= 1, f"two stamps in one bullet: {b[:80]!r}"
    listed = set(HEX_REF.findall(readme_section_4()))
    assert [s for s in stamps if s not in listed] == [], "a stamp the kit README § 4 (Steps by pin) does not list"


def test_every_upgrade_stamp_names_a_commit_of_its_own_task():
    """CE-240: a stamp resolves to an engine commit that is in this history and whose subject leads
    with a task id its bullet cites; each ref in kit README § 4 resolves too, with the date it prints.
    Reads git history, so it is a declared reader in context.toml (no scope id hashes history)."""
    for b in bullets():
        for sha in STAMP.findall(CODE_SPAN.sub("", b)):
            assert git("rev-parse", "--verify", "--quiet", f"{sha}^{{commit}}").returncode == 0, f"{sha} is no commit of this repo"
            assert git("merge-base", "--is-ancestor", sha, "HEAD").returncode == 0, f"{sha} is not in this history"
            subject = git("show", "-s", "--format=%s", sha).stdout.strip()
            lead = re.match(r"(CE-\d+):", subject)
            assert lead and lead[1] in b, f"stamp {sha} ({subject[:60]!r}) leads with no task id its bullet cites"
    section = readme_section_4()
    assert sorted(HEX_REF.findall(section)) == sorted(r for r, _ in DATED_REF.findall(section)), "a ref in kit README § 4 prints no date as `<sha>` (<date>"
    for sha, date in DATED_REF.findall(section):
        assert git("merge-base", "--is-ancestor", sha, "HEAD").returncode == 0, f"{sha} is not in this history"
        assert git("show", "-s", "--format=%ad", "--date=short", sha).stdout.strip() == date, f"{sha} is not from {date}"
