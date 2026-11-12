"""Derive aggregate fixed-price budget references from an attributed Kaggle ZIP.

No source job text, links, client identifiers, or raw rows are emitted. These
descriptive statistics are not labels for bid decisions or reply outcomes.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import statistics
import zipfile


SOURCE = "https://www.kaggle.com/datasets/asaniczka/upwork-job-postings-dataset-2024-50k-records"
LICENSE = "ODC Attribution License (ODC-By)"
CATEGORY_TERMS = {
    "analytics": ("data", "analytics", "dashboard", "power bi", "tableau", "excel"),
    "web_development": ("web", "full stack", "frontend", "backend", "react", "wordpress"),
    "ai_ml": ("machine learning", "ai ", "chatbot", "llm", "computer vision"),
    "design": ("design", "figma", "graphic", "logo", "ux", "ui "),
    "marketing": ("marketing", "seo", "ads", "social media", "media buyer"),
    "writing": ("writer", "writing", "content", "copywriting", "translation"),
}


def category(title: str) -> str:
    value = f" {title.casefold()} "
    for name, terms in CATEGORY_TERMS.items():
        if any(term in value for term in terms):
            return name
    return "other"


def percentile(sorted_values: list[float], p: float) -> float:
    return sorted_values[round((len(sorted_values) - 1) * p)]


def build(zip_path: Path) -> dict:
    groups: dict[str, list[float]] = {name: [] for name in (*CATEGORY_TERMS, "other")}
    total = duplicate = hourly = missing = invalid = 0
    seen: set[tuple[str, str]] = set()
    with zipfile.ZipFile(zip_path) as archive:
        with io.TextIOWrapper(archive.open("upwork-jobs.csv"), encoding="utf-8-sig", newline="") as stream:
            for row in csv.DictReader(stream):
                total += 1
                key = (row["title"].strip().casefold(), row["description"].strip().casefold())
                if key in seen:
                    duplicate += 1
                    continue
                seen.add(key)
                if row["is_hourly"].casefold() == "true":
                    hourly += 1
                    continue
                if not row["budget"].strip():
                    missing += 1
                    continue
                try:
                    budget = float(row["budget"])
                except ValueError:
                    invalid += 1
                    continue
                if not 50 <= budget <= 100_000:
                    invalid += 1
                    continue
                groups[category(row["title"])].append(budget)
    summaries = {}
    for name, values in groups.items():
        if values:
            ordered = sorted(values)
            summaries[name] = {
                "count": len(ordered),
                "median_usd": round(statistics.median(ordered), 2),
                "p25_usd": round(percentile(ordered, .25), 2),
                "p75_usd": round(percentile(ordered, .75), 2),
            }
    return {
        "source": SOURCE,
        "license": LICENSE,
        "source_zip_sha256": hashlib.sha256(zip_path.read_bytes()).hexdigest(),
        "method": "Title keyword categories; exact title+description deduplication; fixed-price USD budgets in [50, 100000]; no outcome labels.",
        "rows": {"total": total, "duplicates": duplicate, "hourly_excluded": hourly, "missing_budget": missing,
                 "invalid_or_outlier_budget": invalid, "included": sum(len(v) for v in groups.values())},
        "categories": summaries,
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("zip_path", type=Path)
    parser.add_argument("--output", type=Path, default=Path("data/derived/kaggle_market_priors.json"))
    args = parser.parse_args()
    result = build(args.zip_path)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(args.output)
