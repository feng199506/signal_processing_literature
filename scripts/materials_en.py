"""Books (B), courses (A), practice (D), applied cases (E), software docs (S) and curricula (P) for PSCL.

  python3 -I scripts/materials_en.py fetch books|courses|practice|cases|software|curricula [--only MID] [--retry-failed]
  python3 -I scripts/materials_en.py status [books|courses|practice|cases|software|curricula]

Manifests: scripts/seeds/materials/<set>_cn.json (list of items; list order = reading order inside a
group). Common item fields: mid, group (primary course group "NN"), related (list), title, authors,
institution (school or publisher), code, term (course term) / edition, orig_year, edition_year, level,
requirement, lang, license, prereq, difficulty, reason, summary, summary_basis, toc_check, kind.
Kinds:
  pdf        one official PDF (whole book / whole lecture-notes volume / programme document)
  pdfs       several official PDFs forming the whole work: `urls`, or `index_url` + `link_regex`
             (every matching link on the official index page). Every file must pass.
  zip        official archive (zip or tar.gz; e.g. MIT OCW "download course", official HTML doc bundle);
             every PDF inside must parse; `min_pdfs` (default 1) / `min_html` (default 0)
  html       official HTML book/course/programme page set: `index_url` + optional `link_regex`
             (table of contents) + `extra_pages`; each page HTTP 200 with >= min_chars text;
             saved offline with wget (page requisites, converted links) into <name>_html_<lang>/
  reuse      copy a verified file or directory from a sibling library (`src`, `src_id`), re-check
  git        official public repository snapshot: `repo` (https URL), optional `ref`; the commit is
             resolved with `git ls-remote`, the GitHub/GitLab archive of that commit is downloaded,
             zip-tested, `must_contain` paths checked, and unpacked to practice/<name>/ (not run)
Hard checks for PDFs: %PDF- header, pypdf parses, page minimums, `title_phrase` in the first 12 pages
of the main file. State: scripts/state/materials/<mid>.json. Failed items are never counted.
"""
import hashlib
import html as htmlmod
import io
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import urllib.parse
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common_en import ROOT, SEEDS, STAGING, STATE, PYLIB, UA, http, load, save, norm  # noqa: E402

sys.path.insert(0, str(PYLIB))
import logging  # noqa: E402
logging.getLogger("pypdf").setLevel(logging.ERROR)
from pypdf import PdfReader  # noqa: E402

SETS = {"books": "books", "courses": "courses", "software": "software_docs", "projects": "projects"}
RES = STATE / "materials"


def manifest(s):
    """All items of a set: seeds/materials/<set>_cn.json plus any <set>_<part>_cn.json."""
    out = []
    for p in sorted((SEEDS / "materials").glob(f"{s}*_cn.json")):
        out += load(p, [])
    return out


def res_path(mid):
    return RES / f"{mid}.json"


def pdf_info(data, phrase=None, head_pages=12):
    if data[:5] != b"%PDF-":
        return None, "无 %PDF- 头"
    try:
        r = PdfReader(io.BytesIO(data))
        n = len(r.pages)
        head = ""
        if phrase:
            for p in r.pages[:head_pages]:
                try:
                    head += (p.extract_text() or "") + "\n"
                except Exception:  # noqa: BLE001
                    pass
        found = (norm(phrase) in norm(head)) if phrase else None
        return {"pages": n, "phrase_found": found}, "ok"
    except Exception as e:  # noqa: BLE001
        return None, f"pypdf 无法解析：{repr(e)[:100]}"


def get(url, timeout=900):
    return http(url, accept="*/*", timeout=timeout, max_bytes=1_500_000_000)


def links_from(index_url, regex):
    st, body, final, _ = get(index_url)
    if st != 200:
        return None, f"索引页 HTTP {st}"
    txt = body.decode("utf-8", "replace")
    out = []
    for h in re.findall(r'(?:href|src)=["\']([^"\'#]+)', txt):
        u = urllib.parse.urljoin(final, htmlmod.unescape(h.strip()))
        if re.search(regex, u) and u not in out:
            out.append(u)
    return out, "ok"


def safe(s):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", s).strip("_")[:60]


def sha(b):
    return hashlib.sha256(b).hexdigest()


def do_pdf(it, stage):
    st, body, final, ct = get(it["url"])
    if st != 200:
        return None, f"HTTP {st}"
    info, why = pdf_info(body, it.get("title_phrase"))
    if not info:
        return None, why
    if info["pages"] < it.get("min_pages", 50):
        return None, f"仅 {info['pages']} 页 < {it.get('min_pages', 50)}"
    if it.get("title_phrase") and not info["phrase_found"]:
        return None, f"前 12 页未见名称短语“{it['title_phrase']}”"
    name = f"{it['name']}_{it.get('lang', 'en')}.pdf"
    (stage / name).write_bytes(body)
    return {"files": [{"path": name, "url": final, "pages": info["pages"], "sha256": sha(body), "bytes": len(body)}],
            "note": f"HTTP 200；%PDF；pypdf 可解析 {info['pages']} 页"
                    + ("；名称短语已见" if it.get("title_phrase") else "")}, "ok"


def do_pdfs(it, stage):
    urls = it.get("urls")
    if not urls:
        urls, why = links_from(it["index_url"], it["link_regex"])
        if not urls:
            return None, f"未从索引页取得文件链接（{why}）"
    urls = [u for u in urls if not any(re.search(x, u) for x in it.get("skip_regex", []))]
    if len(urls) < it.get("min_files", 1):
        return None, f"仅取得 {len(urls)} 个文件 < {it.get('min_files')}"
    lang = it.get("lang", "en")
    pkg = stage / f"{it['name']}_{lang}"
    pkg.mkdir()
    files, total = [], 0
    for i, u in enumerate(urls, 1):
        st, body, final, ct = get(u)
        if st != 200:
            return None, f"第 {i} 个文件 HTTP {st}: {u}"
        info, why = pdf_info(body, it.get("title_phrase") if i == 1 else None)
        if not info:
            return None, f"第 {i} 个文件 {u}: {why}"
        if info["pages"] < it.get("min_pages_each", 1):
            return None, f"第 {i} 个文件仅 {info['pages']} 页: {u}"
        if i == 1 and it.get("title_phrase") and not info["phrase_found"]:
            return None, f"首个文件前 12 页未见名称短语“{it['title_phrase']}”"
        base = Path(urllib.parse.unquote(urllib.parse.urlparse(final).path)).stem
        fn = f"{i:02d}_{safe(base)}_{lang}.pdf"
        (pkg / fn).write_bytes(body)
        total += info["pages"]
        files.append({"path": f"{pkg.name}/{fn}", "url": final, "pages": info["pages"], "sha256": sha(body),
                      "bytes": len(body)})
    if total < it.get("min_pages", 1):
        return None, f"合计仅 {total} 页 < {it.get('min_pages')}"
    src = f"；文件链接取自官方索引页 {it['index_url']}（该页列出的全部匹配文件均已下载）" if it.get("index_url") else ""
    return {"files": files, "note": f"{len(files)} 个 PDF 全部 HTTP 200 且可解析，合计 {total} 页{src}"}, "ok"


def do_zip(it, stage):
    st, body, final, ct = get(it["url"], timeout=1800)
    if st != 200:
        return None, f"HTTP {st}"
    if len(body) > it.get("max_mb", 600) * 2**20:
        return None, f"归档 {len(body) >> 20} MiB 超过上限"
    is_tar = False
    try:
        z = zipfile.ZipFile(io.BytesIO(body))
        bad = z.testzip()
        names = z.namelist()
        read = z.read
    except Exception as e:  # noqa: BLE001
        try:
            t = tarfile.open(fileobj=io.BytesIO(body), mode="r:*")
            members = {m.name: m for m in t.getmembers() if m.isfile()}
            names, bad, is_tar = list(members), None, True
            read = lambda n: t.extractfile(members[n]).read()  # noqa: E731
        except Exception:  # noqa: BLE001
            return None, f"归档无法打开：{repr(e)[:80]}"
    if bad:
        return None, f"zip 校验失败：{bad}"
    pdfs = [n for n in names if n.lower().endswith(".pdf")]
    htmls = [n for n in names if n.lower().endswith((".html", ".htm"))]
    pages, broken = 0, []
    for n in pdfs:
        info, why = pdf_info(read(n))
        if not info:
            broken.append(n)
        else:
            pages += info["pages"]
    if broken:
        return None, f"{len(broken)} 个 PDF 不可解析，如 {broken[0]}"
    if len(pdfs) < it.get("min_pdfs", 1):
        return None, f"仅 {len(pdfs)} 个 PDF < {it.get('min_pdfs', 1)}"
    if len(htmls) < it.get("min_html", 0):
        return None, f"仅 {len(htmls)} 个 HTML < {it.get('min_html')}"
    low = " ".join(names).lower()
    miss = [m for m in it.get("must_contain", []) if m.lower() not in low]
    if miss:
        return None, f"缺少应有文件：{miss}"
    ext = Path(urllib.parse.urlparse(final).path).name.split(".", 1)[-1] if is_tar else "zip"
    name = f"{it['name']}_{it.get('lang', 'en')}.{ext if is_tar else 'zip'}"
    (stage / name).write_bytes(body)
    kind = "tar 归档" if is_tar else "zip 完整性通过"
    return {"files": [{"path": name, "url": final, "pdfs": len(pdfs), "pdf_pages": pages, "html": len(htmls),
                       "sha256": sha(body), "bytes": len(body)}],
            "note": f"官方压缩包（原样保存），{kind}，含 {len(names)} 个文件、{len(pdfs)} 个 PDF"
                    f"（合计 {pages} 页）全部可解析、{len(htmls)} 个 HTML"}, "ok"


def page_text(body):
    t = re.sub(r"(?s)<(script|style)[^>]*>.*?</\1>", " ", body.decode("utf-8", "replace"))
    return re.sub(r"\s+", " ", htmlmod.unescape(re.sub(r"<[^>]+>", " ", t))).strip()


def _looks_html(body, ct):
    return ("html" in (ct or "").lower()) or (
        body and (b"<html" in body[:4000].lower() or b"<!doctype" in body[:400].lower())
    )


def _save_html_body(site, url, body, final):
    parsed = urllib.parse.urlparse(final or url)
    rel = parsed.path.lstrip("/")
    if not rel or rel.endswith("/"):
        rel = (rel or "") + "index.html"
    elif "." not in Path(rel).name:
        rel = rel.rstrip("/") + "/index.html"
    out = site / parsed.netloc / rel
    if parsed.query:
        out = out.with_name(out.stem + "_" + safe(parsed.query)[:40] + (out.suffix or ".html"))
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(body)
    return out


def do_html(it, stage):
    lang = it.get("lang", "en")
    site = stage / f"{it['name']}_html_{lang}"
    site.mkdir()
    minc = it.get("min_chars", 1500)
    st, body, final, ct = get(it["index_url"])
    if st != 200 or not _looks_html(body, ct):
        return None, f"首页 HTTP {st} {ct}: {it['index_url']}"
    first = page_text(body)
    if it.get("title_phrase") and norm(it["title_phrase"]) not in norm(first):
        return None, f"首页未见名称短语“{it['title_phrase']}”"
    if it.get("mirror"):
        base = it.get("mirror_url") or (it["index_url"].rsplit("/", 1)[0] + "/")
        r = subprocess.run(
            ["wget", "-q", "-r", "-np", "-nH", "-E", "-k", "-l", str(it.get("mirror_depth", 2)),
             "--wait=0.3", "-T", "60", "-t", "2", "-R", "mp3,wav,zip,mp4,mov",
             "-e", "robots=on", "-U", UA, "-P", str(site), base],
            capture_output=True, timeout=1800)
        if r.returncode not in (0, 8):
            return None, f"镜像 wget 失败 {r.returncode}: {base}"
        nhtml = sum(1 for p in site.rglob("*") if p.suffix.lower() in {".html", ".htm", ".xhtml"})
        if nhtml < it.get("min_files", 1):
            return None, f"镜像仅 {nhtml} 个 HTML < {it.get('min_files')}"
        nfiles = sum(1 for p in site.rglob("*") if p.is_file())
        nbytes = sum(p.stat().st_size for p in site.rglob("*") if p.is_file())
        (site / f"PAGES_{lang}.txt").write_text(f"mirror {base}\nindex {it['index_url']}\n")
        note = (f"官方 HTML 目录镜像：首页 HTTP 200 且名称短语已见；wget -r -np -l {it.get('mirror_depth', 2)} "
                f"保存 {nhtml} 个 HTML、共 {nfiles} 个文件（未保存音视频安装包）")
        return {"files": [{"path": site.name, "url": it["index_url"], "html_pages": nhtml, "files": nfiles,
                           "bytes": nbytes}], "note": note}, "ok"
    pages = [it["index_url"]]
    if it.get("link_regex"):
        found, why = links_from(it["index_url"], it["link_regex"])
        if found is None:
            return None, why
        pages += [u for u in found if u.split("#")[0] not in pages]
    pages += [u for u in it.get("extra_pages", []) if u not in pages]
    if len(pages) < it.get("min_files", 1):
        return None, f"目录只解析到 {len(pages)} 页 < {it.get('min_files')}"
    short = []
    saved = []
    for u in pages:
        if u == it["index_url"]:
            st2, body2, final2, ct2 = st, body, final, ct
        else:
            st2, body2, final2, ct2 = get(u)
        if st2 != 200 or not _looks_html(body2, ct2):
            return None, f"页面 HTTP {st2} {ct2}: {u}"
        txt = page_text(body2)
        if len(txt) < minc:
            short.append(u)
        saved.append(str(_save_html_body(site, u, body2, final2)))
    if len(short) > it.get("allow_short", 0):
        return None, f"{len(short)} 个页面正文 < {minc} 字符，如 {short[0]}"
    (site / f"PAGES_{lang}.txt").write_text("\n".join(pages) + "\n")
    nfiles = sum(1 for p in site.rglob("*") if p.is_file())
    nbytes = sum(p.stat().st_size for p in site.rglob("*") if p.is_file())
    note = (f"官方 HTML，{len(pages)} 个页面全部 HTTP 200 且正文 ≥ {minc} 字符"
            + (f"（允许 {len(short)} 个短页：目录/附录页）" if short else "")
            + f"；已按 URL 路径保存页面本体（未镜像站外 CSS/JS），共 {nfiles} 个文件；页面清单 PAGES_{lang}.txt")
    return {"files": [{"path": site.name, "url": it["index_url"], "html_pages": len(pages), "files": nfiles,
                       "bytes": nbytes}], "note": note}, "ok"


def do_reuse(it, stage):
    src = Path(it["src"])
    if not src.exists():
        return None, f"来源不存在：{src}"
    lang = it.get("lang", "en")
    if src.is_dir():
        dest = stage / f"{it['name']}_{lang}"
        shutil.copytree(src, dest, symlinks=False)
        pdfs = sorted(dest.rglob("*.pdf"))
        pages = 0
        for p in pdfs:
            info, why = pdf_info(p.read_bytes())
            if not info:
                return None, f"{p.name}: {why}"
            pages += info["pages"]
        htmls = list(dest.rglob("*.htm*"))
        if not pdfs and not htmls:
            return None, "目录内无 PDF/HTML"
        nfiles = sum(1 for p in dest.rglob("*") if p.is_file())
        note = (f"已有复用：复制自 {it.get('src_lib', '')} {it.get('src_id', '')}（{src}），本库重新检查："
                f"{nfiles} 个文件，{len(pdfs)} 个 PDF 全部可解析（合计 {pages} 页），HTML {len(htmls)} 个")
        return {"files": [{"path": dest.name, "copied_from": str(src), "files": nfiles, "pdf_pages": pages}],
                "reuse": True, "note": note}, "ok"
    body = src.read_bytes()
    if src.suffix.lower() == ".zip":
        try:
            zipfile.ZipFile(io.BytesIO(body)).testzip()
        except Exception as e:  # noqa: BLE001
            return None, f"zip 无法打开：{e!r}"[:120]
        name = f"{it['name']}_{lang}.zip"
        (stage / name).write_bytes(body)
        return {"files": [{"path": name, "copied_from": str(src), "sha256": sha(body), "bytes": len(body)}],
                "reuse": True, "note": f"已有复用：复制自 {it.get('src_lib', '')} {it.get('src_id', '')}，zip 完整性通过"}, "ok"
    info, why = pdf_info(body, it.get("title_phrase"))
    if not info:
        return None, why
    if info["pages"] < it.get("min_pages", 50):
        return None, f"仅 {info['pages']} 页"
    if it.get("title_phrase") and not info["phrase_found"]:
        return None, f"前 12 页未见名称短语“{it['title_phrase']}”"
    name = f"{it['name']}_{lang}.pdf"
    (stage / name).write_bytes(body)
    return {"files": [{"path": name, "copied_from": str(src), "pages": info["pages"], "sha256": sha(body),
                       "bytes": len(body)}], "reuse": True,
            "note": f"已有复用：复制自 {it.get('src_lib', '')} {it.get('src_id', '')}，本库重新核验：%PDF；pypdf 可解析 "
                    f"{info['pages']} 页" + ("；名称短语已见" if it.get("title_phrase") else "")}, "ok"


def do_git(it, stage):
    repo = it["repo"].rstrip("/")
    ref = it.get("ref", "HEAD")
    r = subprocess.run(["git", "ls-remote", repo + ".git", ref], capture_output=True, text=True, timeout=120,
                       env={"GIT_TERMINAL_PROMPT": "0", "PATH": "/usr/bin:/bin"})
    line = (r.stdout.split("\n") or [""])[0].split()
    if r.returncode or not line:
        return None, f"git ls-remote 失败：{r.stderr.strip()[:100]}"
    commit = line[0]
    host = urllib.parse.urlparse(repo).netloc
    path = urllib.parse.urlparse(repo).path.strip("/")
    if host == "github.com":
        url = f"https://codeload.github.com/{path}/zip/{commit}"
    elif "gitlab" in host:
        url = f"{repo}/-/archive/{commit}/{path.split('/')[-1]}-{commit}.zip"
    else:
        return None, f"不支持的代码托管：{host}"
    st, body, final, ct = get(url, timeout=1800)
    if st != 200:
        return None, f"归档下载 HTTP {st}"
    if len(body) > it.get("max_mb", 150) * 2**20:
        return None, f"归档 {len(body) >> 20} MiB 超过上限"
    try:
        z = zipfile.ZipFile(io.BytesIO(body))
        bad = z.testzip()
    except Exception as e:  # noqa: BLE001
        return None, f"zip 无法打开：{repr(e)[:80]}"
    if bad:
        return None, f"zip 校验失败：{bad}"
    names = z.namelist()
    root = names[0].split("/")[0] + "/"
    rel = [n[len(root):] for n in names if n.startswith(root)]
    miss = [m for m in it.get("must_contain", []) if not any(x.startswith(m) for x in rel)]
    if miss:
        return None, f"缺少应有文件/目录：{miss}"
    lic = [x for x in rel if re.match(r"(?i)^(license|licence|copying)(\.|$)", x)]
    nb = sum(1 for x in rel if x.endswith(".ipynb"))
    lang = it.get("lang", "en")
    dest = stage / f"{it['name']}_{lang}"
    dest.mkdir()
    for n in names:
        if not n.startswith(root) or n.endswith("/"):
            continue
        relp = Path(n[len(root):])
        if relp.is_absolute() or ".." in relp.parts:
            continue
        out = dest / relp
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(z.read(n))
    (dest / f"SNAPSHOT_{lang}.txt").write_text(f"repo: {repo}\nref: {ref}\ncommit: {commit}\narchive: {url}\n"
                                               f"archive_sha256: {sha(body)}\n")
    keep = it.get("keep_paths") or []
    drop_globs = it.get("drop_globs") or ["*.pt", "*.pth", "*.ckpt", "*.h5", "*.onnx", "*.bin",
                                          "*.pkl.gz", "*.npy", "*.npz", "*.csv.gz"]
    if keep or drop_globs:
        import fnmatch
        for f in list(dest.rglob("*")):
            if not f.is_file() or f.name.startswith("SNAPSHOT_"):
                continue
            rel = str(f.relative_to(dest)).replace("\\", "/")
            if keep and not any(rel == k or rel.startswith(k.rstrip("/") + "/") or fnmatch.fnmatch(rel, k)
                                or fnmatch.fnmatch(Path(rel).name, k) for k in keep):
                f.unlink()
                continue
            if any(fnmatch.fnmatch(rel, g) or fnmatch.fnmatch(Path(rel).name, g) for g in drop_globs):
                f.unlink()
        for d in sorted((x for x in dest.rglob("*") if x.is_dir()), key=lambda x: len(x.parts), reverse=True):
            try:
                d.rmdir()
            except OSError:
                pass
    missing_lfs = [n for n in names if n.endswith(".lfs") or "/lfs/" in n.lower()]
    nfiles = sum(1 for _ in dest.rglob("*") if _.is_file())
    return {"files": [{"path": dest.name, "url": repo, "commit": commit, "files": nfiles, "archive_sha256": sha(body),
                       "bytes": len(body)}], "commit": commit, "license_files": lic,
            "note": f"官方仓库快照 commit {commit[:12]}：归档 zip 完整性通过，解压 {nfiles} 个文件（{nb} 个 notebook）"
                    + (f"；应有文件已见 {it['must_contain']}" if it.get("must_contain") else "")
                    + (f"；仅保留路径 {keep}" if keep else "")
                    + (f"；许可证文件 {lic}" if lic else "；仓库根目录未见许可证文件")
                    + ("；未发现 LFS 指针文件" if not missing_lfs else f"；发现可能的 LFS 路径 {missing_lfs[:5]}，未当作已保存依赖")}, "ok"


KINDS = {"pdf": do_pdf, "pdfs": do_pdfs, "zip": do_zip, "html": do_html, "reuse": do_reuse, "git": do_git}


def fetch(s, only=None, retry_failed=False):
    STAGING.mkdir(parents=True, exist_ok=True)
    for it in manifest(s):
        mid = it["mid"]
        if only and mid not in only.split(","):
            continue
        r = load(res_path(mid), {})
        if it.get("exclude") or r.get("status") == "verified":
            continue
        if r.get("status") == "failed" and not retry_failed and not only:
            continue
        dest = ROOT / it.get("dest", SETS[s])
        dest.mkdir(parents=True, exist_ok=True)
        stage = Path(tempfile.mkdtemp(prefix="mat_", dir=STAGING))
        try:
            out, why = KINDS[it["kind"]](it, stage)
        except Exception as e:  # noqa: BLE001
            out, why = None, f"异常：{repr(e)[:150]}"
        if not out:
            save(res_path(mid), {"status": "failed", "set": s, "note": why, "title": it["title"]})
            print(f"{mid} FAILED {it['title'][:60]} :: {why}", flush=True)
        else:
            for p in stage.iterdir():
                if (dest / p.name).exists():
                    raise SystemExit(f"refusing to overwrite {dest / p.name}")
            rel_root = dest.relative_to(ROOT)
            for p in stage.iterdir():
                shutil.move(str(p), dest / p.name)
            for f in out["files"]:
                f["path"] = f"{rel_root}/{f['path']}"
            save(res_path(mid), {"status": "verified", "set": s, "title": it["title"], **out})
            print(f"{mid} VERIFIED {it['title'][:60]} :: {out['note'][:110]}", flush=True)
        shutil.rmtree(stage, ignore_errors=True)
    status(s)


def status(s):
    items = [i for i in manifest(s) if not i.get("exclude")]
    ok = [i for i in items if load(res_path(i["mid"]), {}).get("status") == "verified"]
    fail = [i for i in items if load(res_path(i["mid"]), {}).get("status") == "failed"]
    print(f"[{s}] 已核验完整资料 {len(ok)}；待核验 {len(items) - len(ok) - len(fail)}；下载失败 {len(fail)}。")
    for i in fail:
        print("   failed", i["mid"], i["title"][:50], "::", load(res_path(i["mid"]), {})["note"][:140])


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "fetch":
        fetch(a[1], a[a.index("--only") + 1] if "--only" in a else None, "--retry-failed" in a)
    elif a and a[0] == "status":
        for s in ([a[1]] if len(a) > 1 else SETS):
            status(s)
    else:
        print(__doc__)
