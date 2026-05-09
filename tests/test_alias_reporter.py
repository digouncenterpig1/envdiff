"""Tests for envdiff.alias_reporter."""
import json
import pytest
from envdiff.aliaser import AliasResult
from envdiff.alias_reporter import format_alias_text, format_alias_json


@pytest.fixture()
def result():
    return AliasResult(
        source="prod.env",
        aliases={"OLD_DB": "DATABASE_URL", "OLD_SECRET": "APP_SECRET"},
        resolved={"DATABASE_URL": "postgres://localhost/db"},
        stale=["APP_SECRET"],
        unknown=["DEBUG"],
    )


def test_text_contains_source(result):
    out = format_alias_text(result)
    assert "prod.env" in out


def test_text_shows_resolved_key(result):
    out = format_alias_text(result)
    assert "DATABASE_URL" in out


def test_text_shows_stale_key(result):
    out = format_alias_text(result)
    assert "APP_SECRET" in out


def test_text_shows_unknown_key(result):
    out = format_alias_text(result)
    assert "DEBUG" in out


def test_json_valid_structure(result):
    raw = format_alias_json(result)
    data = json.loads(raw)
    assert data["source"] == "prod.env"
    assert "DATABASE_URL" in data["resolved"]
    assert "APP_SECRET" in data["stale"]
    assert "DEBUG" in data["unknown"]


def test_json_aliases_present(result):
    data = json.loads(format_alias_json(result))
    assert data["aliases"]["OLD_DB"] == "DATABASE_URL"


def test_text_empty_stale_no_stale_section():
    r = AliasResult(
        source="dev.env",
        aliases={},
        resolved={},
        stale=[],
        unknown=[],
    )
    out = format_alias_text(r)
    assert "Stale" not in out or "0" in out
