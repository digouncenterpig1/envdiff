"""Export MultiDiff results to files."""
from __future__ import annotations

import csv
import io
from pathlib import Path

from envdiff.differ import MultiDiff
from envdiff.diff_reporter import format_multi_diff_json, format_multi_diff_text


def _ensure_parent(path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def export_multi_diff_text(multi: MultiDiff, dest: str, use_color: bool = False) -> None:
    _ensure_parent(dest)
    Path(dest).write_text(format_multi_diff_text(multi, use_color=use_color), encoding="utf-8")


def export_multi_diff_json(multi: MultiDiff, dest: str) -> None:
    _ensure_parent(dest)
    Path(dest).write_text(format_multi_diff_json(multi), encoding="utf-8")


def export_multi_diff_csv(multi: MultiDiff, dest: str) -> None:
    _ensure_parent(dest)
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["base", "target", "issue_type", "key", "base_value", "target_value"])
    for p in multi.pairs:
        for key in sorted(p.result.missing_in_target):
            writer.writerow([p.base_label, p.target_label, "missing_in_target", key, "", ""])
        for key in sorted(p.result.missing_in_base):
            writer.writerow([p.base_label, p.target_label, "missing_in_base", key, "", ""])
        for key, (bv, tv) in sorted(p.result.mismatches.items()):
            writer.writerow([p.base_label, p.target_label, "mismatch", key, bv, tv])
    Path(dest).write_text(buf.getvalue(), encoding="utf-8")
