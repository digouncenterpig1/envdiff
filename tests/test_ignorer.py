"""Tests for envdiff.ignorer and envdiff.ignore_reporter."""
from __future__ import annotations

from pathlib import Path

import pytest

from envdiff.comparator import DiffResult
from envdiff.ignorer import apply_ignore, ignored_keys, load_ignore_patterns
from envdiff.ignore_reporter import format_ignore_summary_text


@pytest.fixture()
def base_result() -> DiffResult:
    return DiffResult(
        missing_in_target={"DB_HOST": "localhost", "SECRET_KEY": "abc"},
        missing_in_base={"NEW_FEATURE": "1"},
        mismatches={"APP_ENV": ("dev", "prod"), "DEBUG": ("true", "false")},
    )


def test_apply_ignore_removes_exact_match(base_result):
    filtered = apply_ignore(base_result, ["DB_HOST"])
    assert "DB_HOST" not in filtered.missing_in_target
    assert "SECRET_KEY" in filtered.missing_in_target


def test_apply_ignore_wildcard(base_result):
    filtered = apply_ignore(base_result, ["SECRET_*"])
    assert "SECRET_KEY" not in filtered.missing_in_target
    assert "DB_HOST" in filtered.missing_in_target


def test_apply_ignore_removes_from_mismatches(base_result):
    filtered = apply_ignore(base_result, ["APP_ENV"])
    assert "APP_ENV" not in filtered.mismatches
    assert "DEBUG" in filtered.mismatches


def test_apply_ignore_removes_from_missing_in_base(base_result):
    filtered = apply_ignore(base_result, ["NEW_*"])
    assert "NEW_FEATURE" not in filtered.missing_in_base


def test_apply_ignore_empty_patterns_returns_same(base_result):
    filtered = apply_ignore(base_result, [])
    assert filtered.missing_in_target == base_result.missing_in_target
    assert filtered.mismatches == base_result.mismatches


def test_ignored_keys_returns_correct_set(base_result):
    skipped = ignored_keys(base_result, ["DB_HOST", "APP_ENV"])
    assert skipped == {"DB_HOST", "APP_ENV"}


def test_ignored_keys_wildcard(base_result):
    skipped = ignored_keys(base_result, ["*_KEY"])
    assert "SECRET_KEY" in skipped


def test_ignored_keys_no_match(base_result):
    skipped = ignored_keys(base_result, ["DOES_NOT_EXIST"])
    assert skipped == set()


def test_load_ignore_patterns(tmp_path: Path):
    ignore_file = tmp_path / ".envignore"
    ignore_file.write_text("# comment\nDB_*\nSECRET_KEY\n\n  SPACED  \n")
    patterns = load_ignore_patterns(ignore_file)
    assert patterns == ["DB_*", "SECRET_KEY", "SPACED"]


def test_load_ignore_patterns_empty_file(tmp_path: Path):
    f = tmp_path / ".envignore"
    f.write_text("# only comments\n\n")
    assert load_ignore_patterns(f) == []


def test_format_ignore_summary_text_lists_skipped(base_result):
    text = format_ignore_summary_text(base_result, ["DB_HOST"], color=False)
    assert "DB_HOST" in text
    assert "Skipped 1 key" in text


def test_format_ignore_summary_no_patterns(base_result):
    text = format_ignore_summary_text(base_result, [], color=False)
    assert "No ignore patterns configured" in text


def test_format_ignore_summary_remaining_count(base_result):
    text = format_ignore_summary_text(base_result, ["DB_HOST", "APP_ENV"], color=False)
    # original: 2 missing_in_target, 1 missing_in_base, 2 mismatches = 5
    # after removing DB_HOST and APP_ENV: 1 + 1 + 1 = 3
    assert "Remaining differences after ignore: 3" in text
