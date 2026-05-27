"""Arxiv API — fetch recent papers from cs.AI, cs.LG, cs.CL, cs.CV."""

import ssl
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET

_SSL = ssl.create_default_context()
try:
    _SSL = ssl._create_unverified_context()
except AttributeError:
    pass
from datetime import datetime, timedelta, timezone

ARXIV_API = "http://export.arxiv.org/api/query"
CATEGORIES = ["cs.AI", "cs.LG", "cs.CL", "cs.CV"]
MAX_RESULTS = 50

# Tags derived from paper title/abstract keywords
TAG_KW = {
    "LLM": ["large language model", "llm", "gpt", "transformer", "chatgpt"],
    "RAG": ["retrieval augmented", "rag", "retrieval-augmented"],
    "Agent": ["agent", "multi-agent", "tool use", "function calling"],
    "Vision": ["vision", "image", "visual", "multimodal", "vlm"],
    "RL": ["reinforcement learning", "rlhf", "dpo", "rl", "reward model"],
    "Diffusion": ["diffusion", "stable diffusion", "dalle"],
    "Safety": ["safety", "alignment", "jailbreak", "harmful", "bias"],
    "Embodied": ["robot", "embodied", "manipulation"],
    "Code": ["code generation", "program synthesis", "software engineering"],
    "Science": ["drug", "protein", "molecule", "climate", "physics"],
    "Audio": ["speech", "audio", "voice", "music"],
    "Video": ["video generation", "video understanding"],
    "Eval": ["benchmark", "evaluation", "eval"],
    "Reasoning": ["reasoning", "chain-of-thought", "cot", "planning"],
    "Training": ["fine-tun", "pretrain", "training", "lora", "qlora"],
}


def _get_tags(title, summary):
    title_lower = title.lower()
    summary_lower = (summary or "").lower()
    combined = title_lower + " " + summary_lower
    tags = []
    for tag, keywords in TAG_KW.items():
        for kw in keywords:
            if kw.lower() in combined:
                tags.append(tag)
                break
    return tags[:5]


def fetch_arxiv():
    today = datetime.now(timezone.utc)
    yesterday = today - timedelta(days=2)

    papers = []
    for cat in CATEGORIES:
        params = urllib.parse.urlencode(
            {
                "search_query": f"cat:{cat}",
                "sortBy": "submittedDate",
                "sortOrder": "descending",
                "start": 0,
                "max_results": 50,
            }
        )
        url = f"{ARXIV_API}?{params}"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "AI-Daily-Digest/1.0"})
            with urllib.request.urlopen(req, timeout=30, context=_SSL) as resp:
                data = resp.read().decode("utf-8")
        except Exception as e:
            print(f"[Arxiv] Failed to fetch {cat}: {e}")
            continue

        root = ET.fromstring(data)
        ns = {
            "atom": "http://www.w3.org/2005/Atom",
            "arxiv": "http://arxiv.org/schemas/atom",
        }

        for entry in root.findall("atom:entry", ns):
            title_el = entry.find("atom:title", ns)
            summary_el = entry.find("atom:summary", ns)
            link_el = entry.find("atom:link", ns)
            published_el = entry.find("atom:published", ns)
            authors = entry.findall("atom:author", ns)

            title = title_el.text.strip().replace("\n", " ") if title_el is not None else ""
            summary = (
                summary_el.text.strip().replace("\n", " ")[:300] if summary_el is not None else ""
            )
            url = link_el.attrib.get("href", "") if link_el is not None else ""
            published = published_el.text[:10] if published_el is not None else ""
            author_names = [
                a.find("atom:name", ns).text for a in authors if a.find("atom:name", ns) is not None
            ]

            papers.append(
                {
                    "title": title,
                    "summary": summary,
                    "url": url,
                    "source": "arxiv",
                    "source_label": "Arxiv",
                    "tags": _get_tags(title, summary),
                    "stars": 0,
                    "date": published or today.strftime("%Y-%m-%d"),
                    "authors": ", ".join(author_names[:3]),
                    "language": "en",
                    "hot_score": 0,
                }
            )

    papers.sort(key=lambda p: p["date"], reverse=True)
    return papers[:MAX_RESULTS]
