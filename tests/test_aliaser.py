"""Tests for envdiff.aliaser."""
import pytest
from envdiff.aliaser import apply_aliases, load_aliases


@pytest.fixture()
def env():
    return {
        "DATABASE_URL": "postgres://localhost/db",
        "APP_SECRET": "s3cr3t",
        "DEBUG": "true",
    }


def test_resolved_when_new_key_exists(env):
    aliases = {"DB_URL": "DATABASE_URL", "SECRET": "APP_SECRET"}
    result = apply_aliases(env, aliases, source="prod.env")
    assert "DATABASE_URL" in result.resolved
    assert "APP_SECRET" in result.resolved
    assert result.total_resolved() == 2


def test_stale_when_new_key_missing(env):
    aliases = {"OLD_HOST": "DB_HOST"}  # DB_HOST not in env
    result = apply_aliases(env, aliases)
    assert "DB_HOST" in result.stale
    assert result.has_stale()


def test_unknown_keys_collected(env):
    aliases = {"DB_URL": "DATABASE_URL"}  # APP_SECRET and DEBUG not aliased
    result = apply_aliases(env, aliases)
    assert "APP_SECRET" in result.unknown
    assert "DEBUG" in result.unknown


def test_no_stale_when_all_resolve(env):
    aliases = {
        "DB_URL": "DATABASE_URL",
        "SECRET": "APP_SECRET",
        "DBG": "DEBUG",
    }
    result = apply_aliases(env, aliases)
    assert not result.has_stale()
    assert result.stale == []


def test_source_stored(env):
    result = apply_aliases(env, {}, source="staging.env")
    assert result.source == "staging.env"


def test_empty_env_all_stale():
    aliases = {"OLD": "NEW_KEY"}
    result = apply_aliases({}, aliases)
    assert "NEW_KEY" in result.stale
    assert result.total_resolved() == 0


def test_load_aliases_strips_whitespace():
    raw = {"  OLD  ": "  NEW  "}
    cleaned = load_aliases(raw)
    assert "OLD" in cleaned
    assert cleaned["OLD"] == "NEW"


def test_load_aliases_drops_empty_entries():
    raw = {"": "NEW", "OLD": ""}
    cleaned = load_aliases(raw)
    assert cleaned == {}
