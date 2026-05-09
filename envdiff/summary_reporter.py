"""Reporters for DiffSummary output."""

import json
from typing import Optional

from envdiff.differ_summary import DiffSummary


def _c(text: str, code: str) -> str:
    return f"\033[{code}m{text}\033[0m"


def format_summary_text(summary: DiffSummary, *, color: bool = True) -> str:
    lines = []
    _h = (lambda t: _c(t, "1")) if color else (lambda t: t)
    _ok = (lambda t: _c(t, "32")) if color else (lambda t: t)
    _warn = (lambda t: _c(t, "33")) if color else (lambda t: t)
    _err = (lambda t: _c(t, "31")) if color else (lambda t: t)

    lines.append(_h("=== Diff Summary ==="))
    lines.append(f"  Pairs compared : {summary.total_pairs}")
    clean_str = _ok(str(summary.clean_pairs)) if summary.clean_pairs == summary.total_pairs else str(summary.clean_pairs)
    diff_str = _ok("0") if summary.pairs_with_differences == 0 else _err(str(summary.pairs_with_differences))
    lines.append(f"  Clean pairs    : {clean_str}")
    lines.append(f"  Pairs with diff: {diff_str}")
    lines.append("")
    lines.append(f"  Missing in target : {_warn(str(summary.total_missing_in_target))}")
    lines.append(f"  Missing in base   : {_warn(str(summary.total_missing_in_base))}")
    lines.append(f"  Mismatches        : {_warn(str(summary.total_mismatches))}")
    lines.append(f"  Total issues      : {_err(str(summary.total_issues)) if summary.total_issues else _ok('0')}")

    if summary.keys_always_missing:
        lines.append("")
        lines.append(_h("  Keys missing in ALL targets:"))
        for k in summary.keys_always_missing:
            lines.append(f"    - {k}")

    if summary.keys_always_mismatched:
        lines.append("")
        lines.append(_h("  Keys mismatched in ALL pairs:"))
        for k in summary.keys_always_mismatched:
            lines.append(f"    ~ {k}")

    return "\n".join(lines)


def format_summary_json(summary: DiffSummary) -> str:
    return json.dumps(summary.as_dict(), indent=2)


def print_summary_report(
    summary: DiffSummary,
    fmt: str = "text",
    color: bool = True,
    out=None,
) -> None:
    import sys
    out = out or sys.stdout
    if fmt == "json":
        print(format_summary_json(summary), file=out)
    else:
        print(format_summary_text(summary, color=color), file=out)
