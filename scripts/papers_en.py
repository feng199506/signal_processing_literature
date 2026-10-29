"""Paper pipeline for the signal processing literature library (categories 01-12).

  python3 -I scripts/papers_en.py search NN [--per-query 60]   arXiv API search with the queries in
                                                  seeds/queries/NN_en.json -> cache/candidates/NN_en.json
  python3 -I scripts/papers_en.py meta ID [ID ...]   fetch arXiv metadata into cache/arxiv_meta/
  python3 -I scripts/papers_en.py show NN [--all] [--abs N]    compact candidate listing (window only
                                                  unless --all; N = abstract characters shown)
  python3 -I scripts/papers_en.py check NN        validate seeds/papers/NN_seed_cn.json (ids, dates,
                                                  duplicates across groups)
  python3 -I scripts/papers_en.py download NN [--target 12] [--retry-failed]
  python3 -I scripts/papers_en.py status [NN]
  python3 -I scripts/papers_en.py text KEY [--pages 2]
  python3 -I scripts/papers_en.py manual KEY --note '...'   promote a 'pending' item after a manual check
  python3 -I scripts/papers_en.py reject KEY --note '...'

Queries file: list of {"q": arXiv search_query (without date clause), "subtopic": "..."}; the date
window [2021-10-30, 2026-10-30] is appended unless "old": true.

Seed entry (seeds/papers/NN_seed_cn.json, list, reading order = list order):
  arxiv | (pdf_url + title + authors + date [+ date_basis, venue, doi, landing])
  subtopic, type (综述 / 学术教程 / 原始研究论文 / 基准与数据集 / 立场与方法论), level, difficulty,
  reason (选入理由), summary (简介), summary_basis, classic_reason (required if first public
  date < 2021-10-30), reserve (bool: only downloaded when the main list falls short).

Verification (all hard checks must pass to count): HTTP 200 (or a verified copy from a sibling
library), %PDF- header, pypdf parses, >= 4 pages, >= 12000 extracted characters, title words >= 0.8
matched in the first two pages, first-author surname found in the first two pages, a references
heading found. Failing only title/author -> 'pending' (manual check). Files are staged in a fresh
empty directory outside the library and moved into papers/NN_slug/ only after passing.
State: scripts/state/papers/NN_en.json (one writer per group).
"""
import csv
import hashlib
import re
import shutil
import sys
import tempfile
import urllib.parse
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_en import (CACHE, CATS, ROOT, SEEDS, STAGING, STATE, WORK, PYLIB, WINDOW_START, WINDOW_END,  # noqa: E402
                       cat_dir, cat_label, has_cjk, http, load, save, short_title, surname, title_in_text,
                       window_status)

sys.path.insert(0, str(PYLIB))
import logging  # noqa: E402
logging.getLogger("pypdf").setLevel(logging.ERROR)
from pypdf import PdfReader  # noqa: E402

META_DIR = CACHE / "arxiv_meta"
CAND_DIR = CACHE / "candidates"
TEXT = WORK / "text"
ATOM = "{http://www.w3.org/2005/Atom}"
ARX = "{http://arxiv.org/schemas/atom}"
API = "https://export.arxiv.org/api/query?"

SIBLINGS = [
    ("gaussian_process_literature", "编号", "标识符", "本地路径"),
    ("recent_top_conference_research", "编号", "标识符", "本地路径"),
    ("industrial_process_monitoring_literature", "文献编号", "arXiv ID", "本地相对路径"),
    ("probability_statistics_curriculum_literature", "编号", "标识符", "本地路径"),
    ("ai_undergraduate_graduate_curriculum_literature", "资料编号", "标识符", "本地相对路径"),
    ("time_series_literature", "编号", "标识符", "本地路径"),
]


def papers_dir(cat):
    return ROOT / cat_dir(cat) / "papers"


def seed_path(cat):
    return SEEDS / "papers" / f"{cat}_{CATS[cat][0]}_seed_cn.json"


def state_path(cat):
    return STATE / "papers" / f"{cat}_en.json"


def seeds(cat):
    return load(seed_path(cat), [])


def key_of(s):
    return "arxiv:" + s["arxiv"] if s.get("arxiv") else "url:" + s["pdf_url"]


# ---------------------------------------------------------------- arXiv metadata
def parse_entries(body):
    out = {}
    root = ET.fromstring(body)
    for e in root.findall(ATOM + "entry"):
        idtext = e.findtext(ATOM + "id") or ""
        if "/abs/" not in idtext:
            continue
        aid = idtext.rsplit("/abs/", 1)[-1]
        m = re.match(r"(.+?)v(\d+)$", aid)
        base, ver = (m.group(1), int(m.group(2))) if m else (aid, 1)
        pc = e.find(ARX + "primary_category")
        out[base] = {
            "id": base,
            "title": " ".join((e.findtext(ATOM + "title") or "").split()),
            "authors": [a.findtext(ATOM + "name") for a in e.findall(ATOM + "author")],
            "v1_date": (e.findtext(ATOM + "published") or "")[:10],
            "latest_version": ver, "latest_date": (e.findtext(ATOM + "updated") or "")[:10],
            "journal_ref": (e.findtext(ARX + "journal_ref") or "").strip(),
            "doi": (e.findtext(ARX + "doi") or "").lower(),
            "comment": " ".join((e.findtext(ARX + "comment") or "").split()),
            "abstract": " ".join((e.findtext(ATOM + "summary") or "").split()),
            "primary": pc.get("term") if pc is not None else "",
        }
    return out


def meta_file(aid):
    return META_DIR / (aid.replace("/", "_") + ".json")


def get_meta(ids, refresh=False):
    ids = [i for i in dict.fromkeys(ids) if i]
    todo = [i for i in ids if refresh or not meta_file(i).exists()]
    for i in range(0, len(todo), 40):
        chunk = todo[i:i + 40]
        st, body, _, _ = http(API + urllib.parse.urlencode({"id_list": ",".join(chunk), "max_results": len(chunk)}),
                              accept="application/atom+xml", tries=4)
        if st != 200:
            print(f"  arXiv API {st} for {len(chunk)} ids", file=sys.stderr)
            continue
        for aid, m in parse_entries(body).items():
            save(meta_file(aid), m)
    return {i: load(meta_file(i), None) for i in ids}


def search(cat, per_query=60):
    qs = load(SEEDS / "queries" / f"{cat}_en.json", [])
    cands = load(CAND_DIR / f"{cat}_en.json", {})
    win = f"submittedDate:[{WINDOW_START.replace('-', '')}0000 TO {WINDOW_END.replace('-', '')}2359]"
    for q in qs:
        qq = q["q"] if q.get("old") else f"({q['q']}) AND {win}"
        url = API + urllib.parse.urlencode({"search_query": qq, "start": 0, "max_results": per_query,
                                           "sortBy": "relevance", "sortOrder": "descending"})
        st, body, _, _ = http(url, accept="application/atom+xml", tries=4)
        if st != 200:
            print(f"  [{st}] {q['q']}")
            continue
        ents = parse_entries(body)
        for rank, (aid, m) in enumerate(ents.items()):
            save(meta_file(aid), m)
            c = cands.setdefault(aid, {"hits": []})
            c["hits"].append({"subtopic": q.get("subtopic", ""), "q": q["q"], "rank": rank})
        print(f"  {len(ents):3d} hits  {q.get('subtopic', '')}: {q['q']}")
        save(CAND_DIR / f"{cat}_en.json", cands)
    print(f"{cat}: {len(cands)} candidates")


def show(cat, show_all=False, abs_chars=0):
    cands = load(CAND_DIR / f"{cat}_en.json", {})
    rows = []
    for aid, c in cands.items():
        m = load(meta_file(aid), None)
        if not m:
            continue
        if not show_all and window_status(m["v1_date"]) != "近五年":
            continue
        best = min(h["rank"] for h in c["hits"])
        rows.append((best, -len(c["hits"]), aid, m, c))
    rows.sort(key=lambda r: (r[0], r[1]))
    for best, nh, aid, m, c in rows:
        subs = ",".join(sorted({h["subtopic"] for h in c["hits"]}))[:40]
        line = f"{aid} | {m['v1_date']} | r{best} n{-nh} | {subs} | {m['title'][:150]} | {(m['authors'] or ['?'])[0]}"
        if m.get("comment"):
            line += f" | c: {m['comment'][:80]}"
        print(line)
        if abs_chars:
            print("    " + m["abstract"][:abs_chars])


# ---------------------------------------------------------------- seed checks
def entry_meta(s):
    if s.get("arxiv"):
        m = load(meta_file(s["arxiv"]), None) or get_meta([s["arxiv"]]).get(s["arxiv"])
        if not m:
            return None
        return {"title": m["title"], "authors": m["authors"], "date": m["v1_date"], "date_basis": "arXiv v1 提交日",
                "version": f"arXiv {s['arxiv']}v{m['latest_version']}", "version_date": m["latest_date"],
                "pdf": f"https://arxiv.org/pdf/{s['arxiv']}v{m['latest_version']}",
                "landing": f"https://arxiv.org/abs/{s['arxiv']}", "journal_ref": m.get("journal_ref", ""),
                "doi": m.get("doi", ""), "comment": m.get("comment", ""), "abstract": m.get("abstract", "")}
    return {"title": s["title"], "authors": s.get("authors", []), "date": s.get("date", ""),
            "date_basis": s.get("date_basis", "出版方页面"), "version": s.get("version", "出版方 PDF"),
            "version_date": s.get("version_date", ""), "pdf": s["pdf_url"], "landing": s.get("landing", s["pdf_url"]),
            "journal_ref": s.get("venue", ""), "doi": s.get("doi", ""), "comment": "", "abstract": ""}


def all_claims():
    """key -> first claiming group (in group order)."""
    out = {}
    for c in CATS:
        for s in seeds(c):
            out.setdefault(key_of(s), c)
    return out


def check(cat):
    ss = seeds(cat)
    get_meta([s["arxiv"] for s in ss if s.get("arxiv")])
    claims = all_claims()
    main = [s for s in ss if not s.get("reserve")]
    seen, old, bad = set(), 0, 0
    for s in ss:
        k = key_of(s)
        m = entry_meta(s)
        tag = "R" if s.get("reserve") else " "
        if k in seen:
            print(f"DUP-IN-GROUP {k}")
            bad += 1
        seen.add(k)
        if not m:
            print(f"NO-META {k}")
            bad += 1
            continue
        w = window_status(m["date"])
        if w != "近五年":
            if not s.get("reserve"):
                old += 1
            if not s.get("classic_reason"):
                print(f"OLD-NO-REASON {k} {m['date']}")
                bad += 1
        if s.get("expect_title") and title_in_text(s["expect_title"], m["title"]) < 0.7:
            print(f"TITLE-MISMATCH {k}: expected '{s['expect_title']}' got '{m['title']}'")
            bad += 1
        if claims.get(k) != cat:
            print(f"CLAIMED-BY-{claims.get(k)} {k} {m['title'][:60]}")
        for f in ("subtopic", "type", "reason", "summary"):
            if not s.get(f):
                print(f"MISSING-{f} {k}")
                bad += 1
        print(f"{tag} {k:24s} {m['date']} {w[:3]} {m['title'][:70]}")
    print(f"{cat}: seeds {len(ss)} (main {len(main)}, reserve {len(ss) - len(main)}), old in main {old}, problems {bad}")


# ---------------------------------------------------------------- verification
def extract(path, maxpages=60):
    r = PdfReader(str(path))
    n = len(r.pages)
    texts = []
    for i in range(min(n, maxpages)):
        try:
            texts.append(r.pages[i].extract_text() or "")
        except Exception:  # noqa: BLE001
            texts.append("")
    if n > maxpages:  # references usually sit near the end
        for i in range(max(maxpages, n - 15), n):
            try:
                texts.append(r.pages[i].extract_text() or "")
            except Exception:  # noqa: BLE001
                texts.append("")
    return n, texts


def verify(path, m):
    data = Path(path).read_bytes()
    if data[:5] != b"%PDF-":
        return "fail", "无 %PDF- 文件头", {}
    try:
        n, texts = extract(path)
    except Exception as e:  # noqa: BLE001
        return "fail", f"pypdf 无法解析：{repr(e)[:120]}", {}
    full = "\n".join(texts)
    head = "\n".join(texts[:2])
    info = {"pages": n, "chars": len(full), "sha256": hashlib.sha256(data).hexdigest(), "bytes": len(data)}
    if n < 4:
        return "fail", f"仅 {n} 页", info
    if len(full) < 12000:
        return "fail", f"可提取文字仅 {len(full)} 字符（可能为扫描件或残缺）", info
    tm = title_in_text(m["title"], head)
    sn = surname(m["authors"][0]) if m["authors"] else ""
    au = bool(sn) and sn.lower() in re.sub(r"[^a-z]", "", fold_lower(head))
    refs = bool(re.search(r"(?i)\b(references|bibliography|works cited)\b", full)) or "参考文献" in full
    info.update({"title_match": round(tm, 2), "author_found": au, "refs": refs})
    if not refs:
        return "fail", "未找到参考文献节（可能不完整）", info
    if tm < 0.8 or not au:
        return "pending", f"标题词匹配 {tm:.2f}；第一作者姓氏{'已见' if au else '未见'}", info
    return "ok", (f"通过：HTTP 200；%PDF 头；pypdf 可解析 {n} 页、{len(full)} 字符；标题匹配 {tm:.2f}；"
                  f"第一作者姓氏已见；参考文献节已见"), info


def fold_lower(s):
    from common_en import fold
    return fold(s).lower()


def fname(m, used):
    year = (m["date"] or "0000")[:4]
    au = surname(m["authors"][0]) if m["authors"] else "Anon"
    lang = "cn" if has_cjk(m["title"]) else "en"
    base = f"{year}_{au}_{short_title(m['title'])}"
    name, i = f"{base}_{lang}.pdf", 2
    while name in used:
        name, i = f"{base}{i}_{lang}.pdf", i + 1
    return name


_SIB = None


def sibling_index():
    global _SIB
    if _SIB is None:
        _SIB = {}
        for lib, idcol, idfield, pathcol in SIBLINGS:
            p = Path("/root") / lib / "catalog_cn.csv"
            if not p.exists():
                continue
            for r in csv.DictReader(open(p, encoding="utf-8-sig")):
                blob = " ".join(str(v) for v in r.values())
                path_raw = r.get(pathcol, "") or r.get("本地路径", "") or r.get("本地相对路径", "")
                first_path = path_raw.split(";")[0].strip()
                f = Path("/root") / lib / first_path
                if not first_path or not f.is_file():
                    continue
                for aid in re.findall(r"(\d{4}\.\d{4,5}(?:v\d+)?)", blob):
                    base = re.sub(r"v\d+$", "", aid)
                    _SIB.setdefault(base, (lib, r.get(idcol, ""), str(f), r.get("SHA256", "") or r.get("SHA256（下载时记录）", "")))
    return _SIB


# ---------------------------------------------------------------- download
def download(cat, target=40, retry_failed=False):
    ss = seeds(cat)
    st = load(state_path(cat), {})
    claims = all_claims()
    outdir = papers_dir(cat)
    outdir.mkdir(parents=True, exist_ok=True)
    used = {Path(v["path"]).name for v in st.values() if v.get("path")}
    get_meta([s["arxiv"] for s in ss if s.get("arxiv")])

    def n_ok():
        return sum(1 for v in st.values() if v["status"] == "ok")

    order = [s for s in ss if not s.get("reserve")] + [s for s in ss if s.get("reserve")]
    for s in order:
        k = key_of(s)
        if s.get("reserve") and n_ok() >= target:
            break
        cur = st.get(k)
        if cur and (cur["status"] in ("ok", "pending", "rejected", "dup_elsewhere")
                    or (cur["status"] == "fail" and not retry_failed)):
            continue
        if claims.get(k) != cat:
            st[k] = {"status": "dup_elsewhere", "note": f"已由 {claims.get(k)} 群收录，本群不重复计数"}
            save(state_path(cat), st)
            continue
        m = entry_meta(s)
        if not m:
            st[k] = {"status": "fail", "note": "无法取得元数据"}
            save(state_path(cat), st)
            continue
        stage = Path(tempfile.mkdtemp(prefix="p_", dir=STAGING))
        tmp = stage / "file.pdf"
        rec = {"status": "fail", "pdf": m["pdf"], "source": "new"}
        sib = sibling_index().get(s.get("arxiv", ""))
        if sib:
            shutil.copyfile(sib[2], tmp)
            status, note, info = verify(tmp, m)
            if status == "ok":
                rec.update({"source": "reuse", "reuse_lib": sib[0], "reuse_id": sib[1], "reuse_path": sib[2]})
                note = note.replace("HTTP 200", f"已有复用（{sib[0]} {sib[1]}，本地复制后重新核验）")
        if rec["source"] == "new":
            code, body, final, ctype = http(m["pdf"], accept="application/pdf")
            if code != 200 or not body:
                rec["note"] = f"下载失败：HTTP {code} {body[:80] if code is None else ''}"
                st[k] = rec
                save(state_path(cat), st)
                shutil.rmtree(stage, ignore_errors=True)
                print(f"  FAIL {k}: {rec['note']}")
                continue
            tmp.write_bytes(body)
            status, note, info = verify(tmp, m)
        rec.update({"status": status, "note": note, **info})
        if status in ("ok", "pending"):
            name = fname(m, used)
            used.add(name)
            dest = outdir / name
            shutil.move(str(tmp), dest)
            rec["path"] = str(dest.relative_to(ROOT))
        st[k] = rec
        save(state_path(cat), st)
        shutil.rmtree(stage, ignore_errors=True)
        print(f"  {status.upper():7s} {k} {rec.get('pages', '-')}p  {m['title'][:60]}  [{n_ok()}]")
    status_line(cat)


def status_line(cat, verbose=True):
    st = load(state_path(cat), {})
    ok = sum(1 for v in st.values() if v["status"] == "ok")
    pend = sum(1 for v in st.values() if v["status"] == "pending")
    fail = sum(1 for v in st.values() if v["status"] == "fail")
    reuse = sum(1 for v in st.values() if v["status"] == "ok" and v.get("source") == "reuse")
    line = (f"{cat} {CATS[cat][1]}：已核验完整资料 {ok}（其中已有复用 {reuse}）；"
            f"待核验 {pend}；下载失败 {fail}。")
    if verbose:
        print(line)
    return line


def find_key(key):
    for c in CATS:
        st = load(state_path(c), {})
        if key in st:
            return c, st
    raise SystemExit(f"{key} not found")


def main(argv):
    cmd = argv[0]
    if cmd == "search":
        pq = int(argv[argv.index("--per-query") + 1]) if "--per-query" in argv else 60
        search(argv[1], pq)
    elif cmd == "meta":
        for aid, m in get_meta(argv[1:], refresh=True).items():
            print(aid, m and m["v1_date"], m and m["title"])
    elif cmd == "show":
        n = int(argv[argv.index("--abs") + 1]) if "--abs" in argv else 0
        show(argv[1], "--all" in argv, n)
    elif cmd == "check":
        check(argv[1])
    elif cmd == "download":
        t = int(argv[argv.index("--target") + 1]) if "--target" in argv else 40
        download(argv[1], t, "--retry-failed" in argv)
    elif cmd == "status":
        for c in ([argv[1]] if len(argv) > 1 else CATS):
            status_line(c)
    elif cmd == "text":
        c, st = find_key(argv[1])
        pages = int(argv[argv.index("--pages") + 1]) if "--pages" in argv else 2
        n, texts = extract(ROOT / st[argv[1]]["path"], pages)
        print("\n----\n".join(texts[:pages])[:6000])
    elif cmd in ("manual", "reject"):
        c, st = find_key(argv[1])
        note = argv[argv.index("--note") + 1]
        rec = st[argv[1]]
        if cmd == "manual":
            rec["status"] = "ok"
            rec["note"] = f"人工核对通过：{note}；自动检查：{rec.get('note', '')}"
        else:
            rec["status"] = "rejected"
            rec["note"] = f"人工拒收：{note}"
            if rec.get("path") and (ROOT / rec["path"]).exists():
                rej = WORK / "rejected"
                rej.mkdir(exist_ok=True)
                shutil.move(str(ROOT / rec["path"]), rej / Path(rec["path"]).name)
                rec["path"] = ""
        save(state_path(c), st)
        print(c, rec["status"])
    else:
        print(__doc__)


if __name__ == "__main__":
    main(sys.argv[1:] or ["help"])
