#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：python-note 
@File    ：get_paper_meta.py
@IDE     ：PyCharm 
@Author  ：wei liyu
@Date    ：2025/10/16 22:18 
'''
import requests
from bs4 import BeautifulSoup
import re
import json

# Crossref API 基础 URL
CROSSREF_API = "https://api.crossref.org/works/"


# 获取 DOI 文章的元数据
def get_metadata_from_doi(doi):
    url = f"{CROSSREF_API}{doi}"
    headers = {
        "User-Agent": "Python Script (contact: your-email@example.com)"
    }
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        data = response.json()
        item = data['message']

        # 提取字段
        title = item.get("title", ["Unknown"])[0]
        authors = [author['given'] + " " + author['family'] for author in item.get("author", [])]
        year = item.get("issued", {}).get("date-parts", [[None]])[0][0]
        container = item.get("container-title", ["Unknown"])[0]
        abstract = item.get("abstract", "No abstract available")
        url = item.get("URL", "No URL available")

        return {
            "title": title,
            "authors": authors,
            "year": year,
            "container": container,
            "abstract": abstract,
            "doi": doi,
            "url": url
        }

    except requests.exceptions.RequestException as e:
        print(f"Error fetching metadata for DOI {doi}: {e}")
        return None


# 从 DOI 网址获取 DOI
def get_doi_from_url(url):
    if "doi.org" in url:
        match = re.search(r"doi.org/([^\s]+)", url)
        if match:
            return match.group(1)
    return None


# 获取文献网页的摘要
def get_abstract_from_url(url):
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # 在HTML中寻找可能的摘要
        abstract_tag = soup.find('meta', attrs={'name': 'description'})
        if abstract_tag:
            return abstract_tag.get('content')
        # 如果找不到，返回页面标题
        return soup.title.string if soup.title else "No abstract found"
    except requests.exceptions.RequestException as e:
        print(f"Error fetching URL {url}: {e}")
        return None


# 综合处理 DOI 或 URL
def get_metadata(doi=None, url=None):
    if doi:
        metadata = get_metadata_from_doi(doi)
        if metadata:
            return metadata
    if url:
        doi = get_doi_from_url(url)
        if doi:
            metadata = get_metadata_from_doi(doi)
            if metadata:
                return metadata
        abstract = get_abstract_from_url(url)
        return {
            "title": "Unknown",
            "authors": ["Unknown"],
            "year": "Unknown",
            "container": "Unknown",
            "abstract": abstract,
            "doi": doi,
            "url": url
        }
    return None


# 测试示例
if __name__ == "__main__":
    doi = "10.1002/widm.70024"  # 输入一个 DOI 进行测试
    url = "https://www.tandfonline.com/doi/full/10.1080/00051144.2025.2480423"  # 或者输入文献的网址

    metadata = get_metadata(doi=doi)
    # metadata = get_doi_from_url(url)
    if metadata:
        print(json.dumps(metadata, indent=4))
    else:
        print("Metadata not found.")
