"""Deduplication and learning score calculation."""

import hashlib
import re
from difflib import SequenceMatcher

# 来源学习价值：有代码能跑 > 讨论能看懂 > 纯论文
SOURCE_SCORES = {
    "github": 1.0,          # 开源仓库，直接能跑代码 — 最适合学习
    "hackernews": 0.85,     # 社区讨论，真实场景 — 能看懂别人的思路
    "paperswithcode": 0.65, # 论文+代码 — 有理论有实践
    "huggingface": 0.5,     # 论文精选 — 部分有 demo
    "arxiv": 0.3,           # 纯学术论文 — 门槛最高
}

# 实用标签加分：越接近"能动手做"越高
TAG_BONUS = {
    "Agent": 1.0,
    "LLM": 1.0,
    "RAG": 0.95,
    "Code": 0.95,
    "Tool": 0.9,
    "MCP": 0.9,
    "OpenSource": 0.85,
    "Training": 0.8,
    "Coding": 0.75,
    "Safety": 0.6,
    "Inference": 0.6,
    "Benchmark": 0.5,
    "Dataset": 0.5,
    "Reasoning": 0.5,
    "Vision": 0.4,
    "Diffusion": 0.4,
    "Multimodal": 0.4,
    "RL": 0.35,
    "Audio": 0.3,
    "Speech": 0.3,
    "Company": 0.3,
    "Drug": 0.2,
    "Science": 0.2,
    "GAN": 0.2,
    "Graph": 0.2,
    "Embodied": 0.2,
    "NLP": 0.5,
    "Eval": 0.5,
    "Video": 0.3,
}


def _make_id(item):
    raw = (item.get("url", "") + item.get("title", "") + item.get("date", ""))
    return hashlib.md5(raw.encode("utf-8")).hexdigest()[:12]


def _normalize_title(title):
    t = title.lower()
    t = re.sub(r"[^a-z0-9\s]", "", t)
    t = re.sub(r"\s+", " ", t).strip()
    return t


def _similar(a, b, threshold=0.82):
    return SequenceMatcher(None, _normalize_title(a), _normalize_title(b)).ratio() >= threshold


def _compute_learning_score(item, max_stars=1):
    # 1. 来源分（40%）— 有代码 > 有讨论 > 纯论文
    source_s = SOURCE_SCORES.get(item["source"], 0.4)

    # 2. 摘要分（15%）— 有简介说明看得懂
    has_summary = 1.0 if (item.get("summary") or "").strip() else 0.3

    # 3. 标签实用度（15%）— 标签越"能动手"越高
    tags = item.get("tags", [])
    if tags:
        tag_scores = [TAG_BONUS.get(t, 0.4) for t in tags]
        tag_s = sum(tag_scores) / len(tag_scores)
    else:
        tag_s = 0.4

    # 4. 社区认可（20%）— star/点赞越多越好
    stars = item.get("stars", 0) or 0
    engagement_norm = min(stars / max(max_stars, 1), 1.0)

    # 5. 新鲜度（10%）
    recency = 1.0

    score = (
        source_s * 0.40
        + has_summary * 0.15
        + tag_s * 0.15
        + engagement_norm * 0.20
        + recency * 0.10
    )
    return round(score * 100, 1)


def deduplicate(items):
    if not items:
        return []

    seen = []
    for item in items:
        is_dup = False
        for s in seen:
            if item["url"] and item["url"] == s["url"]:
                is_dup = True
                break
            if _similar(item["title"], s["title"]):
                is_dup = True
                break
        if not is_dup:
            seen.append(item)

    max_stars = max((i.get("stars", 0) or 0) for i in seen) if seen else 1

    for item in seen:
        item["learning_score"] = _compute_learning_score(item, max_stars)
        item["id"] = _make_id(item)

    seen.sort(key=lambda i: i["learning_score"], reverse=True)
    return seen
