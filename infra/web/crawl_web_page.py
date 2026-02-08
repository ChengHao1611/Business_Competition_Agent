from __future__ import annotations

import ipaddress
import logging
import os
import re
import socket
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from core.ports.web_fetcher import WebFetcher

logger = logging.getLogger(__name__)


class FetchError(Exception):
    pass


def _is_private_ip(hostname: str) -> bool:
    try:
        ip = socket.gethostbyname(hostname)
        addr = ipaddress.ip_address(ip)
        return (
            addr.is_private
            or addr.is_loopback
            or addr.is_link_local
            or addr.is_multicast
            or addr.is_reserved
        )
    except Exception:
        return True


def _normalize_whitespace(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def fetch_page_text(
    url: str,
    *,
    timeout_s: int = 15,
    max_bytes: int = 2_000_000,
    max_chars: int = 40_000,
    user_agent: str = "proposal-agent/1.0",
) -> dict:
    p = urlparse(url)
    if p.scheme not in ("http", "https") or not p.hostname:
        raise FetchError("invalid url")
    if _is_private_ip(p.hostname):
        raise FetchError("blocked private hostname")

    headers = {"User-Agent": user_agent, "Accept": "text/html,*/*"}
    r = requests.get(url, headers=headers, timeout=timeout_s, stream=True, allow_redirects=True)

    content = b""
    size = 0
    for chunk in r.iter_content(chunk_size=65536):
        if not chunk:
            continue
        size += len(chunk)
        if size > max_bytes:
            raise FetchError("content too large")
        content += chunk

    html = content.decode(r.encoding or "utf-8", errors="replace")
    soup = BeautifulSoup(html, "html.parser")

    for tag in soup(["script", "style", "noscript", "svg", "canvas"]):
        tag.decompose()

    title = soup.title.get_text(strip=True) if soup.title else None
    text = soup.get_text(separator=" ", strip=True)
    text = _normalize_whitespace(text)[:max_chars]

    return {
        "ok": True,
        "url": r.url,
        "title": title,
        "text": text,
    }


def search_competition_with_serpapi(
    competition_name: str,
    *,
    num_results: int = 10,
) -> dict:
    api_key = os.getenv("SERPAPI_API_KEY")
    if not api_key:
        raise RuntimeError("SERPAPI_API_KEY not set")

    if not competition_name or not isinstance(competition_name, str):
        raise ValueError("competition_name must be a non-empty string")

    params = {
        "engine": "google",
        "q": competition_name,
        "hl": "zh-TW",
        "num": num_results,
        "api_key": api_key,
    }

    resp = requests.get("https://serpapi.com/search", params=params, timeout=20)
    data = resp.json()

    organic = data.get("organic_results", [])
    picked_urls = []
    seen_domains = set()

    for item in organic:
        link = item.get("link")
        if not link:
            continue
        p = urlparse(link)
        if p.scheme not in ("http", "https") or not p.hostname:
            continue
        if _is_private_ip(p.hostname):
            continue
        domain = p.hostname.lower()
        if domain in seen_domains:
            continue
        seen_domains.add(domain)
        picked_urls.append(link)
        if len(picked_urls) == 2:
            break

    pages = []
    for url in picked_urls:
        try:
            pages.append(fetch_page_text(url))
        except Exception as e:
            logger.exception("爬取網頁失敗: %s", url)
            pages.append({"ok": False, "url": url, "error": str(e), "text": ""})

    return {
        "ok": True,
        "competition_name": competition_name,
        "picked_urls": picked_urls,
        "pages": pages,
        "serpapi_meta": {
            "search_engine": "google",
            "total_results": data.get("search_information", {}).get("total_results"),
        },
    }


class SerpApiWebFetcher(WebFetcher):
    def fetch_page_text(self, url: str) -> dict:
        return fetch_page_text(url)

    def search_competition(self, competition_name: str, num_results: int = 10) -> dict:
        return search_competition_with_serpapi(competition_name, num_results=num_results)

