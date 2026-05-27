"""Papers With Code — trending papers."""

import json
import urllib.request
from datetime import datetime, timezone

PWC_API = "https://paperswithcode.com/api/v1/papers/"

TAG_KW = {
    "LLM": ["llm", "language model", "gpt", "transformer"],
    "Vision": ["vision", "image", "visual", "detection", "segmentation"],
    "RL": ["reinforcement learning", "rl", "policy"],
    "Graph": ["graph neural", "gnn"],
    "NLP": ["nlp", "language", "text"],
    "GAN": ["gan", "generative adversarial"],
    "Diffusion": ["diffusion", "denoising"],
    "Reasoning": ["reasoning", "math"],
    "Code": ["code generation", "program synthesis"],
    "Safety": ["safety", "robust", "adversarial"],
    "Drug": ["drug", "molecule", "protein"],
    "Audio": ["speech", "audio", "voice"],
}


def fetch_paperswithcode():
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    results = []

    try:
        req = urllib.request.Request(
            PWC_API,
            headers={"User-Agent": "AI-Daily-Digest/1.0", "Accept": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"[PapersWithCode] Failed to fetch: {e}")
        return []

    papers = data.get("results", [])[:30]

    for p in papers:
        title = p.get("title", "")
        url_parts = p.get("url_abs", p.get("url_pdf", ""))
        if not url_parts and p.get("id"):
            url_parts = f"https://paperswithcode.com/paper/{p['id']}"

        title = title.replace("\n", " ").strip()
        summary = (p.get("abstract", "") or "")[:300].replace("\n", " ").strip()

        tags = []
        combined = (title + " " + summary).lower()
        for tag, keywords in TAG_KW.items():
            for kw in keywords:
                if kw.lower() in combined:
                    tags.append(tag)
                    break

        stars = p.get("stars", p.get("github_stars", 0)) or 0

        results.append(
            {
                "title": title,
                "summary": summary,
                "url": url_parts,
                "source": "paperswithcode",
                "source_label": "PapersWithCode",
                "tags": tags[:4],
                "stars": int(stars) if stars else 0,
                "date": today,
                "authors": "",
                "language": "en",
                "hot_score": 0,
            }
        )

    return results[:20]
