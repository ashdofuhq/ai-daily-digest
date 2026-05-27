"""GitHub Trending — AI/ML repositories via GitHub trending page."""

import json
import urllib.request
import re
from datetime import datetime, timezone

GH_TRENDING = "https://github.com/trending?since=daily"
AI_TOPICS = {
    "ai", "machine-learning", "deep-learning", "llm", "gpt", "transformer",
    "neural-network", "nlp", "natural-language-processing", "computer-vision",
    "reinforcement-learning", "generative-ai", "stable-diffusion", "langchain",
    "rag", "agent", "llama", "openai", "anthropic", "chatbot", "embedding",
    "vector-database", "mlops", "tensorflow", "pytorch", "jax",
}

TAG_KW = {
    "LLM": ["llm", "gpt", "chatgpt", "language model", "llama"],
    "Agent": ["agent", "autonomous", "multi-agent"],
    "RAG": ["rag", "retrieval"],
    "Vision": ["vision", "image", "visual", "multimodal", "vlm"],
    "Tool": ["framework", "library", "sdk", "tool"],
    "MCP": ["mcp", "model context protocol"],
    "Code": ["code", "programming", "copilot"],
    "Training": ["finetune", "pretrain", "training", "lora"],
    "Inference": ["inference", "vllm", "tensorrt", "onnx"],
    "Safety": ["safety", "guardrail", "alignment"],
}


def _parse_trending(html):
    results = []
    repo_pattern = re.compile(
        r'<h2[^>]*class="[^"]*h3[^"]*lh-condensed[^"]*"[^>]*>.*?<a[^>]*href="/([^/"]+/[^/"]+)"[^>]*>(.*?)</a>.*?<p[^>]*class="[^"]*col-9[^"]*"[^>]*>(.*?)</p>',
        re.DOTALL,
    )
    star_pattern = re.compile(
        r'<span[^>]*class="[^"]*d-inline-block[^"]*float-sm-right[^"]*"[^>]*>(.*?)</span>',
        re.DOTALL,
    )

    repos = repo_pattern.findall(html)
    stars = star_pattern.findall(html)

    for i, (repo_path, _, desc) in enumerate(repos):
        desc_clean = re.sub(r"<[^>]+>", "", desc).strip()
        star_count = 0
        if i < len(stars):
            star_str = re.sub(r"<[^>]+>", "", stars[i]).strip().replace(",", "")
            try:
                star_count = int(star_str)
            except ValueError:
                pass

        results.append(
            {
                "repo": repo_path,
                "description": desc_clean,
                "stars": star_count,
            }
        )
    return results


def fetch_github():
    try:
        req = urllib.request.Request(
            GH_TRENDING,
            headers={"User-Agent": "Mozilla/5.0", "Accept": "text/html"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8")
    except Exception as e:
        print(f"[GitHub] Failed to fetch trending: {e}")
        return []

    repos = _parse_trending(html)
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    papers = []

    for r in repos:
        desc_lower = r["description"].lower() + " " + r["repo"].lower()
        if not any(topic in desc_lower for topic in AI_TOPICS):
            continue

        tags = []
        for tag, keywords in TAG_KW.items():
            for kw in keywords:
                if kw.lower() in desc_lower:
                    tags.append(tag)
                    break

        papers.append(
            {
                "title": r["repo"],
                "summary": r["description"][:300],
                "url": f"https://github.com/{r['repo']}",
                "source": "github",
                "source_label": "GitHub",
                "tags": tags[:4],
                "stars": r["stars"],
                "date": today,
                "authors": "",
                "language": "en",
                "hot_score": 0,
            }
        )

    papers.sort(key=lambda p: p["stars"], reverse=True)
    return papers[:25]
