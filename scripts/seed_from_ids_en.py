#!/usr/bin/env python3
"""Build a paper seed JSON from a compact pick list after filling arXiv metadata.

  python3 -I scripts/seed_from_ids_en.py NN

Reads scripts/seeds/papers/NN_picks_cn.json (list of dicts with at least `arxiv`
plus subtopic/type/reason[/classic_reason/reserve/level/difficulty]) and writes
scripts/seeds/papers/{NN}_{slug}_seed_cn.json with title/authors/date/summary
taken from arXiv v1 metadata.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_en import CATS, SEEDS, save
from papers_en import get_meta, entry_meta


def main(cat):
    slug = CATS[cat][0]
    picks = Path(SEEDS / "papers" / f"{cat}_picks_cn.json")
    import json
    items = json.loads(picks.read_text())
    get_meta([s["arxiv"] for s in items if s.get("arxiv")])
    out = []
    for s in items:
        rec = dict(s)
        if rec.get("arxiv"):
            m = entry_meta(rec)
            if not m:
                print("NO-META", rec["arxiv"], file=sys.stderr)
                continue
            rec.setdefault("summary", (m.get("abstract") or "")[:400])
            rec.setdefault("summary_basis", "arXiv 摘要（检索日）")
            rec.setdefault("level", "硕士/博士")
            rec.setdefault("difficulty", "中级")
        out.append(rec)
        print(rec.get("arxiv") or rec.get("title", "")[:50], rec.get("subtopic"), (m.get("date") if rec.get("arxiv") else ""))
    dest = SEEDS / "papers" / f"{cat}_{slug}_seed_cn.json"
    save(dest, out)
    print("wrote", dest, "n=", len(out))


if __name__ == "__main__":
    main(sys.argv[1])
