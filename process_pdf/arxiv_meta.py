#!/usr/bin/env python
# -*- coding: UTF-8 -*-
'''
@Project ：python-note 
@File    ：arxiv_meta.py
@IDE     ：PyCharm 
@Author  ：wei liyu
@Date    ：2025/10/16 22:45 
'''
import requests
from bs4 import BeautifulSoup
import re
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def extract_arxiv_paper_info(arxiv_url: str) -> dict:
    """
    从 arXiv 论文 URL 解析论文信息

    参数:
    arxiv_url (str): arXiv 论文的 URL，例如 https://arxiv.org/abs/2305.12345

    返回:
    dict: 包含论文标题、摘要和正文的字典
    """
    # 确保 URL 是有效的 arXiv URL
    if "arxiv.org" not in arxiv_url:
        raise ValueError("Invalid arXiv URL. Must contain 'arxiv.org'")

    # 如果是摘要页面，转换为 PDF 页面
    if "abs" in arxiv_url:
        paper_id = arxiv_url.split("/")[-1]
        pdf_url = f"https://arxiv.org/pdf/{paper_id}.pdf"
    else:
        pdf_url = arxiv_url

    # 使用 Jina AI Reader 解析 PDF
    reader_url = f"https://r.jina.ai/{pdf_url}"

    logger.info(f"Fetching paper from: {reader_url}")

    try:
        # 获取解析后的 HTML
        response = requests.get(reader_url, timeout=30)
        response.raise_for_status()
        html_content = response.text
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching paper: {e}")
        return None

    # 使用 BeautifulSoup 解析 HTML
    soup = BeautifulSoup(html_content, 'html.parser')

    # 提取标题
    title = None
    title_element = soup.find('h1', class_='title')
    if title_element:
        title = title_element.text.strip()
    else:
        # 尝试从 meta 标签中提取
        meta_title = soup.find('meta', property='og:title')
        if meta_title and 'content' in meta_title.attrs:
            title = meta_title['content'].strip()

    # 提取摘要
    abstract = None
    abstract_element = soup.find('div', class_='abstract')
    if abstract_element:
        abstract = abstract_element.text.strip().replace("Abstract", "").strip()

    # 提取正文
    content = []
    # 查找所有段落
    for p in soup.find_all('p'):
        text = p.text.strip()
        # 跳过页脚、页眉和不相关的文本
        if text and not re.search(r"arXiv:\d{4}\.\d{5}", text) and not text.startswith('arXiv'):
            # 跳过非常短的文本（可能是页码、图表编号等）
            if len(text) > 15:
                content.append(text)

    # 清理内容
    content = [line for line in content if len(line) > 10]

    # 如果没有找到正文，尝试获取更多内容
    if not content:
        for div in soup.find_all('div'):
            text = div.text.strip()
            if text and not re.search(r"arXiv:\d{4}\.\d{5}", text):
                content.append(text)

    return {
        'title': title,
        'abstract': abstract,
        'content': '\n'.join(content)
    }


def print_paper_summary(paper_info: dict):
    """打印论文摘要信息"""
    if not paper_info:
        print("无法获取论文信息")
        return

    print(f"论文标题: {paper_info['title']}")
    print(f"摘要: {paper_info['abstract']}")

    print("\n正文摘要 (前500字符):")
    print(paper_info['content'][:500] + "..." if len(paper_info['content']) > 500 else paper_info['content'])


if __name__ == "__main__":
    # 示例：解析一篇 arXiv 论文
    arxiv_url = "https://arxiv.org/abs/2510.13009"  # 替换为实际的 arXiv URL

    try:
        paper_info = extract_arxiv_paper_info(arxiv_url)
        print_paper_summary(paper_info)
    except Exception as e:
        print(f"处理论文时出错: {e}")