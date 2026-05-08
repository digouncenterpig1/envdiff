"""Tests for envdiff.tag_reporter."""

import json

import pytest

from envdiff.tagger import tag_env
from envdiff.tag_reporter import (
    format_tag_text,
    format_tag_json,
    format_tags_comparison,
)


@pytest.fixture
def result():
    env = {
        "API_KEY": "secret123",
        "PORT": "8080",
        "VERBOSE": "false",
        "NOTES": "hello world",
    }
    return tag_env(env, source="test.env")


def test_text_contains_source(result):
    text = format_tag_text(result)
    assert "test.env" in text


def test_text_lists_keys(result):
    text = format_tag_text(result)
    assert "API_KEY" in text
    assert "PORT" in text


def test_text_shows_tag_labels(result):
    text = format_tag_text(result)
    assert "secret" in text
    assert "numeric" in text


def test_text_empty_env():
    empty = tag_env({}, source="empty.env")
    text = format_tag_text(empty)
    assert "(no keys)" in text


def test_json_valid_structure(result):
    raw = format_tag_json(result)
    data = json.loads(raw)
    assert data["source"] == "test.env"
    assert "API_KEY" in data["tags"]
    assert isinstance(data["tags"]["API_KEY"], list)


def test_json_tags_are_sorted(result):
    raw = format_tag_json(result)
    data = json.loads(raw)
    for tags in data["tags"].values():
        assert tags == sorted(tags)


def test_comparison_joins_multiple_results():
    r1 = tag_env({"A": "1"}, source="a.env")
    r2 = tag_env({"B": "2"}, source="b.env")
    text = format_tags_comparison([r1, r2])
    assert "a.env" in text
    assert "b.env" in text
