"""Tests for envdiff.templater and envdiff.template_reporter."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from envdiff.templater import (
    EnvTemplate,
    _make_placeholder,
    build_template,
    template_from_file,
    template_from_string,
    write_template,
)
from envdiff.template_reporter import format_template_json, format_template_text


# ---------------------------------------------------------------------------
# _make_placeholder
# ---------------------------------------------------------------------------

def test_placeholder_empty_value_stays_empty():
    assert _make_placeholder("SOME_KEY", "") == ""


def test_placeholder_secret_key_returns_secret_hint():
    assert _make_placeholder("DB_PASSWORD", "hunter2") == "<secret>"


def test_placeholder_token_key_returns_secret_hint():
    assert _make_placeholder("API_TOKEN", "abc123") == "<secret>"


def test_placeholder_normal_key_returns_value_hint():
    assert _make_placeholder("APP_HOST", "localhost") == "<value>"


# ---------------------------------------------------------------------------
# build_template / template_from_string
# ---------------------------------------------------------------------------

def test_keys_order_preserved():
    env = {"Z_KEY": "1", "A_KEY": "2", "M_KEY": "3"}
    tmpl = build_template(env)
    assert tmpl.keys == ["Z_KEY", "A_KEY", "M_KEY"]


def test_preserve_values_flag():
    env = {"HOST": "localhost", "PORT": "5432"}
    tmpl = build_template(env, preserve_values=True)
    assert tmpl.placeholders["HOST"] == "localhost"
    assert tmpl.placeholders["PORT"] == "5432"


def test_template_from_string_basic():
    content = "HOST=localhost\nPORT=5432\nSECRET_KEY=supersecret\n"
    tmpl = template_from_string(content)
    assert "HOST" in tmpl.keys
    assert tmpl.placeholders["HOST"] == "<value>"
    assert tmpl.placeholders["SECRET_KEY"] == "<secret>"


def test_template_to_string_format():
    tmpl = EnvTemplate(keys=["A", "B"], placeholders={"A": "<value>", "B": ""})
    result = tmpl.to_string()
    assert "A=<value>" in result
    assert "B=" in result


# ---------------------------------------------------------------------------
# template_from_file / write_template
# ---------------------------------------------------------------------------

def test_template_from_file(tmp_path: Path):
    env_file = tmp_path / ".env"
    env_file.write_text("DB_HOST=db\nDB_PASSWORD=secret\n")
    tmpl = template_from_file(env_file)
    assert tmpl.source == str(env_file)
    assert tmpl.placeholders["DB_PASSWORD"] == "<secret>"
    assert tmpl.placeholders["DB_HOST"] == "<value>"


def test_write_template_creates_file(tmp_path: Path):
    tmpl = EnvTemplate(keys=["FOO"], placeholders={"FOO": "<value>"})
    dest = tmp_path / "subdir" / ".env.example"
    write_template(tmpl, dest)
    assert dest.exists()
    assert "FOO=<value>" in dest.read_text()


# ---------------------------------------------------------------------------
# reporters
# ---------------------------------------------------------------------------

def test_format_template_text_contains_key():
    tmpl = template_from_string("MY_VAR=hello\n")
    text = format_template_text(tmpl, color=False)
    assert "MY_VAR" in text


def test_format_template_json_valid():
    tmpl = template_from_string("X=1\nY=2\n")
    data = json.loads(format_template_json(tmpl))
    assert "keys" in data
    assert "placeholders" in data
    assert "X" in data["keys"]
