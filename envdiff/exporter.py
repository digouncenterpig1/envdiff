"""Export diff results to various file formats on disk."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Literal

from envdiff.comparator import DiffResult
from envdiff.formatter import format_json, format_text

ExportFormat = Literal["text", "json", "csv"]


def _ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def export_text(result: DiffResult, path: Path) -> None:
    """Write a human-readable text report to *path*."""
    _ensure_parent(path)
    path.write_text(format_text(result), encoding="utf-8")


def export_json(result: DiffResult, path: Path) -> None:
    """Write a JSON report to *path*."""
    _ensure_parent(path)
    path.write_text(format_json(result), encoding="utf-8")


def export_csv(result: DiffResult, path: Path) -> None:
    """Write a CSV report to *path*."""
    _ensure_parent(path)
    rows: list[dict[str, str]] = []
    for key in result.missing_in_target:
        rows.append({"key": key, "type": "missing_in_target", "base_value": "", "target_value": ""})
    for key in result.missing_in_base:
        rows.append({"key": key, "type": "missing_in_base", "base_value": "", "target_value": ""})
    for key, (base_val, target_val) in result.mismatches.items():
        rows.append({"key": key, "type": "mismatch", "base_value": base_val, "target_value": target_val})

    with path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(fh, fieldnames=["key", "type", "base_value", "target_value"])
        writer.writeheader()
        writer.writerows(rows)


def export_result(result: DiffResult, path: Path, fmt: ExportFormat = "text") -> None:
    """Dispatch export to the appropriate handler based on *fmt*."""
    handlers = {
        "text": export_text,
        "json": export_json,
        "csv": export_csv,
    }
    if fmt not in handlers:
        raise ValueError(f"Unsupported export format: {fmt!r}. Choose from {list(handlers)}.")
    handlers[fmt](result, path)
