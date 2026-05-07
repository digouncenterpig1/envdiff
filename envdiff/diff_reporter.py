"""Reporting for MultiDiff results."""
from __future__ import annotations

import json
from typing import List

from envdiff.differ import MultiDiff, PairDiff

ANSI_RESET = "\033[0m"
ANSI_RED = "\033[31m"
ANSI_YELLOW = "\033[33m"
ANSI_GREEN = "\033[32m"
ANSI_BOLD = "\033[1m"


def _c(color: str, text: str, use_color: bool) -> str:
    return f"{color}{text}{ANSI_RESET}" if use_color else text


def _format_pair(pair: PairDiff, use_color: bool) -> List[str]:
    lines: List[str] = []
    header = f"--- {pair.base_label}  vs  {pair.target_label} ---"
    lines.append(_c(ANSI_BOLD, header, use_color))

    r = pair.result
    if not (r.missing_in_target or r.missing_in_base or r.mismatches):
        lines.append(_c(ANSI_GREEN, "  No differences found.", use_color))
        return lines

    for key in sorted(r.missing_in_target):
        lines.append(_c(ANSI_RED, f"  MISSING IN TARGET : {key}", use_color))
    for key in sorted(r.missing_in_base):
        lines.append(_c(ANSI_YELLOW, f"  MISSING IN BASE   : {key}", use_color))
    for key, (bv, tv) in sorted(r.mismatches.items()):
        lines.append(_c(ANSI_YELLOW, f"  MISMATCH          : {key}  ({bv!r} != {tv!r})", use_color))
    return lines


def format_multi_diff_text(multi: MultiDiff, use_color: bool = False) -> str:
    lines = [f"Base: {multi.base_label}", ""]
    for pair in multi.pairs:
        lines.extend(_format_pair(pair, use_color))
        lines.append("")
    summary = multi.summary()
    lines.append("Summary:")
    for label, count in summary.items():
        status = _c(ANSI_GREEN, "OK", use_color) if count == 0 else _c(ANSI_RED, f"{count} issue(s)", use_color)
        lines.append(f"  {label}: {status}")
    return "\n".join(lines)


def format_multi_diff_json(multi: MultiDiff) -> str:
    pairs = []
    for p in multi.pairs:
        pairs.append({
            "base": p.base_label,
            "target": p.target_label,
            "missing_in_target": sorted(p.result.missing_in_target),
            "missing_in_base": sorted(p.result.missing_in_base),
            "mismatches": {
                k: {"base": bv, "target": tv}
                for k, (bv, tv) in sorted(p.result.mismatches.items())
            },
        })
    return json.dumps({"base": multi.base_label, "comparisons": pairs}, indent=2)


def print_multi_diff_report(multi: MultiDiff, use_color: bool = True) -> None:
    print(format_multi_diff_text(multi, use_color=use_color))
