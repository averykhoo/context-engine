"""OKF read and write: byte-identical round trips, unknown keys kept, line-ending-blind hashes."""

from pathlib import Path

import pytest

from context_engine import okf
from context_engine.errors import Refusal

REPO = Path(__file__).resolve().parents[1]
RECORDS = sorted(
    [*REPO.glob("docs/decisions/*.md"), *REPO.glob("docs/stories/*.md"), *REPO.glob("tasks/*.md"), REPO / "docs/charter.md"]
)

HAND_WRITTEN = (
    "---\n"
    "type: Decision\n"
    "id: DEC-3\n"
    "title: \"Quoted: with a colon\"\n"
    "charter_status: unconfirmed   # owner review pending: ASK-1\n"
    "# a full-line comment between keys\n"
    "generated: { by: claude-code/x, at: 2026-10-08T15:00:00+08:00 }\n"
    "x_unknown: { kept: [a, b] }\n"
    "tags: [storage]\n"
    "closed:\n"
    "---\n"
    "\n"
    "Body text.\n"
)


@pytest.mark.criterion("AC-1")
@pytest.mark.parametrize("path", RECORDS, ids=lambda p: p.name)
def test_every_record_in_this_repo_round_trips_byte_identical(path):
    raw = path.read_bytes().decode("utf-8")
    assert okf.parse(raw).render() == raw


@pytest.mark.criterion("AC-1")
@pytest.mark.parametrize("newline", ["\n", "\r\n"], ids=["LF", "CRLF"])
def test_setting_one_key_leaves_every_other_byte_alone(newline):
    raw = HAND_WRITTEN.replace("\n", newline)
    doc = okf.parse(raw)
    doc.set("tags", ["storage", "lock"])
    out = doc.render()
    before, after = raw.split(newline), out.split(newline)
    changed = [(a, b) for a, b in zip(before, after) if a != b]
    assert changed == [("tags: [storage]", "tags: [storage, lock]")]
    assert len(before) == len(after)


@pytest.mark.criterion("AC-1")
def test_an_end_of_line_comment_survives_a_change_to_its_key():
    doc = okf.parse(HAND_WRITTEN)
    doc.set("charter_status", "confirmed")
    assert "charter_status: confirmed   # owner review pending: ASK-1\n" in doc.render()


@pytest.mark.criterion("AC-2")
def test_unknown_keys_survive_writes_to_other_keys_and_new_keys():
    doc = okf.parse(HAND_WRITTEN)
    doc.set("title", "Changed")
    doc.set("added", "new")
    doc.delete("closed")
    out = okf.parse(doc.render())
    assert out.get("x_unknown") == {"kept": ["a", "b"]}
    assert "x_unknown: { kept: [a, b] }\n" in doc.render()
    assert list(out.data) == ["type", "id", "title", "charter_status", "generated", "x_unknown", "tags", "added"]


def test_a_value_with_a_colon_is_quoted_and_reads_back():
    doc = okf.parse(HAND_WRITTEN)
    doc.set("title", "Engine core: OKF records, ids: under a lock")
    assert okf.parse(doc.render()).get("title") == "Engine core: OKF records, ids: under a lock"


def test_invalid_yaml_is_refused_with_a_remedy():
    with pytest.raises(Refusal) as e:
        okf.parse("---\ntitle: First trial repo: adhoc\n---\n")
    assert "quote" in e.value.remedy


@pytest.mark.criterion("AC-7")
def test_body_hash_is_the_same_for_lf_and_crlf_checkouts():
    lf = okf.parse(HAND_WRITTEN)
    crlf = okf.parse(HAND_WRITTEN.replace("\n", "\r\n"))
    assert crlf.newline == "\r\n"
    assert okf.body_sha(lf.body) == okf.body_sha(crlf.body)
    # the hash normalises on its own, not only because parse() did it first
    assert okf.body_sha("\r\nOwner words.\r\nSecond line.\r\n") == okf.body_sha("\nOwner words.\nSecond line.\n")


@pytest.mark.criterion("AC-7")
def test_body_hash_sees_a_real_change_and_ignores_amendments():
    base = "\nOriginal words.\n"
    assert okf.body_sha(base) != okf.body_sha("\nOriginal word.\n")
    assert okf.body_sha(base) == okf.body_sha(base + "\n## Amendments\n\n- later note\n")
