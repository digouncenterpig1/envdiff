"""Format and print TagResult objects."""

from __future__ import annotations

import json
from typing import List

from envdiff.tagger import TagResult

_COLORS = {
    "secret": "\033[91m",
    "url": "\033[94m",
    "flag": "\033[93m",
    "numeric": "\033[96m",
    "empty": "\033[90m",
    "plain": "\033[0m",
}
_RESET = "\033[0m"


def _c(text: str, tag: str, color: bool) -> str:
    if not color:
        return text
    code = _COLORS.get(tag, "")
    return f"{code}{text}{_RESET}" if code else text


def format_tag_text(result: TagResult, color: bool = False) -> str:
    lines = [f"Tags for: {result.source}"]
    if not result.tags:
        lines.append("  (no keys)")
        return "\n".join(lines)
    for key, tags in sorted(result.tags.items()):
        primary = next(iter(sorted(tags)), "plain")
        tag_str = ", ".join(sorted(tags))
        lines.append(f"  {_c(key, primary, color)}: [{tag_str}]")
    return "\n".join(lines)


def format_tag_json(result: TagResult) -> str:
    payload = {
        "source": result.source,
        "tags": {k: sorted(v) for k, v in result.tags.items()},
    }
    return json.dumps(payload, indent=2)


def format_tags_comparison(results: List[TagResult], color: bool = False) -> str:
    blocks = [format_tag_text(r, color=color) for r in results]
    return "\n\n".join(blocks)


def print_tag_report(result: TagResult, color: bool = True) -> None:
    print(format_tag_text(result, color=color))
