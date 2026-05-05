"""Tests for envdiff.filter module."""

import pytest

from envdiff.comparator import DiffResult
from envdiff.filter import (
    exclude_keys,
    filter_by_pattern,
    filter_by_type,
    filter_keys,
)


@pytest.fixture()
def sample_result() -> DiffResult:
    return DiffResult(
        missing_in_target={"DB_HOST": "localhost", "DB_PORT": "5432"},
        missing_in_base={"NEW_FEATURE_FLAG": "true"},
        mismatches={"APP_ENV": ("development", "production"), "LOG_LEVEL": ("debug", "info")},
    )


def test_filter_by_pattern_prefix(sample_result):
    filtered = filter_by_pattern(sample_result, "DB_*")
    assert set(filtered.missing_in_target.keys()) == {"DB_HOST", "DB_PORT"}
    assert filtered.missing_in_base == {}
    assert filtered.mismatches == {}


def test_filter_by_pattern_no_match(sample_result):
    filtered = filter_by_pattern(sample_result, "REDIS_*")
    assert filtered.missing_in_target == {}
    assert filtered.missing_in_base == {}
    assert filtered.mismatches == {}


def test_filter_by_pattern_wildcard_all(sample_result):
    filtered = filter_by_pattern(sample_result, "*")
    assert filtered.missing_in_target == sample_result.missing_in_target
    assert filtered.missing_in_base == sample_result.missing_in_base
    assert filtered.mismatches == sample_result.mismatches


def test_filter_by_type_only_mismatches(sample_result):
    filtered = filter_by_type(
        sample_result,
        include_missing_in_target=False,
        include_missing_in_base=False,
        include_mismatches=True,
    )
    assert filtered.missing_in_target == {}
    assert filtered.missing_in_base == {}
    assert filtered.mismatches == sample_result.mismatches


def test_filter_by_type_exclude_mismatches(sample_result):
    filtered = filter_by_type(sample_result, include_mismatches=False)
    assert filtered.mismatches == {}
    assert filtered.missing_in_target == sample_result.missing_in_target
    assert filtered.missing_in_base == sample_result.missing_in_base


def test_filter_keys_subset(sample_result):
    filtered = filter_keys(sample_result, ["DB_HOST", "APP_ENV"])
    assert filtered.missing_in_target == {"DB_HOST": "localhost"}
    assert filtered.mismatches == {"APP_ENV": ("development", "production")}
    assert filtered.missing_in_base == {}


def test_filter_keys_empty_list(sample_result):
    filtered = filter_keys(sample_result, [])
    assert filtered.missing_in_target == {}
    assert filtered.missing_in_base == {}
    assert filtered.mismatches == {}


def test_exclude_keys_removes_specified(sample_result):
    filtered = exclude_keys(sample_result, ["DB_HOST", "LOG_LEVEL", "NEW_FEATURE_FLAG"])
    assert "DB_HOST" not in filtered.missing_in_target
    assert "DB_PORT" in filtered.missing_in_target
    assert filtered.missing_in_base == {}
    assert "LOG_LEVEL" not in filtered.mismatches
    assert "APP_ENV" in filtered.mismatches


def test_exclude_keys_nonexistent_key(sample_result):
    filtered = exclude_keys(sample_result, ["DOES_NOT_EXIST"])
    assert filtered.missing_in_target == sample_result.missing_in_target
    assert filtered.missing_in_base == sample_result.missing_in_base
    assert filtered.mismatches == sample_result.mismatches
