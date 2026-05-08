"""Reporting helpers for RenameResult."""

from __future__ import annotations

import json
from typing import Optional

from .renamer import RenameResult

_RESET = "\033[0m"
_GREEN = "\033[32m"
_YELLOW = "\033[33m"
_CYAN = "\033[36m"


def _c(text: str, code: str, color: bool) -> str:
    return f"{code}{text}{_RESET}" if color else text


def format_rename_text(result: RenameResult, color: bool = True) -> str:
    lines: list[str] = []

    if result.renamed:
        lines.append(_c("Renamed keys:", _CYAN, color))
        for old, new in result.renamed.items():
            arrow = _c("→", _GREEN, color)
            lines.append(f"  {old}  {arrow}  {new}")
    else:
        lines.append(_c("No keys renamed.", _YELLOW, color))

    if result.skipped:
        lines.append(_c("Skipped (not found):", _YELLOW, color))
        for key in result.skipped:
            lines.append(f"  {key}")

    return "\n".join(lines)


def format_rename_json(result: RenameResult) -> str:
    payload = {
        "renamed": result.renamed,
        "skipped": result.skipped,
        "total_renamed": len(result.renamed),
        "total_skipped": len(result.skipped),
    }
    return json.dumps(payload, indent=2)


def print_rename_report(
    result: RenameResult,
    fmt: str = "text",
    color: bool = True,
) -> None:
    if fmt == "json":
        print(format_rename_json(result))
    else:
        print(format_rename_text(result, color=color))
