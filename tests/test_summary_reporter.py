"""Tests for summary_reporter.py"""

import json
import pytest
from envdiff.differ_summary import DiffSummary
from envdiff.summary_reporter import (
    format_summary_text,
    format_summary_json,
    print_summary_report,
)
import io


@pytest.fixture
def clean_summary():
    return DiffSummary(total_pairs=3, pairs_with_differences=0)


@pytest.fixture
def dirty_summary():
    return DiffSummary(
        total_pairs=3,
        pairs_with_differences=2,
        total_missing_in_target=4,
        total_missing_in_base=1,
        total_mismatches=2,
        keys_always_missing=["DB_URL"],
        keys_always_mismatched=["APP_ENV"],
    )


def test_text_contains_header(clean_summary):
    out = format_summary_text(clean_summary, color=False)
    assert "Diff Summary" in out


def test_text_shows_total_pairs(dirty_summary):
    out = format_summary_text(dirty_summary, color=False)
    assert "3" in out


def test_text_shows_always_missing(dirty_summary):
    out = format_summary_text(dirty_summary, color=False)
    assert "DB_URL" in out


def test_text_shows_always_mismatched(dirty_summary):
    out = format_summary_text(dirty_summary, color=False)
    assert "APP_ENV" in out


def test_text_no_always_missing_section_when_empty(clean_summary):
    out = format_summary_text(clean_summary, color=False)
    assert "Keys missing in ALL" not in out


def test_json_is_valid(dirty_summary):
    raw = format_summary_json(dirty_summary)
    data = json.loads(raw)
    assert data["total_pairs"] == 3
    assert data["pairs_with_differences"] == 2
    assert "DB_URL" in data["keys_always_missing"]


def test_print_summary_report_text(dirty_summary):
    buf = io.StringIO()
    print_summary_report(dirty_summary, fmt="text", color=False, out=buf)
    assert "Diff Summary" in buf.getvalue()


def test_print_summary_report_json(dirty_summary):
    buf = io.StringIO()
    print_summary_report(dirty_summary, fmt="json", out=buf)
    data = json.loads(buf.getvalue())
    assert "total_issues" in data


def test_print_summary_report_invalid_fmt(dirty_summary):
    """Passing an unsupported format should raise a ValueError."""
    buf = io.StringIO()
    with pytest.raises(ValueError, match="fmt"):
        print_summary_report(dirty_summary, fmt="xml", out=buf)
