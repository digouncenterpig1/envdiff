"""Reporting helpers for pin/drift results."""

from __future__ import annotations

import json
from typing import List

from envdiff.pinner import PinResult


def _c(text: str, color: str) -> str:
    codes = {"red": "\033[31m", "green": "\033[32m", "yellow": "\033[33m", "reset": "\033[0m"}
    return f"{codes.get(color, '')}{text}{codes['reset']}"


def format_pin_text(result: PinResult) -> str:
    lines: List[str] = []
    label = result.source or "env"
    lines.append(f"Pin drift report for: {label}")
    lines.append("-" * 40)

    if not result.has_drift():
        lines.append(_c("  No drift detected. All values match the pin.", "green"))
        return "\n".join(lines)

    if result.drifted:
        lines.append(_c(f"  Changed ({len(result.drifted)}):", "yellow"))
        for k in sorted(result.drifted):
            lines.append(f"    ~ {k}")

    if result.new_keys:
        lines.append(_c(f"  New keys ({len(result.new_keys)}):", "yellow"))
        for k in sorted(result.new_keys):
            lines.append(f"    + {k}")

    if result.removed_keys:
        lines.append(_c(f"  Removed keys ({len(result.removed_keys)}):", "red"))
        for k in sorted(result.removed_keys):
            lines.append(f"    - {k}")

    return "\n".join(lines)


def format_pin_json(result: PinResult) -> str:
    return json.dumps(
        {
            "source": result.source,
            "has_drift": result.has_drift(),
            "drifted": sorted(result.drifted),
            "new_keys": sorted(result.new_keys),
            "removed_keys": sorted(result.removed_keys),
        },
        indent=2,
    )


def print_pin_report(result: PinResult, fmt: str = "text") -> None:
    if fmt == "json":
        print(format_pin_json(result))
    else:
        print(format_pin_text(result))
