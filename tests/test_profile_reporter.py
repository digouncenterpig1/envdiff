"""Tests for envdiff.profile_reporter."""
import json
import pytest

from envdiff.profiler import profile_env_string
from envdiff.profile_reporter import (
    format_profile_text,
    format_profile_json,
    format_profiles_comparison,
)


CONTENT = "DB_HOST=localhost\nDB_PASS=secret\nAPP_NAME=test\nEMPTY=\n"


@pytest.fixture
def profile():
    return profile_env_string(CONTENT, label="test.env")


def test_text_contains_source(profile):
    out = format_profile_text(profile)
    assert "test.env" in out


def test_text_shows_total_keys(profile):
    out = format_profile_text(profile)
    assert "4" in out


def test_text_shows_empty_count(profile):
    out = format_profile_text(profile)
    assert "Empty" in out
    assert "EMPTY" in out


def test_text_shows_secrets_hint(profile):
    out = format_profile_text(profile)
    assert "yes" in out


def test_json_is_valid(profile):
    raw = format_profile_json(profile)
    data = json.loads(raw)
    assert data["source"] == "test.env"
    assert data["total_keys"] == 4
    assert data["empty_count"] == 1
    assert "EMPTY" in data["empty_keys"]
    assert data["has_secrets_hint"] is True


def test_json_contains_prefixes(profile):
    raw = format_profile_json(profile)
    data = json.loads(raw)
    assert "DB" in data["prefixes"]


def test_comparison_combines_profiles():
    p1 = profile_env_string("A=1\nB=2\n", label="base.env")
    p2 = profile_env_string("C=3\n", label="prod.env")
    out = format_profiles_comparison([p1, p2])
    assert "base.env" in out
    assert "prod.env" in out
