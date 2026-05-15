"""Tests for envdiff.classify_reporter."""

import json
import pytest
from envdiff.classifier import classify_env
from envdiff.classify_reporter import (
    format_classify_text,
    format_classify_json,
    format_classify_comparison,
)


@pytest.fixture
def result():
    env = {
        "DB_PASSWORD": "secret123",
        "API_URL": "https://api.example.com",
        "APP_PORT": "3000",
        "UNKNOWN_KEY": "somevalue",
    }
    return classify_env(env, source="staging")


def test_text_contains_source(result):
    text = format_classify_text(result, color=False)
    assert "staging" in text


def test_text_shows_secret_category(result):
    text = format_classify_text(result, color=False)
    assert "SECRET" in text
    assert "DB_PASSWORD" in text


def test_text_shows_url_category(result):
    text = format_classify_text(result, color=False)
    assert "URL" in text
    assert "API_URL" in text


def test_text_shows_port_category(result):
    text = format_classify_text(result, color=False)
    assert "PORT" in text
    assert "APP_PORT" in text


def test_text_shows_unknown_category(result):
    text = format_classify_text(result, color=False)
    assert "UNKNOWN" in text
    assert "UNKNOWN_KEY" in text


def test_json_has_source(result):
    data = json.loads(format_classify_json(result))
    assert data["source"] == "staging"


def test_json_has_categories(result):
    data = json.loads(format_classify_json(result))
    assert "categories" in data
    assert "secret" in data["categories"]


def test_json_has_counts(result):
    data = json.loads(format_classify_json(result))
    assert "counts" in data
    total = sum(data["counts"].values())
    assert total == 4


def test_comparison_includes_both_sources():
    r1 = classify_env({"SECRET_KEY": "abc"}, source="dev")
    r2 = classify_env({"API_URL": "https://x.com"}, source="prod")
    text = format_classify_comparison([r1, r2], color=False)
    assert "dev" in text
    assert "prod" in text


def test_empty_result_text():
    r = classify_env({}, source="empty")
    text = format_classify_text(r, color=False)
    assert "no keys" in text
