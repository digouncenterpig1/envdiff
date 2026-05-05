"""Tests for envdiff.formatter."""

import json
import csv
import io
import pytest
from envdiff.comparator import DiffResult
from envdiff.formatter import format_text, format_json, format_csv, format_result


@pytest.fixture
def sample_result():
    return DiffResult(
        missing_in_target={"SECRET_KEY"},
        missing_in_base={"NEW_FEATURE_FLAG"},
        mismatched={"DB_HOST": ("localhost", "prod.db.example.com")},
    )


@pytest.fixture
def empty_result():
    return DiffResult(missing_in_target=set(), missing_in_base=set(), mismatched={})


def test_format_text_shows_missing_in_target(sample_result):
    out = format_text(sample_result)
    assert "Missing in target" in out
    assert "SECRET_KEY" in out


def test_format_text_shows_missing_in_base(sample_result):
    out = format_text(sample_result)
    assert "Missing in base" in out
    assert "NEW_FEATURE_FLAG" in out


def test_format_text_shows_mismatches(sample_result):
    out = format_text(sample_result)
    assert "DB_HOST" in out
    assert "localhost" in out
    assert "prod.db.example.com" in out


def test_format_text_no_differences(empty_result):
    out = format_text(empty_result)
    assert "No differences found" in out


def test_format_json_structure(sample_result):
    out = format_json(sample_result)
    data = json.loads(out)
    assert "missing_in_target" in data
    assert "missing_in_base" in data
    assert "mismatched" in data
    assert "SECRET_KEY" in data["missing_in_target"]
    assert "DB_HOST" in data["mismatched"]
    assert data["mismatched"]["DB_HOST"]["base"] == "localhost"


def test_format_json_custom_names(sample_result):
    out = format_json(sample_result, base_name="prod", target_name="staging")
    data = json.loads(out)
    assert "missing_in_staging" in data
    assert "missing_in_prod" in data
    assert data["mismatched"]["DB_HOST"]["prod"] == "localhost"


def test_format_csv_has_header(sample_result):
    out = format_csv(sample_result)
    reader = csv.reader(io.StringIO(out))
    header = next(reader)
    assert header == ["type", "key", "base", "target"]


def test_format_csv_rows(sample_result):
    out = format_csv(sample_result)
    rows = list(csv.reader(io.StringIO(out)))
    types = [r[0] for r in rows[1:]]
    assert "missing_in_target" in types
    assert "missing_in_base" in types
    assert "mismatch" in types


def test_format_result_dispatches_json(sample_result):
    out = format_result(sample_result, fmt="json")
    data = json.loads(out)
    assert isinstance(data, dict)


def test_format_result_dispatches_csv(sample_result):
    out = format_result(sample_result, fmt="csv")
    assert "type" in out.splitlines()[0]


def test_format_result_default_is_text(sample_result):
    out = format_result(sample_result)
    assert "Missing in target" in out
