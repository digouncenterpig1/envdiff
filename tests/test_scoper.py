"""Tests for envdiff.scoper."""

import pytest
from envdiff.scoper import ScopeResult, available_scopes, scope_env


@pytest.fixture
def sample_env():
    return {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "REDIS_URL": "redis://localhost",
        "APP_SECRET": "supersecret",
        "APP_DEBUG": "true",
        "STANDALONE": "yes",
    }


def test_matched_keys_returned(sample_env):
    result = scope_env(sample_env, "DB", source="test.env")
    assert set(result.matched.keys()) == {"DB_HOST", "DB_PORT"}


def test_unmatched_keys_returned(sample_env):
    result = scope_env(sample_env, "DB", source="test.env")
    assert "REDIS_URL" in result.unmatched
    assert "APP_SECRET" in result.unmatched
    assert "STANDALONE" in result.unmatched


def test_has_matches_true(sample_env):
    result = scope_env(sample_env, "APP")
    assert result.has_matches is True


def test_has_matches_false(sample_env):
    result = scope_env(sample_env, "MISSING")
    assert result.has_matches is False


def test_match_count(sample_env):
    result = scope_env(sample_env, "APP")
    assert result.match_count == 2


def test_unmatched_count(sample_env):
    result = scope_env(sample_env, "DB")
    # 6 total - 2 DB = 4
    assert result.unmatched_count == 4


def test_source_stored(sample_env):
    result = scope_env(sample_env, "DB", source="prod.env")
    assert result.source == "prod.env"


def test_scope_stored(sample_env):
    result = scope_env(sample_env, "REDIS")
    assert result.scope == "REDIS"


def test_stripped_keys_removes_prefix(sample_env):
    result = scope_env(sample_env, "DB")
    stripped = result.stripped_keys()
    assert "HOST" in stripped
    assert "PORT" in stripped
    assert stripped["HOST"] == "localhost"


def test_case_insensitive_matching():
    env = {"db_host": "localhost", "DB_PORT": "5432", "OTHER": "x"}
    result = scope_env(env, "DB", case_sensitive=False)
    assert "db_host" in result.matched
    assert "DB_PORT" in result.matched


def test_case_sensitive_matching():
    env = {"db_host": "localhost", "DB_PORT": "5432"}
    result = scope_env(env, "DB", case_sensitive=True)
    assert "DB_PORT" in result.matched
    assert "db_host" not in result.matched


def test_available_scopes(sample_env):
    scopes = available_scopes(sample_env)
    assert "DB" in scopes
    assert "REDIS" in scopes
    assert "APP" in scopes


def test_available_scopes_excludes_no_separator():
    env = {"STANDALONE": "yes", "DB_HOST": "h"}
    scopes = available_scopes(env)
    assert "STANDALONE" not in scopes
    assert "DB" in scopes


def test_available_scopes_sorted():
    env = {"Z_KEY": "1", "A_KEY": "2", "M_KEY": "3"}
    scopes = available_scopes(env)
    assert scopes == sorted(scopes)
