"""Tests for envdiff.group_reporter."""
import json
import pytest
from envdiff.grouper import group_by_prefix
from envdiff.group_reporter import (
    format_group_text,
    format_group_json,
    format_groups_comparison,
)


@pytest.fixture
def result():
    env = {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "AWS_KEY": "abc",
        "AWS_SECRET": "xyz",
        "PORT": "8080",
    }
    return group_by_prefix(env, source="staging")


def test_text_contains_source(result):
    text = format_group_text(result, color=False)
    assert "staging" in text


def test_text_shows_group_names(result):
    text = format_group_text(result, color=False)
    assert "[DB]" in text
    assert "[AWS]" in text


def test_text_shows_ungrouped(result):
    text = format_group_text(result, color=False)
    assert "ungrouped" in text
    assert "PORT" in text


def test_text_shows_key_count(result):
    text = format_group_text(result, color=False)
    assert str(result.key_count()) in text


def test_json_valid_structure(result):
    raw = format_group_json(result)
    data = json.loads(raw)
    assert data["source"] == "staging"
    assert "groups" in data
    assert "ungrouped" in data
    assert data["total_groups"] == result.total_groups()


def test_json_groups_contain_keys(result):
    data = json.loads(format_group_json(result))
    assert "DB_HOST" in data["groups"]["DB"]
    assert "AWS_KEY" in data["groups"]["AWS"]


def test_comparison_contains_both_sources():
    env1 = {"DB_HOST": "a", "DB_PORT": "b", "X": "1"}
    env2 = {"APP_NAME": "foo", "APP_ENV": "prod", "Y": "2"}
    r1 = group_by_prefix(env1, source="base")
    r2 = group_by_prefix(env2, source="target")
    text = format_groups_comparison([r1, r2], color=False)
    assert "base" in text
    assert "target" in text
