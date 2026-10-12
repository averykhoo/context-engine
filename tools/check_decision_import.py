"""Independent check of a trial import: every non-blank line of the source log's entries and
rejected table is in some imported record, and every record's text is a verbatim slice of the
source. It does not use the importer's parser.

Usage: <interpreter> tools/check_decision_import.py <trial repo> <source log copy>. Written for
adhoc's log (`D-n` ids, a `## Entries` heading); its output is in
docs/evidence/decision-import-trial-2026-10-12.md."""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from context_engine import okf  # noqa: E402

root, src = Path(sys.argv[1]), Path(sys.argv[2])
text = src.read_text(encoding="utf-8").replace("\r\n", "\n")
recs = {}
for p in sorted((root / "docs/decisions").glob("D-*.md")):
    doc = okf.parse(p.read_text(encoding="utf-8"))
    recs[doc.get("id")] = doc
print("records:", len(recs))

# 1. every record's original text is a verbatim slice of the source (rejected rows: their row line)
missing = []
for rid, doc in recs.items():
    canon = okf.canonical(doc.body).strip("\n")
    if doc.get("decision_status") == "REJECTED":
        canon = canon.splitlines()[-1]
    if canon not in text:
        missing.append(rid)
print("records whose text is not a verbatim slice of the source:", missing or "none")

# 2. every non-blank, non-heading line from `## Entries` on, and every table row, is in a record
bodies = "\n".join(okf.canonical(d.body) for d in recs.values())
entries = text[text.index("\n## Entries") :]
lines = [ln for ln in entries.splitlines() if ln.strip() and not ln.startswith(("### ", "## "))]
lost = [ln for ln in lines if ln not in bodies]
rows = [ln for ln in text[: text.index("\n## Entries")].splitlines() if ln.startswith("| ") and not ln.startswith("| thing")]
lost_rows = [ln for ln in rows if ln not in bodies]
print(f"entry lines checked: {len(lines)}, not in any record: {len(lost)}")
print(f"table rows checked: {len(rows)}, not in any record: {len(lost_rows)}")
for ln in (lost + lost_rows)[:10]:
    print("  LOST:", ln[:100])

# 3. every heading: id kept, title kept, trailing note kept as an amendment
heads = re.findall(r"^### (D-\d+) -- (.*)$", text, re.M)
bad = []
for rid, rest in heads:
    doc = recs.get(rid)
    if doc is None or not rest.startswith(str(doc.get("title"))):
        bad.append(rid)
        continue
    note = re.search(r"\)\* -- (.*)$", rest)
    if note and note.group(1) not in doc.body:
        bad.append(rid + " (note)")
print(f"headings checked: {len(heads)}, id/title/note not kept: {bad or 'none'}")
for rid in ("D-27", "D-29", "D-12", "D-30", "D-2", "D-26"):
    d = recs[rid]
    links = {k: d.get(k) for k in ("supersedes", "superseded_by", "relaxes", "narrowed_by") if d.get(k)}
    print(f"  {rid}: {d.get('decision_status')} {links}")
