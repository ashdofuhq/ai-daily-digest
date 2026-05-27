"""Hugging Face Daily Papers — scrape the daily papers page."""

import ssl
import json
import urllib.request
import re
from datetime import datetime, timezone

_SSL = ssl.create_default_context()
try:
    _SSL = ssl._create_unverified_context()
except AttributeError:
    pass

HF_DAILY = "https://huggingface.co/papers"

TAG_KW = {
    "LLM": ["llm", "language model", "gpt", "transformer", "chatgpt"],
    "RAG": ["rag", "retrieval augmented"],
    "Agent": ["agent", "multi-agent", "tool"],
    "Vision": ["vision", "image", "visual", "multimodal", "vlm"],
    "RL": ["reinforcement learning", "rlhf", "dpo", "reward"],
    "Diffusion": ["diffusion", "image generation"],
    "Safety": ["safety", "alignment", "bias", "fairness"],
    "Benchmark": ["benchmark", "leaderboard"],
    "Code": ["code", "programming"],
    "Reasoning": ["reasoning", "chain-of-thought"],
    "Training": ["fine-tun", "pretrain", "training", "lora"],
    "Dataset": ["dataset", "corpus", "data"],
    "Multimodal": ["multimodal", "vision-language"],
    "Speech": ["speech", "tts", "voice"],
}


def fetch_huggingface():
    try:
        req = urllib.request.Request(
            HF_DAILY,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
        )
        with urllib.request.urlopen(req, timeout=30, context=_SSL) as resp:
            html = resp.read().decode("utf-8")
    except Exception as e:
        print(f"[HuggingFace] Failed to fetch: {e}")
        return []

    # Try to extract papers from the Next.js data payload
    papers = []
    script_pattern = re.compile(
        r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>', re.DOTALL
    )
    script_match = script_pattern.search(html)
    if script_match:
        try:
            data = json.loads(script_match.group(1))
            props = data.get("props", {}).get("pageProps", {})
            daily_papers = props.get("dailyPapers", [])
            for p in daily_papers:
                paper_data = p.get("paper", p)
                papers.append(
                    {
                        "title": paper_data.get("title", ""),
                        "url": f"https://huggingface.co/papers/{paper_data.get('id', '')}",
                        "upvotes": p.get("upvotes", 0),
                    }
                )
        except (json.JSONDecodeError, KeyError) as e:
            print(f"[HF] JSON parse error: {e}")

    if not papers:
        pattern = re.compile(
            r'<article[^>]*>.*?<a[^>]*href="(/papers/[^"]+)"[^>]*>(.*?)</a>',
            re.DOTALL,
        )
        for url_path, raw_title in pattern.findall(html):
            title = re.sub(r"<[^>]+>", "", raw_title).strip()
            if title and url_path:
                papers.append(
                    {"title": title, "url": f"https://huggingface.co{url_path}", "upvotes": 0}
                )

    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    results = []

    for item in papers[:20]:
        title = item["title"]
        tags = []
        title_lower = title.lower()
        for tag, keywords in TAG_KW.items():
            for kw in keywords:
                if kw.lower() in title_lower:
                    tags.append(tag)
                    break

        results.append(
            {
                "title": title,
                "summary": "",
                "url": item["url"],
                "source": "huggingface",
                "source_label": "HuggingFace",
                "tags": tags[:4],
                "stars": item.get("upvotes", 0),
                "date": today,
                "authors": "",
                "language": "en",
                "hot_score": 0,
            }
        )

    return results[:20]
