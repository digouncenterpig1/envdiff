"""Reporters for GroupResult output."""
from __future__ import annotations

import json
from typing import List

from envdiff.grouper import GroupResult


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_group_text(result: GroupResult, color: bool = True) -> str:
    lines: List[str] = []
    header = f"Groups for {result.source}  ({result.total_groups()} groups, {result.key_count()} keys)"
    lines.append(_c(header, "1;34") if color else header)
    lines.append("")

    for name in result.group_names():
        keys = result.groups[name]
        label = _c(f"[{name}]", "1;33") if color else f"[{name}]"
        lines.append(f"  {label}  ({len(keys)} keys)")
        for k in keys:
            lines.append(f"    {k}")
        lines.append("")

    if result.ungrouped:
        ug_label = _c("[ungrouped]", "2") if color else "[ungrouped]"
        lines.append(f"  {ug_label}  ({len(result.ungrouped)} keys)")
        for k in result.ungrouped:
            lines.append(f"    {k}")
        lines.append("")

    return "\n".join(lines)


def format_group_json(result: GroupResult) -> str:
    data = {
        "source": result.source,
        "total_groups": result.total_groups(),
        "key_count": result.key_count(),
        "groups": result.groups,
        "ungrouped": result.ungrouped,
    }
    return json.dumps(data, indent=2)


def format_groups_comparison(results: List[GroupResult], color: bool = True) -> str:
    parts = [format_group_text(r, color=color) for r in results]
    sep = _c("─" * 50, "2") if color else "─" * 50
    return ("\n" + sep + "\n").join(parts)


def print_group_report(result: GroupResult, color: bool = True) -> None:
    print(format_group_text(result, color=color))
