#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：python-note 
@File    ：meta_resolver.py
@IDE     ：PyCharm 
@Author  ：wei liyu
@Date    ：2025/10/17 8:17 
'''
# -*- coding: utf-8 -*-
"""
Unified metadata resolver for DOI / URL / arXiv URL.

Given a DOI or a URL (including arXiv URLs), returns:
  title, authors (list[str]), year (int or None), container (journal/conference),
  abstract (plain text), doi, url

Usage:
    from meta_resolver import get_metadata
    print(get_metadata(doi="10.1038/nature14539"))
    print(get_metadata(url="https://doi.org/10.1038/nature14539"))
    print(get_metadata(url="https://arxiv.org/abs/1706.03762"))
"""

import re
import json
import html
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import Dict, Any, List, Optional
import xml.etree.ElementTree as ET

_CROSSREF_API = "https://api.crossref.org/works"
_DOI_BASE = "https://doi.org/"
_ARXIV_API = "http://export.arxiv.org/api/query"  # Atom


# ------------------------ Utilities ------------------------

def _headers(contact_email: Optional[str] = None, accept_json=True) -> Dict[str, str]:
    ua = "MetaResolver/1.0 (+https://example.org)"
    if contact_email:
        ua += f" mailto:{contact_email}"
    headers = {"User-Agent": ua}
    if accept_json:
        headers["Accept"] = "application/json"
    return headers


def _clean_text(s: Optional[str]) -> str:
    if not s:
        return ""
    s = html.unescape(s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def _clean_abstract(s: Optional[str]) -> str:
    if not s:
        return ""
    # 去掉常见 HTML/JATS 标签
    s = re.sub(r"</?jats:[^>]+>", " ", s, flags=re.I)
    s = re.sub(r"</?[^>]+>", " ", s)
    return _clean_text(s)


def _norm_year(y) -> Optional[int]:
    try:
        y = int(str(y)[:4])
        if 1800 <= y <= datetime.now().year + 1:
            return y
    except Exception:
        pass
    return None


def _format_authors_cr(auth: Any) -> List[str]:
    out = []
    if not auth:
        return out
    for a in auth:
        given = (a.get("given") or "").strip()
        family = (a.get("family") or "").strip()
        if family and given:
            out.append(f"{given} {family}")
        elif family:
            out.append(family)
        elif given:
            out.append(given)
    return out


# ------------------------ DOI path ------------------------

def _get_metadata_from_doi(doi: str, contact_email: Optional[str] = None) -> Optional[Dict[str, Any]]:
    doi = doi.strip().replace(" ", "")
    if doi.lower().startswith("https://doi.org/") or doi.lower().startswith("http://doi.org/"):
        doi = re.sub(r"^https?://doi\.org/", "", doi, flags=re.I)

    # 1) try doi.org content negotiation (CSL JSON)
    try:
        r = requests.get(
            _DOI_BASE + doi,
            headers={**_headers(contact_email, accept_json=False),
                     "Accept": "application/vnd.citationstyles.csl+json"},
            timeout=(8, 15),
            allow_redirects=True,
        )
        if r.status_code == 200 and r.headers.get("Content-Type", "").startswith(
                ("application/vnd.citationstyles", "application/json")):
            d = r.json()
            title = d.get("title") or ""
            if isinstance(title, list):
                title = title[0] if title else ""
            authors = _format_authors_cr(d.get("author"))
            # year from issued
            year = None
            issued = d.get("issued", {}).get("date-parts", [[None]])
            if issued and issued[0]:
                year = _norm_year(issued[0][0])
            container = ""
            ct = d.get("container-title")  # 期刊名
            if isinstance(ct, list):
                container = ct[0] if ct else ""
            else:
                container = ct or ""
            abstract = _clean_abstract(d.get("abstract"))
            url = d.get("URL") or f"{_DOI_BASE}{doi}"

            return {
                "title": _clean_text(title),
                "authors": authors,
                "year": year,
                "container": _clean_text(container),
                "abstract": abstract,
                "doi": doi,
                "url": url,
                "source": "doi.org"
            }
    except Exception:
        pass

    # 2) fallback to Crossref works/{doi}
    try:
        r = requests.get(f"{_CROSSREF_API}/{requests.utils.quote(doi)}",
                         headers=_headers(contact_email),
                         timeout=(8, 15))
        if r.status_code == 200:
            m = r.json().get("message", {})
            title = (m.get("title") or [""])[0]
            authors = _format_authors_cr(m.get("author"))
            year = None
            for key in ("issued", "published-print", "published-online"):
                dp = (m.get(key) or {}).get("date-parts") or []
                if dp and dp[0]:
                    year = _norm_year(dp[0][0])
                    if year:
                        break
            container = (m.get("container-title") or [""])
            container = container[0] if container else ""
            abstract = _clean_abstract(m.get("abstract"))
            url = m.get("URL") or f"{_DOI_BASE}{doi}"
            return {
                "title": _clean_text(title),
                "authors": authors,
                "year": year,
                "container": _clean_text(container),
                "abstract": abstract,
                "doi": doi,
                "url": url,
                "source": "crossref"
            }
    except Exception:
        pass

    return None


# ------------------------ arXiv path ------------------------

_ARXIV_ID_RE = re.compile(
    r"""(?ix)
    (?:arxiv\.org/(?:abs|pdf)/|arxiv:)\s*
    (?P<id>
        (?:\d{4}\.\d{4,5})        # new style 1706.03762
        |(?:[a-z\-]+/\d{7})       # old style cs/0112017
    )
    (?:v\d+)?                     # optional version
    (?:\.pdf)?$
    """
)


def _extract_arxiv_id(s: str) -> Optional[str]:
    s = s.strip()
    m = _ARXIV_ID_RE.search(s)
    if m:
        return m.group("id")
    # also accept a bare ID
    if re.fullmatch(r"\d{4}\.\d{4,5}(?:v\d+)?", s):
        return s.split("v")[0]
    if re.fullmatch(r"[a-z\-]+/\d{7}(?:v\d+)?", s, re.I):
        return s.split("v")[0]
    return None


def _get_metadata_from_arxiv(url_or_id: str) -> Optional[Dict[str, Any]]:
    aid = _extract_arxiv_id(url_or_id)
    if not aid:
        return None
    params = {"id_list": aid}
    try:
        r = requests.get(_ARXIV_API, params=params, timeout=(8, 15),
                    headers=_headers(accept_json=False))
        if r.status_code != 200:
            return None
        root = ET.fromstring(r.text)
        ns = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}
        entry = root.find("atom:entry", ns)
        if entry is None:
            return None

        title = entry.findtext("atom:title", default="", namespaces=ns)
        summary = entry.findtext("atom:summary", default="", namespaces=ns)
        published = entry.findtext("atom:published", default="", namespaces=ns)
        link_id = entry.findtext("atom:id", default="", namespaces=ns)

        authors = []
        for a in entry.findall("atom:author", ns):
            nm = a.findtext("atom:name", default="", namespaces=ns)
            if nm:
                authors.append(_clean_text(nm))

        doi = entry.findtext("arxiv:doi", default="", namespaces=ns) or ""
        journal_ref = entry.findtext("arxiv:journal_ref", default="", namespaces=ns) or ""
        year = _norm_year(published)

        # 优先使用 journal_ref 作为 container，否则标记为 arXiv
        container = journal_ref if journal_ref else "arXiv"

        return {
            "title": _clean_text(title),
            "authors": authors,
            "year": year,
            "container": _clean_text(container),
            "abstract": _clean_text(summary),
            "doi": doi,
            "url": link_id or f"https://arxiv.org/abs/{aid}",
            "source": "arxiv"
        }
    except Exception:
        return None


# ------------------------ Generic URL path ------------------------

_DOI_RE = re.compile(r"\b(10\.\d{4,9}/[-._;()/:A-Z0-9]+)\b", re.I)


def _extract_doi_from_url(url: str) -> Optional[str]:
    # https://doi.org/xxx
    m = re.search(r"https?://doi\.org/([^?#\s]+)", url, re.I)
    if m:
        return m.group(1)
    return None


def _find_doi_in_html(soup: BeautifulSoup) -> Optional[str]:
    # Highwire/CSL/DC 常见位置
    for key in ["citation_doi", "dc.identifier", "dc.identifier.doi", "doi"]:
        tag = soup.find("meta", attrs={"name": key})
        if tag and tag.get("content"):
            return tag["content"].strip()
    tag = soup.find("meta", attrs={"property": "og:doi"})
    if tag and tag.get("content"):
        return tag["content"].strip()
    # 正则兜底
    m = _DOI_RE.search(soup.get_text(" ", strip=True))
    return m.group(1) if m else None


def _get_metadata_from_generic_url(url: str, contact_email: Optional[str]) -> Optional[Dict[str, Any]]:
    try:
        r = requests.get(url, headers=_headers(contact_email, accept_json=False), timeout=(8, 20))
        r.raise_for_status()
    except Exception:
        return None

    soup = BeautifulSoup(r.text, "html.parser")

    # 先尝试在 HTML 里找 DOI，再走 DOI 流程
    doi = _extract_doi_from_url(url) or _find_doi_in_html(soup)
    if doi:
        meta = _get_metadata_from_doi(doi, contact_email=contact_email)
        if meta:
            return meta

    # 否则从 Highwire/DC 元标签尽力抽取
    def _meta_first(names: List[str]) -> str:
        for n in names:
            tag = soup.find("meta", attrs={"name": n}) or soup.find("meta", attrs={"property": n})
            if tag and tag.get("content"):
                return _clean_text(tag["content"])
        return ""

    title = _meta_first(["citation_title", "dc.title", "og:title"]) or (soup.title.string.strip() if soup.title else "")
    abstract = _meta_first(["citation_abstract", "dc.description", "og:description"])
    container = _meta_first(
        ["citation_journal_title", "citation_conference_title", "prism.publicationName", "dc.source"])
    # authors: 多值
    authors = []
    for tag in soup.find_all("meta", attrs={"name": "citation_author"}):
        if tag.get("content"):
            authors.append(_clean_text(tag["content"]))
    if not authors:
        a = _meta_first(["dc.creator"])
        if a:
            authors = [a]

    # year
    pubdate = _meta_first(["citation_publication_date", "prism.publicationDate", "dc.date", "citation_date"])
    year = None
    if pubdate:
        y = re.search(r"(19|20)\d{2}", pubdate)
        year = _norm_year(y.group(0)) if y else None

    return {
        "title": title,
        "authors": authors,
        "year": year,
        "container": container,
        "abstract": abstract,
        "doi": doi or "",
        "url": url,
        "source": "html-meta"
    }


# ------------------------ Public entry ------------------------

def get_metadata(doi: Optional[str] = None, url: Optional[str] = None, contact_email: Optional[str] = None) -> Dict[
    str, Any]:
    """
    Return a normalized metadata dict:
        {title, authors, year, container, abstract, doi, url, source}
    """
    # 1) explicit DOI
    if doi:
        meta = _get_metadata_from_doi(doi, contact_email=contact_email)
        if meta:
            return meta

    # 2) URL path
    if url:
        # arXiv?
        if _extract_arxiv_id(url):
            meta = _get_metadata_from_arxiv(url)
            if meta:
                # 如果 arXiv 给出了 DOI，可进一步用 DOI 补全期刊信息（可选）
                if meta.get("doi"):
                    enriched = _get_metadata_from_doi(meta["doi"], contact_email=contact_email)
                    if enriched:
                        # 用期刊等补全，但保留 arXiv 摘要作为优先
                        enriched["abstract"] = meta["abstract"] or enriched.get("abstract", "")
                        enriched["url"] = meta["url"] or enriched.get("url", "")
                        return enriched
                return meta
        # DOI URL?
        doi2 = _extract_doi_from_url(url)
        if doi2:
            meta = _get_metadata_from_doi(doi2, contact_email=contact_email)
            if meta:
                return meta
        # generic HTML
        meta = _get_metadata_from_generic_url(url, contact_email=contact_email)
        if meta:
            return meta

    return {
        "title": "",
        "authors": [],
        "year": None,
        "container": "",
        "abstract": "",
        "doi": doi or "",
        "url": url or (f"{_DOI_BASE}{doi}" if doi else ""),
        "source": "none"
    }


# ------------------------ CLI test ------------------------
if __name__ == "__main__":
    tests = [
        {"doi": "10.1080/00051144.2025.2480423"},
        {"url": "https://doi.org/10.1038/nature14539"},
        {"url": "https://arxiv.org/abs/2510.13009"},
        # {"url": "https://arxiv.org/pdf/1706.03762.pdf"},
        # 一般网页示例（若该页含 citation_* 元标签会成功）
        # {"url": "https://openaccess.thecvf.com/content/CVPR2020/html/He_Momentum_Contrast_for_Unsupervised_Visual_Representation_Learning_CVPR_2020_paper.html"},
    ]
    for q in tests:
        print("=== Query:", q, "===")
        print(json.dumps(get_metadata(**q, contact_email="2825024660@qq.com"), ensure_ascii=False, indent=2))
