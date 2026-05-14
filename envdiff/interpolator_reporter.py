"""Format and print InterpolateResult objects."""
from __future__ import annotations

import json
from typing import Optional

from envdiff.interpolator import InterpolateResult


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_interpolate_text(result: InterpolateResult, *, color: bool = True) -> str:
    lines: list[str] = []
    label = _c(result.source, "1") if color else result.source
    lines.append(f"Interpolation report: {label}")
    lines.append(f"  Total keys : {len(result.resolved)}")
    lines.append(f"  Unresolved : {result.unresolved_count}")

    if result.unresolved_refs:
        lines.append("")
        lines.append("  Unresolved references:")
        for key, missing in sorted(result.unresolved_refs.items()):
            key_label = _c(key, "33") if color else key
            refs = ", ".join(missing)
            lines.append(f"    {key_label}  ->  missing: {refs}")
    else:
        ok = _c("all references resolved", "32") if color else "all references resolved"
        lines.append(f"  Status     : {ok}")

    return "\n".join(lines)


def format_interpolate_json(result: InterpolateResult) -> str:
    payload = {
        "source": result.source,
        "total_keys": len(result.resolved),
        "unresolved_count": result.unresolved_count,
        "resolved": result.resolved,
        "unresolved_refs": result.unresolved_refs,
    }
    return json.dumps(payload, indent=2)


def print_interpolate_report(
    result: InterpolateResult,
    *,
    fmt: str = "text",
    color: bool = True,
) -> None:
    if fmt == "json":
        print(format_interpolate_json(result))
    else:
        print(format_interpolate_text(result, color=color))
