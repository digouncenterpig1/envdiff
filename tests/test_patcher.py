"""Tests for envdiff.patcher."""

import pytest
from pathlib import Path

from envdiff.patcher import patch_env_string, patch_env_file, write_patch


BASE_CONTENT = """APP_ENV=production
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=abc123
"""


def test_set_new_key_adds_to_added():
    result = patch_env_string(BASE_CONTENT, set_keys={"NEW_KEY": "hello"})
    assert "NEW_KEY" in result.added
    assert result.patched["NEW_KEY"] == "hello"


def test_set_existing_key_goes_to_updated():
    result = patch_env_string(BASE_CONTENT, set_keys={"DB_HOST": "remotehost"})
    assert "DB_HOST" in result.updated
    assert result.patched["DB_HOST"] == "remotehost"


def test_set_same_value_not_marked_updated():
    result = patch_env_string(BASE_CONTENT, set_keys={"DB_HOST": "localhost"})
    assert "DB_HOST" not in result.updated
    assert "DB_HOST" not in result.added


def test_unset_removes_key():
    result = patch_env_string(BASE_CONTENT, unset_keys=["DB_PORT"])
    assert "DB_PORT" in result.removed
    assert "DB_PORT" not in result.patched


def test_unset_missing_key_ignored():
    result = patch_env_string(BASE_CONTENT, unset_keys=["DOES_NOT_EXIST"])
    assert "DOES_NOT_EXIST" not in result.removed
    assert not result.has_changes()


def test_original_is_not_mutated():
    result = patch_env_string(BASE_CONTENT, set_keys={"X": "1"}, unset_keys=["DB_PORT"])
    assert "DB_PORT" in result.original
    assert "X" not in result.original


def test_has_changes_true():
    result = patch_env_string(BASE_CONTENT, set_keys={"NEW": "val"})
    assert result.has_changes()


def test_has_changes_false_when_no_ops():
    result = patch_env_string(BASE_CONTENT)
    assert not result.has_changes()


def test_as_env_string_contains_all_keys():
    result = patch_env_string(BASE_CONTENT, set_keys={"EXTRA": "yes"})
    env_str = result.as_env_string()
    assert "APP_ENV=production" in env_str
    assert "EXTRA=yes" in env_str


def test_value_with_spaces_gets_quoted():
    result = patch_env_string(BASE_CONTENT, set_keys={"GREETING": "hello world"})
    assert 'GREETING="hello world"' in result.as_env_string()


def test_patch_env_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(BASE_CONTENT)
    result = patch_env_file(str(env_file), set_keys={"NEW": "value"}, unset_keys=["DB_PORT"])
    assert "NEW" in result.added
    assert "DB_PORT" in result.removed
    assert result.source == str(env_file)


def test_write_patch_creates_file(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text(BASE_CONTENT)
    result = patch_env_file(str(env_file), set_keys={"WRITTEN": "yes"})
    out_file = tmp_path / ".env.patched"
    write_patch(result, str(out_file))
    content = out_file.read_text()
    assert "WRITTEN=yes" in content
    assert content.endswith("\n")
