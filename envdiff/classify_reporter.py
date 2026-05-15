"""Reporters for ClassifyResult output."""

from __future__ import annotations

import json
from typing import List

from envdiff.classifier import ClassifyResult

_CATEGORY_COLORS = {
    "secret": "\033[91m",
    "url": "\033[94m",
    "port": "\033[96m",
    "flag": "\033[93m",
    "path": "\033[95m",
    "email": "\033[92m",
    "timeout": "\033[33m",
    "numeric": "\033[36m",
    "unknown": "\033[90m",
}
_RESET = "\033[0m"


def _c(text: str, category: str, color: bool) -> str:
    if not color:
        return text
    code = _CATEGORY_COLORS.get(category, "")
    return f"{code}{text}{_RESET}"


def format_classify_text(result: ClassifyResult, color: bool = True) -> str:
    lines = [f"Classification: {result.source}"]
    lines.append("-" * 40)
    by_cat = result.by_category()
    if not by_cat:
        lines.append("  (no keys)")
        return "\n".join(lines)
    for category in sorted(by_cat):
        entries = by_cat[category]
        label = _c(f"[{category.upper()}]", category, color)
        lines.append(f"  {label} ({len(entries)} key(s))")
        for e in entries:
            lines.append(f"    {e.key}")
    return "\n".join(lines)


def format_classify_json(result: ClassifyResult) -> str:
    payload = {
        "source": result.source,
        "categories": {
            cat: [e.key for e in entries]
            for cat, entries in result.by_category().items()
        },
        "counts": result.category_counts(),
    }
    return json.dumps(payload, indent=2)


def format_classify_comparison(results: List[ClassifyResult], color: bool = True) -> str:
    lines = []
    for r in results:
        lines.append(format_classify_text(r, color=color))
        lines.append("")
    return "\n".join(lines).rstrip()


def print_classify_report(result: ClassifyResult, color: bool = True) -> None:
    print(format_classify_text(result, color=color))
