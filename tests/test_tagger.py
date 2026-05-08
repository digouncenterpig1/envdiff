"""Tests for envdiff.tagger."""

import pytest

from envdiff.tagger import TagResult, tag_env, tags_for_key


@pytest.fixture
def sample_env():
    return {
        "DATABASE_URL": "postgres://localhost/mydb",
        "API_SECRET": "s3cr3t",
        "DEBUG": "true",
        "MAX_RETRIES": "5",
        "DESCRIPTION": "some plain text",
        "EMPTY_VAR": "",
    }


def test_url_tag_detected(sample_env):
    result = tag_env(sample_env)
    assert "url" in result.tags["DATABASE_URL"]


def test_secret_tag_detected(sample_env):
    result = tag_env(sample_env)
    assert "secret" in result.tags["API_SECRET"]


def test_flag_tag_detected(sample_env):
    result = tag_env(sample_env)
    assert "flag" in result.tags["DEBUG"]


def test_numeric_tag_detected(sample_env):
    result = tag_env(sample_env)
    assert "numeric" in result.tags["MAX_RETRIES"]


def test_plain_tag_for_untagged_key(sample_env):
    result = tag_env(sample_env)
    assert "plain" in result.tags["DESCRIPTION"]


def test_empty_tag_detected(sample_env):
    result = tag_env(sample_env)
    assert "empty" in result.tags["EMPTY_VAR"]


def test_source_stored():
    result = tag_env({}, source="prod.env")
    assert result.source == "prod.env"


def test_keys_with_tag(sample_env):
    result = tag_env(sample_env)
    numeric_keys = result.keys_with_tag("numeric")
    assert "MAX_RETRIES" in numeric_keys


def test_all_tags_returns_union(sample_env):
    result = tag_env(sample_env)
    all_t = result.all_tags()
    assert "secret" in all_t
    assert "url" in all_t
    assert "flag" in all_t


def test_tags_for_key_standalone():
    tags = tags_for_key("AUTH_TOKEN", "abc123")
    assert "secret" in tags


def test_empty_env_produces_no_tags():
    result = tag_env({})
    assert result.tags == {}
