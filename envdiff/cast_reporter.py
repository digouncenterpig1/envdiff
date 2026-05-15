"""Reporting helpers for CastResult."""
from __future__ import annotations

import json
from typing import List

from .caster import CastResult

_TYPE_COLORS = {
    "int": "\033[36m",
    "float": "\033[35m",
    "bool": "\033[33m",
    "empty": "\033[90m",
    "string": "\033[0m",
}
_RESET = "\033[0m"


def _c(text: str, type_name: str, *, color: bool) -> str:
    if not color:
        return text
    return f"{_TYPE_COLORS.get(type_name, '')}{text}{_RESET}"


def format_cast_text(result: CastResult, *, color: bool = False) -> str:
    lines: List[str] = [f"Cast inference: {result.source}"]
    lines.append("-" * 40)
    if not result.entries:
        lines.append("  (no keys)")
        return "\n".join(lines)
    for entry in result.entries:
        label = _c(entry.inferred_type, entry.inferred_type, color=color)
        lines.append(f"  {entry.key} = {entry.raw!r}  [{label}]")
    lines.append("")
    counts = result.type_counts
    summary_parts = ", ".join(f"{t}: {n}" for t, n in sorted(counts.items()))
    lines.append(f"Summary: {summary_parts}")
    return "\n".join(lines)


def format_cast_json(result: CastResult) -> str:
    data = {
        "source": result.source,
        "type_counts": result.type_counts,
        "entries": [
            {
                "key": e.key,
                "raw": e.raw,
                "inferred_type": e.inferred_type,
                "cast_value": e.cast_value,
            }
            for e in result.entries
        ],
    }
    return json.dumps(data, indent=2)


def format_cast_comparison(results: List[CastResult], *, color: bool = False) -> str:
    blocks: List[str] = []
    for r in results:
        blocks.append(format_cast_text(r, color=color))
    return "\n\n".join(blocks)


def print_cast_report(result: CastResult, *, color: bool = True) -> None:
    print(format_cast_text(result, color=color))
