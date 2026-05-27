#!/usr/bin/env python3
"""AI Daily Digest — main entrypoint. Fetches from all sources, deduplicates,
computes hot scores, and writes JSON data files."""

import json
import os
import sys
from datetime import datetime, timezone

from sources import (
    fetch_arxiv,
    fetch_github,
    fetch_huggingface,
    fetch_paperswithcode,
    fetch_hackernews,
)
from dedup import deduplicate

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


def fetch_all():
    print("=" * 50)
    print("AI Daily Digest — Collector")
    print(f"Run at: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 50)

    all_items = []
    sources = [
        ("Arxiv", fetch_arxiv),
        ("GitHub Trending", fetch_github),
        ("HuggingFace Daily", fetch_huggingface),
        ("Papers With Code", fetch_paperswithcode),
        ("Hacker News", fetch_hackernews),
    ]

    for name, fetcher in sources:
        try:
            print(f"\n[{name}] Fetching...")
            items = fetcher()
            print(f"[{name}] Got {len(items)} items")
            all_items.extend(items)
        except Exception as e:
            print(f"[{name}] Error: {e}")

    print(f"\nTotal before dedup: {len(all_items)}")
    unique = deduplicate(all_items)
    print(f"Total after dedup: {len(unique)}")

    return unique


def save_data(items):
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")

    # Daily file
    daily_path = os.path.join(DATA_DIR, f"{today}.json")
    with open(daily_path, "w", encoding="utf-8") as f:
        json.dump(
            {"date": today, "total": len(items), "items": items},
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(f"\nSaved: {daily_path}")

    # latest.json (symlink not portable on Windows, write a copy)
    latest_path = os.path.join(DATA_DIR, "latest.json")
    with open(latest_path, "w", encoding="utf-8") as f:
        json.dump(
            {"date": today, "total": len(items), "items": items},
            f,
            ensure_ascii=False,
            indent=2,
        )
    print(f"Saved: {latest_path}")

    # archive.json (last 7 days)
    archive_path = os.path.join(DATA_DIR, "archive.json")
    archive = {}
    if os.path.exists(archive_path):
        try:
            with open(archive_path, "r", encoding="utf-8") as f:
                archive = json.load(f)
        except (json.JSONDecodeError, IOError):
            archive = {}

    archive[today] = {
        "date": today,
        "total": len(items),
        "items": items,
    }

    # Keep only the last 7 entries
    sorted_dates = sorted(archive.keys(), reverse=True)[:7]
    trimmed = {d: archive[d] for d in sorted_dates}

    with open(archive_path, "w", encoding="utf-8") as f:
        json.dump(trimmed, f, ensure_ascii=False, indent=2)
    print(f"Saved: {archive_path} (last {len(trimmed)} days)")


def main():
    ensure_data_dir()
    items = fetch_all()
    save_data(items)
    print("\nDone!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
