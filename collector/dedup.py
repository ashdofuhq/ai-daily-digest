"""Deduplication and hot score calculation."""

import hashlib
import re
from difflib import SequenceMatcher

SOURCE_WEIGHTS = {
    "hackernews": 1.0,
    "huggingface": 0.9,
    "paperswithcode": 0.7,
    "arxiv": 0.5,
    "github": 0.4,
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


def _compute_hot_score(item, max_stars=1, max_engagement=1):
    source_w = SOURCE_WEIGHTS.get(item["source"], 0.5)
    stars = item.get("stars", 0) or 0

    engagement_norm = min(stars / max(max_engagement, 1), 1.0)
    recency = 1.0  # all items from today

    score = (recency * 0.3) + (source_w * 0.2) + (engagement_norm * 0.5)
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
    max_engagement = max((i.get("stars", 0) or 0) for i in seen) if seen else 1

    for item in seen:
        item["hot_score"] = _compute_hot_score(item, max_stars, max_engagement)
        item["id"] = _make_id(item)

    seen.sort(key=lambda i: i["hot_score"], reverse=True)
    return seen
