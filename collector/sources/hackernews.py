"""Hacker News — AI-related hot posts via Algolia HN Search API."""

import json
import urllib.request
import urllib.parse
from datetime import datetime, timezone

HN_SEARCH = "https://hn.algolia.com/api/v1/search_by_date"

AI_QUERIES = [
    '"artificial intelligence"',
    '"machine learning"',
    "llm",
    '"language model"',
    "gpt",
    "chatgpt",
    "claude",
    "gemini",
    '"stable diffusion"',
    '"image generation"',
    "RAG",
    "agent",
    "transformer",
    '"deep learning"',
    '"neural network"',
    "openai",
    "anthropic",
    "llama",
    "mistral",
    "copilot",
]

TAG_KW = {
    "LLM": ["llm", "gpt", "chatgpt", "language model", "llama"],
    "Agent": ["agent", "autonomous"],
    "RAG": ["rag"],
    "Vision": ["image generation", "stable diffusion", "vision"],
    "Tool": ["copilot", "tool", "cli", "sdk"],
    "Safety": ["safety", "regulation", "policy", "ban"],
    "Company": ["openai", "anthropic", "google", "meta", "microsoft"],
    "OpenSource": ["open source", "open-source", "oss"],
    "Coding": ["programming", "code", "developer", "engineer"],
    "Benchmark": ["benchmark", "eval"],
}


def fetch_hackernews():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    all_hits = []
    seen_ids = set()

    for query in AI_QUERIES[:10]:
        params = urllib.parse.urlencode(
            {
                "query": query,
                "tags": "story",
                "hitsPerPage": 15,
                "numericFilters": "points>5",
            }
        )
        url = f"{HN_SEARCH}?{params}"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "AI-Daily-Digest/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as e:
            print(f"[HN] Failed query '{query}': {e}")
            continue

        for hit in data.get("hits", []):
            object_id = hit.get("objectID", "")
            if object_id in seen_ids:
                continue
            seen_ids.add(object_id)

            title = hit.get("title", "").replace("\n", " ").strip()
            url = hit.get("url") or f"https://news.ycombinator.com/item?id={object_id}"
            points = hit.get("points", 0) or 0
            num_comments = hit.get("num_comments", 0) or 0

            tags = []
            title_lower = title.lower()
            for tag, keywords in TAG_KW.items():
                for kw in keywords:
                    if kw.lower() in title_lower:
                        tags.append(tag)
                        break

            all_hits.append(
                {
                    "title": title,
                    "summary": "",
                    "url": url,
                    "source": "hackernews",
                    "source_label": "Hacker News",
                    "tags": tags[:4],
                    "stars": points,
                    "date": today,
                    "authors": "",
                    "language": "en",
                    "hot_score": 0,
                }
            )

    all_hits.sort(key=lambda h: h["stars"], reverse=True)
    return all_hits[:20]
