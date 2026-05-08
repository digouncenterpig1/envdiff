"""Tests for envdiff.duplicator."""
import pytest

from envdiff.duplicator import DuplicateResult, find_duplicates, find_duplicates_in_file


@pytest.fixture
def sample_env():
    return {
        "DB_HOST": "localhost",
        "CACHE_HOST": "localhost",   # duplicate of DB_HOST
        "APP_KEY": "secret123",
        "BACKUP_KEY": "secret123",  # duplicate of APP_KEY
        "PORT": "8080",             # unique
        "EMPTY": "",                # ignored by default
        "EMPTY2": "",               # ignored by default
    }


def test_no_duplicates_returns_empty_result():
    env = {"A": "1", "B": "2", "C": "3"}
    result = find_duplicates(env, source="test")
    assert not result.has_duplicates
    assert result.total_groups == 0
    assert result.affected_keys == []


def test_duplicate_values_detected(sample_env):
    result = find_duplicates(sample_env, source="test.env")
    assert result.has_duplicates
    assert result.total_groups == 2


def test_correct_keys_grouped(sample_env):
    result = find_duplicates(sample_env, source="test.env")
    assert set(result.duplicates["localhost"]) == {"DB_HOST", "CACHE_HOST"}
    assert set(result.duplicates["secret123"]) == {"APP_KEY", "BACKUP_KEY"}


def test_affected_keys_lists_all_involved(sample_env):
    result = find_duplicates(sample_env, source="test.env")
    assert set(result.affected_keys) == {"DB_HOST", "CACHE_HOST", "APP_KEY", "BACKUP_KEY"}


def test_empty_values_ignored_by_default(sample_env):
    result = find_duplicates(sample_env, source="test.env")
    # EMPTY and EMPTY2 both have "" but should not appear
    for keys in result.duplicates.values():
        assert "EMPTY" not in keys
        assert "EMPTY2" not in keys


def test_empty_values_included_when_flag_false(sample_env):
    result = find_duplicates(sample_env, source="test.env", ignore_empty=False)
    assert "" in result.duplicates
    assert set(result.duplicates[""]) == {"EMPTY", "EMPTY2"}


def test_source_label_stored():
    result = find_duplicates({}, source="prod.env")
    assert result.source == "prod.env"


def test_find_duplicates_in_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("A=same\nB=same\nC=unique\n")
    result = find_duplicates_in_file(str(env_file))
    assert result.has_duplicates
    assert set(result.duplicates["same"]) == {"A", "B"}
    assert result.source == str(env_file)


def test_find_duplicates_in_file_no_dupes(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("X=1\nY=2\nZ=3\n")
    result = find_duplicates_in_file(str(env_file))
    assert not result.has_duplicates
