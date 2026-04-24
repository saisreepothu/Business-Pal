from datetime import datetime, timedelta
from typing import Optional

import streamlit as st
from serpapi.google_search import GoogleSearch
from tenacity import retry, stop_after_attempt, wait_exponential

from config.settings import SERPAPI_API_KEY, WEB_CACHE_TTL_HOURS, WEB_CACHE_MAX_SIZE


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), reraise=True)
def _execute_search(params: dict) -> dict:
    return GoogleSearch(params).get_dict()


def search_web(query: str) -> str:
    cache_key = query[:100]
    cached = st.session_state.web_cache.get(cache_key)

    if cached and datetime.now() - cached["timestamp"] < timedelta(hours=WEB_CACHE_TTL_HOURS):
        return cached["results"]

    params = {
        "q": query,
        "api_key": SERPAPI_API_KEY,
        "engine": "google",
        "num": 5,
    }

    try:
        results = _execute_search(params)
    except Exception:
        return ""

    web_context = []
    for item in results.get("organic_results", []):
        title = item.get("title", "Untitled")
        link = item.get("link", "#")
        snippet = item.get("snippet", "No description available")
        web_context.append(f"### {title}\n**Source**: [{link}]({link})\n{snippet}\n")

    web_content = "\n".join(web_context)

    # Evict oldest entry when cache is full
    if len(st.session_state.web_cache) >= WEB_CACHE_MAX_SIZE:
        oldest = min(
            st.session_state.web_cache,
            key=lambda k: st.session_state.web_cache[k]["timestamp"],
        )
        del st.session_state.web_cache[oldest]

    st.session_state.web_cache[cache_key] = {
        "results": web_content,
        "timestamp": datetime.now(),
    }
    return web_content
