"""Export DiffSummary to files."""

import json
from pathlib import Path

from envdiff.differ_summary import DiffSummary
from envdiff.summary_reporter import format_summary_text, format_summary_json


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def export_summary_text(summary: DiffSummary, dest: Path, *, color: bool = False) -> None:
    _ensure_parent(dest)
    dest.write_text(format_summary_text(summary, color=color), encoding="utf-8")


def export_summary_json(summary: DiffSummary, dest: Path) -> None:
    _ensure_parent(dest)
    dest.write_text(format_summary_json(summary), encoding="utf-8")


def export_summary_csv(summary: DiffSummary, dest: Path) -> None:
    _ensure_parent(dest)
    rows = [
        "metric,value",
        f"total_pairs,{summary.total_pairs}",
        f"clean_pairs,{summary.clean_pairs}",
        f"pairs_with_differences,{summary.pairs_with_differences}",
        f"total_missing_in_target,{summary.total_missing_in_target}",
        f"total_missing_in_base,{summary.total_missing_in_base}",
        f"total_mismatches,{summary.total_mismatches}",
        f"total_issues,{summary.total_issues}",
        f"keys_always_missing,{'|'.join(summary.keys_always_missing)}",
        f"keys_always_mismatched,{'|'.join(summary.keys_always_mismatched)}",
    ]
    dest.write_text("\n".join(rows) + "\n", encoding="utf-8")


def export_summary(summary: DiffSummary, dest: Path, fmt: str = "text") -> None:
    if fmt == "json":
        export_summary_json(summary, dest)
    elif fmt == "csv":
        export_summary_csv(summary, dest)
    else:
        export_summary_text(summary, dest)
