"""Tests for envdiff.renamer and envdiff.rename_reporter."""

import json
import pytest

from envdiff.renamer import rename_key, rename_keys, rename_by_pattern, RenameResult
from envdiff.rename_reporter import format_rename_text, format_rename_json


@pytest.fixture
def env():
    return {
        "APP_HOST": "localhost",
        "APP_PORT": "8080",
        "DB_URL": "postgres://localhost/db",
        "SECRET_KEY": "abc123",
    }


# --- rename_key ---

def test_rename_key_success(env):
    result = rename_key(env, "APP_HOST", "HOST")
    assert "HOST" in result.env
    assert "APP_HOST" not in result.env
    assert result.renamed == {"APP_HOST": "HOST"}
    assert result.skipped == []


def test_rename_key_missing(env):
    result = rename_key(env, "MISSING", "NEW_KEY")
    assert "NEW_KEY" not in result.env
    assert "MISSING" in result.skipped
    assert result.renamed == {}


def test_rename_key_preserves_value(env):
    result = rename_key(env, "APP_PORT", "PORT")
    assert result.env["PORT"] == "8080"


# --- rename_keys ---

def test_rename_keys_multiple(env):
    result = rename_keys(env, {"APP_HOST": "HOST", "APP_PORT": "PORT"})
    assert "HOST" in result.env
    assert "PORT" in result.env
    assert "APP_HOST" not in result.env
    assert "APP_PORT" not in result.env
    assert len(result.renamed) == 2


def test_rename_keys_partial_missing(env):
    result = rename_keys(env, {"APP_HOST": "HOST", "NOPE": "ALSO_NOPE"})
    assert "HOST" in result.env
    assert "NOPE" in result.skipped
    assert len(result.renamed) == 1


# --- rename_by_pattern ---

def test_rename_by_pattern_add_prefix(env):
    result = rename_by_pattern(env, "APP_*", prefix="NEW_")
    assert "NEW_APP_HOST" in result.env
    assert "NEW_APP_PORT" in result.env
    assert "APP_HOST" not in result.env


def test_rename_by_pattern_strip_prefix(env):
    result = rename_by_pattern(env, "APP_*", strip_prefix="APP_")
    assert "HOST" in result.env
    assert "PORT" in result.env
    assert "APP_HOST" not in result.env


def test_rename_by_pattern_no_match(env):
    result = rename_by_pattern(env, "NONEXISTENT_*", prefix="X_")
    assert result.renamed == {}
    assert result.env == env


def test_rename_by_pattern_requires_operation(env):
    with pytest.raises(ValueError):
        rename_by_pattern(env, "APP_*")


# --- reporter ---

def test_format_text_shows_renamed(env):
    result = rename_key(env, "APP_HOST", "HOST")
    text = format_rename_text(result, color=False)
    assert "APP_HOST" in text
    assert "HOST" in text


def test_format_text_shows_skipped():
    result = rename_key({"A": "1"}, "MISSING", "NEW")
    text = format_rename_text(result, color=False)
    assert "MISSING" in text


def test_format_json_structure(env):
    result = rename_keys(env, {"APP_HOST": "HOST"})
    data = json.loads(format_rename_json(result))
    assert "renamed" in data
    assert "skipped" in data
    assert data["total_renamed"] == 1
