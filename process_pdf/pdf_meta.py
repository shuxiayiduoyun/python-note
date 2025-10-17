#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：python-note 
@File    ：pdf_meta.py
@IDE     ：PyCharm 
@Author  ：wei liyu
@Date    ：2025/10/16 20:21 
'''
"""
基于 PyMuPDF + Crossref / doi.org 的 PDF 元数据抓取：
- 从 PDF（首页为主）识别 DOI 与标题候选
- 优先用 DOI 直接拉取元数据（doi.org 内容协商 / Crossref works/{doi}）
- 没 DOI 时按标题搜索 Crossref，基于 token Jaccard 选最匹配结果
输出字段：title, year, container (期刊/会议), authors, doi, url, abstract, confidence

用法：
    from pdf_meta import extract_and_fetch
    meta = extract_and_fetch("paper.pdf", contact_email="you@example.com")
"""
# from __future__ import annotations
import re
import html
import time
import json
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple

import requests
import fitz  # PyMuPDF

_CROSSREF_API = "https://api.crossref.org/works"
_DOI_BASE = "https://doi.org/"

def _headers(contact_email: Optional[str] = None) -> Dict[str, str]:
    ua = "PaperMetaBot/1.0 (+https://example.org)"
    if contact_email:
        ua += f" mailto:{contact_email}"
    return {
        "User-Agent": ua,
        "Accept": "application/json",
    }

# ------------------ PDF 解析：DOI / 标题线索 ------------------

_DOI_RE = re.compile(r"\b(10\.\d{4,9}/[-._;()/:A-Z0-9]+)\b", re.I)

def _detect_doi_in_text(text: str) -> Optional[str]:
    m = _DOI_RE.search(text or "")
    if not m:
        return None
    doi = m.group(1)
    # 清理可能附着的尾随标点
    doi = doi.rstrip(").,;")
    return doi

def _tokenize(s: str) -> List[str]:
    return re.findall(r"[A-Za-z0-9]+", (s or "").lower())

def _token_jaccard(a: str, b: str) -> float:
    ta, tb = set(_tokenize(a)), set(_tokenize(b))
    if not ta or not tb:
        return 0.0
    return len(ta & tb) / len(ta | tb)

def _extract_title_from_page(page: fitz.Page) -> Optional[str]:
    """
    版心顶部区域，取最大字号连行作为标题（避开 Abstract/Keywords/DOI 等噪声）。
    """
    try:
        info = page.get_text("dict")
    except Exception:
        return None

    h = float(page.rect.height)
    spans = []
    for b in info.get("blocks", []):
        if b.get("type", 0) != 0:
            continue
        for line in b.get("lines", []):
            for s in line.get("spans", []):
                txt = (s.get("text") or "").strip()
                if not txt:
                    continue
                y0 = float(s.get("bbox", [0, 0, 0, 0])[1])
                spans.append(
                    dict(text=txt, size=float(s.get("size", 0)), y0=y0)
                )

    # 顶部 30% 视为标题候选区
    top_spans = [s for s in spans if s["y0"] < 0.3 * h and len(s["text"]) > 3]
    if not top_spans:
        return None

    max_size = max(s["size"] for s in top_spans)
    cand = [s for s in top_spans if s["size"] >= 0.9 * max_size]
    cand.sort(key=lambda s: (s["y0"], -s["size"]))

    # 合并相近行
    lines: List[str] = []
    buf: List[str] = []
    last_y = None
    for s in cand:
        if last_y is None or abs(s["y0"] - last_y) <= (1.6 * s["size"]):
            buf.append(s["text"])
        else:
            if buf:
                lines.append(" ".join(buf))
                buf = [s["text"]]
        last_y = s["y0"]
    if buf:
        lines.append(" ".join(buf))

    cleaned = []
    for line in lines:
        t = re.sub(r"\s+", " ", line).strip()
        # 排除常见非标题词
        if re.search(r"\b(abstract|introduction|keywords|doi|issn|copyright|proceedings|volume|vol\.|no\.)\b", t, re.I):
            continue
        if len(t) < 5:
            continue
        cleaned.append(t)

    if cleaned:
        # 多行标题常见，前两行合并
        return " ".join(cleaned[:2])
    return None

def _extract_pdf_hints(pdf_path: str, max_pages: int = 2) -> Dict[str, Any]:
    doc = fitz.open(pdf_path)
    text_all = []
    doi = None
    for i in range(min(max_pages, len(doc))):
        t = doc[i].get_text("text") or ""
        text_all.append(t)
        if doi is None:
            doi = _detect_doi_in_text(t)

    title = _extract_title_from_page(doc[0]) if len(doc) > 0 else None

    # 兜底：文本层前若干行择一
    if not title and text_all:
        lines = [x.strip() for x in text_all[0].splitlines() if x.strip()]
        for l in lines[:15]:
            if re.search(r"\b(abstract|introduction|keywords|doi)\b", l, re.I):
                break
            if re.search(r"(arxiv|issn|www|http)", l, re.I):
                continue
            letters = sum(ch.isalpha() for ch in l)
            digits = sum(ch.isdigit() for ch in l)
            if letters > 2 * digits and len(l) > 5:
                title = l
                break

    # 粗略年份候选
    year = None
    yr_cands = re.findall(r"\b(19|20)\d{2}\b", "\n".join(text_all))
    if yr_cands:
        years = [int(x[0] + x[1:]) if isinstance(x, tuple) else int(x) for x in yr_cands]  # 防小瑕疵
        years = [y for y in years if 1900 <= y <= (datetime.now().year + 1)]
        if years:
            year = min(years)

    return {"doi": doi, "title_hint": title, "year_hint": year, "text_sample": "\n".join(text_all[:2])}

# ------------------ Crossref / doi.org 查询 ------------------

def _clean_abstract(s: Optional[str]) -> str:
    if not s:
        return ""
    # 移除 JATS / HTML 标签
    s = re.sub(r"</?jats:[^>]+>", " ", s, flags=re.I)
    s = re.sub(r"</?[^>]+>", " ", s)
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def _format_authors(auth: Any) -> List[str]:
    out = []
    if not auth:
        return out
    for a in auth:
        given = (a.get("given") or a.get("given-name") or "").strip()
        family = (a.get("family") or a.get("family-name") or "").strip()
        name = (family + (", " + given if given else "")) or (a.get("name") or "").strip()
        if name:
            out.append(name)
    return out

def _pick_year_from_item(item: Dict[str, Any]) -> Optional[int]:
    for key in ("issued", "published-print", "published-online"):
        part = item.get(key, {})
        parts = part.get("date-parts") or []
        if parts and parts[0]:
            y = parts[0][0]
            try:
                y = int(y)
                if 1800 <= y <= datetime.now().year + 1:
                    return y
            except Exception:
                pass
    return None

def _get_title_from_item(item: Dict[str, Any]) -> str:
    t = (item.get("title") or [])
    return (t[0] if t else "").strip()

def _fetch_doi_via_doi_org(doi: str, contact_email: Optional[str]) -> Optional[Dict[str, Any]]:
    url = _DOI_BASE + doi
    headers = _headers(contact_email)
    headers["Accept"] = "application/vnd.citationstyles.csl+json"
    try:
        r = requests.get(url, timeout=(6, 12), headers=headers, allow_redirects=True)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

def _fetch_doi_via_crossref(doi: str, contact_email: Optional[str]) -> Optional[Dict[str, Any]]:
    url = f"{_CROSSREF_API}/{requests.utils.quote(doi)}"
    try:
        r = requests.get(url, timeout=(6, 12), headers=_headers(contact_email))
        if r.status_code == 200:
            return r.json().get("message")
    except Exception:
        pass
    return None

def _search_crossref_by_title(title: str, contact_email: Optional[str], rows: int = 5) -> List[Dict[str, Any]]:
    params = {"query.bibliographic": title, "rows": rows}
    try:
        r = requests.get(_CROSSREF_API, params=params, timeout=(8, 15), headers=_headers(contact_email))
        if r.status_code == 200:
            return r.json().get("message", {}).get("items", []) or []
    except Exception:
        pass
    return []

def _select_best_by_title(pdf_title: str, items: List[Dict[str, Any]]) -> Tuple[Optional[Dict[str, Any]], float]:
    """返回 (最佳条目, 匹配分数[0~1])。基于 token Jaccard。"""
    if not pdf_title or not items:
        return None, 0.0
    best, best_s = None, 0.0
    for it in items:
        t = _get_title_from_item(it)
        s = _token_jaccard(pdf_title, t)
        if s > best_s:
            best, best_s = it, s
    return best, best_s

@dataclass
class MetaResult:
    pdf_path: str
    title: str = ""
    year: Optional[int] = None
    container: str = ""  # 期刊/会议
    authors: List[str] = None
    doi: str = ""
    url: str = ""
    abstract: str = ""
    source: str = ""     # 'doi.org' / 'crossref-doi' / 'crossref-search'
    confidence: float = 0.0
    hint_title: str = "" # PDF 识别到的标题候选

    def as_item_fields(self) -> Dict[str, Any]:
        return dict(
            title=self.title or self.hint_title,
            creators=self.authors or [],
            year=str(self.year or ""),
            venue=self.container or "",
            type="Article",
            tags=["auto-import"],
            abstract=self.abstract or "",
            doi=self.doi or "",
            url=self.url or (f"{_DOI_BASE}{self.doi}" if self.doi else ""),
        )

def extract_and_fetch(pdf_path: str, contact_email: Optional[str] = None, polite_delay: float = 0.0) -> MetaResult:
    """
    主函数：对单个 PDF 提取元数据。
    polite_delay: 每次网络访问后的轻微 sleep，避免过快轮询（如 0.2 秒）
    """
    hints = _extract_pdf_hints(pdf_path)
    doi = hints.get("doi")
    hint_title = hints.get("title_hint") or ""

    # 优先：有 DOI 则直取
    # 先试 doi.org，再退 Crossref
    if doi:
        item = _fetch_doi_via_doi_org(doi, contact_email)
        if polite_delay: time.sleep(polite_delay)
        if not item:
            item = _fetch_doi_via_crossref(doi, contact_email)
            if polite_delay: time.sleep(polite_delay)
        if item:
            # doi.org 返回的是 CSL JSON；Crossref message 结构稍不同，这里统一取字段
            title = (item.get("title") or (item.get("title", [""]) if isinstance(item.get("title"), list) else ""))  # 兼容
            if isinstance(title, list):
                title = title[0] if title else ""
            authors = _format_authors(item.get("author"))
            abstract = _clean_abstract(item.get("abstract"))
            container = ""
            if isinstance(item.get("container-title"), list):
                container = (item.get("container-title") or [""])[0]
            else:
                container = item.get("container-title") or item.get("container_title") or ""
            year = None
            # doi.org CSL 用 'issued'；Crossref 也有 issued/published-*
            year = _pick_year_from_item(item) or item.get("issued", {}).get("date-parts", [[None]])[0][0]
            try:
                year = int(year) if year else None
            except Exception:
                year = None
            url = item.get("URL") or item.get("url") or f"{_DOI_BASE}{doi}"

            conf = _token_jaccard(hint_title, title) if hint_title else 1.0

            return MetaResult(
                pdf_path=pdf_path, title=title or "", year=year, container=container or "",
                authors=authors, doi=doi, url=url, abstract=abstract, source="doi.org/crossref",
                confidence=float(conf), hint_title=hint_title
            )

    # 其次：按标题搜索 Crossref
    if hint_title:
        items = _search_crossref_by_title(hint_title, contact_email, rows=5)
        if polite_delay: time.sleep(polite_delay)
        best, score = _select_best_by_title(hint_title, items)
        if best:
            title = _get_title_from_item(best)
            authors = _format_authors(best.get("author"))
            abstract = _clean_abstract(best.get("abstract"))
            container = (best.get("container-title") or [""])
            container = container[0] if container else ""
            year = _pick_year_from_item(best)
            doi = best.get("DOI") or ""
            url = best.get("URL") or (f"{_DOI_BASE}{doi}" if doi else "")
            return MetaResult(
                pdf_path=pdf_path, title=title or "", year=year, container=container or "",
                authors=authors, doi=doi, url=url, abstract=abstract, source="crossref-search",
                confidence=float(score), hint_title=hint_title
            )

    # 全部失败：只返回 PDF 线索
    return MetaResult(pdf_path=pdf_path, title=hint_title or "", hint_title=hint_title, confidence=0.0)


if __name__ == '__main__':
    file_path = "D:\Downloads\\2506.21611v2.pdf"
    infos = extract_and_fetch(file_path)
    print(infos.as_item_fields())
