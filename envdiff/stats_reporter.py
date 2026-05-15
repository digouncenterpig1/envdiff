"""Reporters for DiffStats — text, JSON, and print helper."""

from __future__ import annotations

import json

from envdiff.differ_stats import DiffStats


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_stats_text(stats: DiffStats) -> str:
    lines = []
    lines.append(_c(f"=== Diff Stats: {stats.source} ===", "1"))
    lines.append(f"  Total pairs     : {stats.total_pairs}")
    clean_label = _c(str(stats.clean_pairs), "32") if stats.clean_pairs == stats.total_pairs else str(stats.clean_pairs)
    lines.append(f"  Clean pairs     : {clean_label}")
    dirty_label = _c(str(stats.dirty_pairs), "31") if stats.dirty_pairs > 0 else str(stats.dirty_pairs)
    lines.append(f"  Dirty pairs     : {dirty_label}")
    lines.append(f"  Health ratio    : {stats.health_ratio:.2%}")
    lines.append("")
    lines.append(_c("  Issue breakdown:", "1"))
    lines.append(f"    Missing in target : {stats.total_missing_in_target} keys across {stats.pairs_with_missing_in_target} pair(s)")
    lines.append(f"    Missing in base   : {stats.total_missing_in_base} keys across {stats.pairs_with_missing_in_base} pair(s)")
    lines.append(f"    Mismatches        : {stats.total_mismatches} keys across {stats.pairs_with_mismatches} pair(s)")
    if stats.most_affected_key:
        lines.append("")
        lines.append(f"  Most affected key : {_c(stats.most_affected_key, '33')}")
    return "\n".join(lines)


def format_stats_json(stats: DiffStats) -> str:
    return json.dumps(stats.as_dict(), indent=2)


def format_stats_comparison(stats_list: list[DiffStats]) -> str:
    lines = [_c("=== Stats Comparison ===", "1"), ""]
    for stats in stats_list:
        lines.append(format_stats_text(stats))
        lines.append("")
    return "\n".join(lines).rstrip()


def print_stats_report(stats: DiffStats, fmt: str = "text") -> None:
    if fmt == "json":
        print(format_stats_json(stats))
    else:
        print(format_stats_text(stats))
