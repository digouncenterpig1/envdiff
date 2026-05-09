"""Tests for envdiff.trimmer."""

import pytest
from envdiff.trimmer import trim_to_reference, trim_keys, TrimResult


@pytest.fixture
def sample_env() -> dict:
    return {
        "APP_HOST": "localhost",
        "APP_PORT": "8080",
        "DB_URL": "postgres://localhost/db",
        "SECRET_KEY": "abc123",
        "DEBUG": "true",
    }


def test_trim_to_reference_keeps_matching_keys(sample_env):
    reference = {"APP_HOST": "prod", "APP_PORT": "443"}
    result = trim_to_reference(sample_env, reference, source="test.env")
    assert "APP_HOST" in result.trimmed
    assert "APP_PORT" in result.trimmed


def test_trim_to_reference_removes_extra_keys(sample_env):
    reference = {"APP_HOST": "prod"}
    result = trim_to_reference(sample_env, reference, source="test.env")
    assert "DB_URL" not in result.trimmed
    assert "SECRET_KEY" not in result.trimmed
    assert "DEBUG" not in result.trimmed


def test_trim_to_reference_removed_keys_sorted(sample_env):
    reference = {"APP_HOST": "x"}
    result = trim_to_reference(sample_env, reference)
    assert result.removed_keys == sorted(result.removed_keys)


def test_trim_to_reference_has_removals_true(sample_env):
    reference = {"APP_HOST": "x"}
    result = trim_to_reference(sample_env, reference)
    assert result.has_removals is True


def test_trim_to_reference_has_removals_false(sample_env):
    result = trim_to_reference(sample_env, sample_env)
    assert result.has_removals is False
    assert result.removal_count == 0


def test_trim_to_reference_original_unchanged(sample_env):
    reference = {"APP_HOST": "x"}
    result = trim_to_reference(sample_env, reference)
    assert result.original == sample_env


def test_trim_keys_removes_specified(sample_env):
    result = trim_keys(sample_env, ["SECRET_KEY", "DEBUG"], source="local.env")
    assert "SECRET_KEY" not in result.trimmed
    assert "DEBUG" not in result.trimmed
    assert "APP_HOST" in result.trimmed


def test_trim_keys_missing_key_ignored(sample_env):
    result = trim_keys(sample_env, ["NONEXISTENT"])
    assert result.removal_count == 0
    assert result.trimmed == sample_env


def test_trim_keys_source_stored(sample_env):
    result = trim_keys(sample_env, [], source="staging.env")
    assert result.source == "staging.env"


def test_as_env_string_format(sample_env):
    result = trim_keys(sample_env, ["DEBUG", "SECRET_KEY"])
    env_str = result.as_env_string()
    lines = env_str.splitlines()
    assert all("=" in line for line in lines)
    assert not any(line.startswith("DEBUG") for line in lines)


def test_removal_count_matches_removed_keys(sample_env):
    result = trim_keys(sample_env, ["APP_HOST", "APP_PORT"])
    assert result.removal_count == len(result.removed_keys) == 2
