"""Tests for envdiff.profiler."""
import pytest

from envdiff.profiler import profile_env_string, _detect_secret_hint, _extract_prefix


SIMPLE = """
DB_HOST=localhost
DB_PORT=5432
DB_PASSWORD=secret123
APP_NAME=myapp
APP_ENV=production
EMPTY_VAL=
"""


def test_total_keys():
    p = profile_env_string(SIMPLE)
    assert p.total_keys == 6


def test_empty_values_detected():
    p = profile_env_string(SIMPLE)
    assert "EMPTY_VAL" in p.empty_values
    assert p.empty_count == 1


def test_top_prefix_detected():
    p = profile_env_string(SIMPLE)
    # DB and APP both appear twice, top_prefix is one of them
    assert p.top_prefix in ("DB", "APP")


def test_prefix_counts():
    p = profile_env_string(SIMPLE)
    assert p.prefixes.get("DB") == 3
    assert p.prefixes.get("APP") == 2


def test_secrets_hint_detected():
    p = profile_env_string(SIMPLE)
    assert p.has_secrets_hint is True


def test_no_secrets_hint():
    content = "FOO=bar\nBAZ=qux\n"
    p = profile_env_string(content)
    assert p.has_secrets_hint is False


def test_longest_key():
    content = "SHORT=1\nMUCH_LONGER_KEY=2\nX=3\n"
    p = profile_env_string(content)
    assert p.longest_key == "MUCH_LONGER_KEY"


def test_label_stored():
    p = profile_env_string("A=1", label="staging.env")
    assert p.source == "staging.env"


def test_extract_prefix_with_underscore():
    assert _extract_prefix("DB_HOST") == "DB"


def test_extract_prefix_no_underscore():
    assert _extract_prefix("HOSTNAME") is None


def test_detect_secret_hint_positive():
    assert _detect_secret_hint(["DB_PASSWORD", "HOST"]) is True


def test_detect_secret_hint_negative():
    assert _detect_secret_hint(["HOST", "PORT", "NAME"]) is False
