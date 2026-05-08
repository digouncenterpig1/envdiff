"""Tests for envdiff.grouper."""
import pytest
from envdiff.grouper import (
    GroupResult,
    group_by_prefix,
    group_by_custom,
    _extract_prefix,
)


@pytest.fixture
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "mydb",
        "AWS_KEY": "abc",
        "AWS_SECRET": "xyz",
        "PORT": "8080",
        "DEBUG": "true",
    }


def test_extract_prefix_with_separator():
    assert _extract_prefix("DB_HOST") == "DB"


def test_extract_prefix_no_separator():
    assert _extract_prefix("PORT") is None


def test_group_by_prefix_creates_groups(sample_env):
    result = group_by_prefix(sample_env, source="test")
    assert "DB" in result.groups
    assert "AWS" in result.groups


def test_group_by_prefix_correct_keys(sample_env):
    result = group_by_prefix(sample_env, source="test")
    assert sorted(result.groups["DB"]) == ["DB_HOST", "DB_NAME", "DB_PORT"]
    assert sorted(result.groups["AWS"]) == ["AWS_KEY", "AWS_SECRET"]


def test_group_by_prefix_ungrouped_keys(sample_env):
    result = group_by_prefix(sample_env, source="test")
    assert "PORT" in result.ungrouped
    assert "DEBUG" in result.ungrouped


def test_group_by_prefix_min_group_size(sample_env):
    result = group_by_prefix(sample_env, source="test", min_group_size=3)
    assert "DB" in result.groups
    assert "AWS" not in result.groups
    assert "AWS_KEY" in result.ungrouped
    assert "AWS_SECRET" in result.ungrouped


def test_total_groups(sample_env):
    result = group_by_prefix(sample_env, source="test")
    assert result.total_groups() == 2


def test_key_count(sample_env):
    result = group_by_prefix(sample_env, source="test")
    assert result.key_count() == len(sample_env)


def test_group_by_custom_rules(sample_env):
    rules = {"database": ["DB"], "cloud": ["AWS"]}
    result = group_by_custom(sample_env, rules=rules, source="test")
    assert "database" in result.groups
    assert "cloud" in result.groups
    assert sorted(result.groups["database"]) == ["DB_HOST", "DB_NAME", "DB_PORT"]


def test_group_by_custom_ungrouped(sample_env):
    rules = {"database": ["DB"]}
    result = group_by_custom(sample_env, rules=rules, source="test")
    assert "AWS_KEY" in result.ungrouped
    assert "PORT" in result.ungrouped


def test_group_names_sorted(sample_env):
    result = group_by_prefix(sample_env, source="test")
    assert result.group_names() == sorted(result.group_names())
