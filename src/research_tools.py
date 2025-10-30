"""
研究工具模块 - 提供学术搜索和文档处理功能
本模块包含：
1. arXiv 学术论文搜索工具
2. Tavily 网络搜索工具
3. Wikipedia 百科搜索工具
4. PDF 下载和文本提取工具
"""

from typing import List, Dict, Optional
import os, re, time
import requests
import xml.etree.ElementTree as ET
from io import BytesIO

# ----- 带重试和请求头的会话配置 -----
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


def _build_session(
    user_agent: str = "LF-ADP-Agent/1.0 (mailto:your.email@example.com)",
) -> requests.Session:
    """
    构建带有重试机制的 HTTP 会话
    
    参数:
        user_agent: 用户代理字符串
    
    返回:
        配置好的 requests.Session 对象
    """
    s = requests.Session()
    # 设置请求头
    s.headers.update(
        {
            "User-Agent": user_agent,
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }
    )
    # 配置重试策略
    retry = Retry(
        total=5,  # 总共重试5次
        connect=5,  # 连接重试5次
        read=5,  # 读取重试5次
        backoff_factor=0.6,  # 退避因子
        status_forcelist=(429, 500, 502, 503, 504),  # 需要重试的状态码
        allowed_methods=frozenset(["GET", "HEAD"]),  # 允许重试的方法
        raise_on_redirect=False,
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_maxsize=20)
    s.mount("https://", adapter)
    s.mount("http://", adapter)
    return s


# 创建全局会话对象
session = _build_session()


# ----- 工具函数 -----
def ensure_pdf_url(abs_or_pdf_url: str) -> str:
    """
    确保 URL 指向 PDF 文件
    将 arXiv 摘要页面 URL 转换为 PDF URL
    
    参数:
        abs_or_pdf_url: arXiv 摘要或 PDF URL
    
    返回:
        PDF 文件的 URL
    """
    url = abs_or_pdf_url.strip().replace("http://", "https://")
    if "/pdf/" in url and url.endswith(".pdf"):
        return url
    url = url.replace("/abs/", "/pdf/")
    if not url.endswith(".pdf"):
        url += ".pdf"
    return url


def _safe_filename(name: str) -> str:
    """
    生成安全的文件名，移除特殊字符
    
    参数:
        name: 原始文件名
    
    返回:
        安全的文件名
    """
    import re

    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name)
    if not name.lower().endswith(".pdf"):
        name += ".pdf"
    return name


def clean_text(s: str) -> str:
    """
    清理文本，移除多余的空白和换行
    
    参数:
        s: 原始文本
    
    返回:
        清理后的文本
    """
    s = re.sub(r"-\n", "", s)  # "transfor-\nmers" -> "transformers"
    s = re.sub(r"\r\n|\r", "\n", s)  # 标准化换行符
    s = re.sub(r"[ \t]+", " ", s)  # 合并多个空格
    s = re.sub(r"\n{3,}", "\n\n", s)  # 最多保留一个空行
    return s.strip()


def fetch_pdf_bytes(pdf_url: str, timeout: int = 90) -> bytes:
    """
    下载 PDF 文件并返回字节内容
    
    参数:
        pdf_url: PDF 文件的 URL
        timeout: 超时时间（秒）
    
    返回:
        PDF 文件的字节内容
    """
    r = session.get(pdf_url, timeout=timeout, allow_redirects=True)
    r.raise_for_status()
    return r.content


def pdf_bytes_to_text(pdf_bytes: bytes, max_pages: Optional[int] = None) -> str:
    """
    从 PDF 字节内容中提取文本
    优先使用 PyMuPDF，失败则使用 pdfminer.six
    
    参数:
        pdf_bytes: PDF 文件的字节内容
        max_pages: 最多提取的页数（None 表示全部）
    
    返回:
        提取的文本内容
    """
    # 1) 尝试使用 PyMuPDF
    try:
        import fitz  # PyMuPDF

        out = []
        with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
            n = len(doc)
            limit = n if max_pages is None else min(max_pages, n)
            for i in range(limit):
                out.append(doc.load_page(i).get_text("text"))
        return "\n".join(out)
    except Exception:
        pass

    # 2) 回退到 pdfminer.six
    try:
        from pdfminer.high_level import extract_text_to_fp

        buf_in = BytesIO(pdf_bytes)
        buf_out = BytesIO()
        extract_text_to_fp(buf_in, buf_out)
        return buf_out.getvalue().decode("utf-8", errors="ignore")
    except Exception as e:
        raise RuntimeError(f"PDF 文本提取失败: {e}")


def maybe_save_pdf(pdf_bytes: bytes, dest_dir: str, filename: str) -> str:
    """
    将 PDF 字节内容保存到文件
    
    参数:
        pdf_bytes: PDF 文件的字节内容
        dest_dir: 目标目录
        filename: 文件名
    
    返回:
        保存的文件路径
    """
    os.makedirs(dest_dir, exist_ok=True)
    path = os.path.join(dest_dir, _safe_filename(filename))
    with open(path, "wb") as f:
        f.write(pdf_bytes)
    return path


# ----- arXiv 搜索工具 -----
from typing import List, Dict
import time, requests, xml.etree.ElementTree as ET
from io import BytesIO


def arxiv_search_tool(
    query: str,
    max_results: int = 3,
) -> List[Dict]:
    """
    在 arXiv 上搜索学术论文，并提取 PDF 全文
    
    参数:
        query: 搜索关键词
        max_results: 最多返回的结果数（默认: 3）
    
    返回:
        包含论文信息的字典列表，每个字典包含：
        - title: 论文标题
        - authors: 作者列表
        - published: 发布日期
        - url: 摘要页面 URL
        - summary: 提取的 PDF 文本（或原始摘要）
        - link_pdf: PDF 文件 URL
    """
    # ===== 内部配置标志 =====
    _INCLUDE_PDF = True  # 是否包含 PDF
    _EXTRACT_TEXT = True  # 是否提取文本
    _MAX_PAGES = 6  # 最多提取的页数
    _TEXT_CHARS = 5000  # 文本字符数限制
    _SAVE_FULL_TEXT = False  # 是否保存完整文本
    _SLEEP_SECONDS = 1.0  # 请求间隔（秒）
    # ==========================

    # 构建 arXiv API 查询 URL
    api_url = (
        "https://export.arxiv.org/api/query"
        f"?search_query=all:{requests.utils.quote(query)}&start=0&max_results={max_results}"
    )

    out: List[Dict] = []
    try:
        resp = session.get(api_url, timeout=60)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        return [{"error": f"arXiv API 请求失败: {e}"}]

    try:
        # 解析 XML 响应
        root = ET.fromstring(resp.content)
        ns = {"atom": "http://www.w3.org/2005/Atom"}

        # 遍历每个搜索结果
        for entry in root.findall("atom:entry", ns):
            # 提取基本信息
            title = (
                entry.findtext("atom:title", default="", namespaces=ns) or ""
            ).strip()
            published = (
                entry.findtext("atom:published", default="", namespaces=ns) or ""
            )[:10]
            url_abs = entry.findtext("atom:id", default="", namespaces=ns) or ""
            # 原始摘要
            abstract_summary = (
                entry.findtext("atom:summary", default="", namespaces=ns) or ""
            ).strip()

            # 提取作者列表
            authors = []
            for a in entry.findall("atom:author", ns):
                nm = a.findtext("atom:name", default="", namespaces=ns)
                if nm:
                    authors.append(nm)

            # 查找 PDF 链接
            link_pdf = None
            for link in entry.findall("atom:link", ns):
                if link.attrib.get("title") == "pdf":
                    link_pdf = link.attrib.get("href")
                    break
            if not link_pdf and url_abs:
                link_pdf = ensure_pdf_url(url_abs)

            # 构建结果项
            item = {
                "title": title,
                "authors": authors,
                "published": published,
                "url": url_abs,
                "summary": abstract_summary,
                "link_pdf": link_pdf,
            }

            # 下载 PDF（如果需要）
            pdf_bytes = None
            if (_INCLUDE_PDF or _EXTRACT_TEXT) and link_pdf:
                try:
                    pdf_bytes = fetch_pdf_bytes(link_pdf, timeout=90)
                    time.sleep(_SLEEP_SECONDS)  # 避免请求过快
                except Exception as e:
                    item["pdf_error"] = f"PDF 下载失败: {e}"

            # 提取 PDF 文本（如果需要）
            if _EXTRACT_TEXT and pdf_bytes:
                try:
                    text = pdf_bytes_to_text(pdf_bytes, max_pages=_MAX_PAGES)
                    text = clean_text(text) if text else ""
                    if text:
                        if _SAVE_FULL_TEXT:
                            item["summary"] = text  # 保存完整文本
                        else:
                            item["summary"] = text[:_TEXT_CHARS]  # 截断文本
                except Exception as e:
                    item["text_error"] = f"文本提取失败: {e}"

            out.append(item)
        return out
    except ET.ParseError as e:
        return [{"error": f"arXiv API XML 解析失败: {e}"}]
    except Exception as e:
        return [{"error": f"意外错误: {e}"}]


# ---- arXiv 工具定义 ----
arxiv_tool_def = {
    "type": "function",
    "function": {
        "name": "arxiv_search_tool",
        "description": "在 arXiv 上搜索学术论文，并（内部）下载 PDF 到内存并提取文本。",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "搜索关键词。"},
                "max_results": {"type": "integer", "default": 3},
            },
            "required": ["query"],
        },
    },
}


## ----- Tavily 网络搜索工具 -----


import os
from dotenv import load_dotenv
from tavily import TavilyClient

load_dotenv()  # 从 .env 文件加载环境变量


def tavily_search_tool(
    query: str, max_results: int = 5, include_images: bool = False
) -> list[dict]:
    """
    使用 Tavily API 执行网络搜索
    
    参数:
        query: 搜索查询
        max_results: 返回的结果数量（默认: 5）
        include_images: 是否包含图片结果
    
    返回:
        包含搜索结果的字典列表，每个字典包含 'title'、'content' 和 'url' 键
    """
    api_key = os.getenv("TAVILY_API_KEY")
    if not api_key:
        raise ValueError("环境变量中未找到 TAVILY_API_KEY。")

    client = TavilyClient(api_key, api_base_url=os.getenv("DLAI_TAVILY_BASE_URL"))

    try:
        # 执行搜索
        response = client.search(
            query=query, max_results=max_results, include_images=include_images
        )

        # 处理搜索结果
        results = []
        for r in response.get("results", []):
            results.append(
                {
                    "title": r.get("title", ""),
                    "content": r.get("content", ""),
                    "url": r.get("url", ""),
                }
            )

        # 如果需要，添加图片结果
        if include_images:
            for img_url in response.get("images", []):
                results.append({"image_url": img_url})

        return results

    except Exception as e:
        return [{"error": str(e)}]  # 返回友好的错误信息


tavily_tool_def = {
    "type": "function",
    "function": {
        "name": "tavily_search_tool",
        "description": "使用 Tavily API 执行通用网络搜索。",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "从网络检索信息的搜索关键词。",
                },
                "max_results": {
                    "type": "integer",
                    "description": "返回的最大结果数。",
                    "default": 5,
                },
                "include_images": {
                    "type": "boolean",
                    "description": "是否包含图片结果。",
                    "default": False,
                },
            },
            "required": ["query"],
        },
    },
}

## ----- Wikipedia 搜索工具 -----

from typing import List, Dict
import wikipedia


def wikipedia_search_tool(query: str, sentences: int = 5) -> List[Dict]:
    """
    在 Wikipedia 上搜索给定查询的摘要
    
    参数:
        query: Wikipedia 搜索查询
        sentences: 摘要中包含的句子数
    
    返回:
        包含单个字典的列表，字典包含 title、summary 和 url
    """
    try:
        # 搜索并获取第一个结果
        page_title = wikipedia.search(query)[0]
        page = wikipedia.page(page_title)
        summary = wikipedia.summary(page_title, sentences=sentences)

        return [{"title": page.title, "summary": summary, "url": page.url}]
    except Exception as e:
        return [{"error": str(e)}]


# Wikipedia 工具定义
wikipedia_tool_def = {
    "type": "function",
    "function": {
        "name": "wikipedia_search_tool",
        "description": "通过查询字符串搜索 Wikipedia 文章摘要。",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Wikipedia 文章的搜索关键词。",
                },
                "sentences": {
                    "type": "integer",
                    "description": "摘要中的句子数量。",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
    },
}


# 工具映射字典 - 将工具名称映射到对应的函数
tool_mapping = {
    "tavily_search_tool": tavily_search_tool,
    "arxiv_search_tool": arxiv_search_tool,
    "wikipedia_search_tool": wikipedia_search_tool,
}
