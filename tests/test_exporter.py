"""Tests for envdiff.exporter."""

from __future__ import annotations

import csv
import json
from pathlib import Path

import pytest

from envdiff.comparator import DiffResult
from envdiff.exporter import export_csv, export_json, export_result, export_text


@pytest.fixture()
def result() -> DiffResult:
    return DiffResult(
        missing_in_target={"ONLY_BASE"},
        missing_in_base={"ONLY_TARGET"},
        mismatches={"SHARED": ("val1", "val2")},
    )


@pytest.fixture()
def empty_result() -> DiffResult:
    return DiffResult(missing_in_target=set(), missing_in_base=set(), mismatches={})


def test_export_text_creates_file(tmp_path: Path, result: DiffResult) -> None:
    out = tmp_path / "report.txt"
    export_text(result, out)
    assert out.exists()
    content = out.read_text()
    assert "ONLY_BASE" in content
    assert "ONLY_TARGET" in content
    assert "SHARED" in content


def test_export_json_valid_structure(tmp_path: Path, result: DiffResult) -> None:
    out = tmp_path / "report.json"
    export_json(result, out)
    data = json.loads(out.read_text())
    assert "missing_in_target" in data
    assert "ONLY_BASE" in data["missing_in_target"]
    assert data["mismatches"]["SHARED"] == ["val1", "val2"]


def test_export_csv_rows(tmp_path: Path, result: DiffResult) -> None:
    out = tmp_path / "report.csv"
    export_csv(result, out)
    with out.open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    types = {r["type"] for r in rows}
    assert "missing_in_target" in types
    assert "missing_in_base" in types
    assert "mismatch" in types


def test_export_csv_empty(tmp_path: Path, empty_result: DiffResult) -> None:
    out = tmp_path / "empty.csv"
    export_csv(empty_result, out)
    with out.open(newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert rows == []


def test_export_result_dispatches(tmp_path: Path, result: DiffResult) -> None:
    for fmt in ("text", "json", "csv"):
        out = tmp_path / f"out.{fmt}"
        export_result(result, out, fmt=fmt)  # type: ignore[arg-type]
        assert out.exists()


def test_export_result_bad_format(tmp_path: Path, result: DiffResult) -> None:
    with pytest.raises(ValueError, match="Unsupported export format"):
        export_result(result, tmp_path / "x.xyz", fmt="xml")  # type: ignore[arg-type]


def test_export_creates_parent_dirs(tmp_path: Path, result: DiffResult) -> None:
    out = tmp_path / "nested" / "deep" / "report.json"
    export_json(result, out)
    assert out.exists()
