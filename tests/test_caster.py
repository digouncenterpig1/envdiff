"""Tests for envdiff.caster and envdiff.cast_reporter."""
import json
import pytest

from envdiff.caster import cast_env, CastEntry, CastResult, _infer
from envdiff.cast_reporter import format_cast_text, format_cast_json, format_cast_comparison


@pytest.fixture
def sample_env():
    return {
        "PORT": "8080",
        "RATIO": "3.14",
        "DEBUG": "true",
        "DISABLED": "false",
        "NAME": "myapp",
        "EMPTY": "",
    }


def test_int_inferred(sample_env):
    result = cast_env(sample_env, source="test")
    port = next(e for e in result.entries if e.key == "PORT")
    assert port.inferred_type == "int"
    assert port.cast_value == 8080


def test_float_inferred(sample_env):
    result = cast_env(sample_env, source="test")
    ratio = next(e for e in result.entries if e.key == "RATIO")
    assert ratio.inferred_type == "float"
    assert ratio.cast_value == pytest.approx(3.14)


def test_bool_true_inferred(sample_env):
    result = cast_env(sample_env, source="test")
    debug = next(e for e in result.entries if e.key == "DEBUG")
    assert debug.inferred_type == "bool"
    assert debug.cast_value is True


def test_bool_false_inferred(sample_env):
    result = cast_env(sample_env, source="test")
    dis = next(e for e in result.entries if e.key == "DISABLED")
    assert dis.inferred_type == "bool"
    assert dis.cast_value is False


def test_string_inferred(sample_env):
    result = cast_env(sample_env, source="test")
    name = next(e for e in result.entries if e.key == "NAME")
    assert name.inferred_type == "string"
    assert name.cast_value == "myapp"


def test_empty_inferred(sample_env):
    result = cast_env(sample_env, source="test")
    empty = next(e for e in result.entries if e.key == "EMPTY")
    assert empty.inferred_type == "empty"
    assert empty.cast_value is None


def test_type_counts(sample_env):
    result = cast_env(sample_env, source="test")
    counts = result.type_counts
    assert counts["int"] == 1
    assert counts["float"] == 1
    assert counts["bool"] == 2
    assert counts["string"] == 1
    assert counts["empty"] == 1


def test_by_type_filter(sample_env):
    result = cast_env(sample_env, source="test")
    bools = result.by_type("bool")
    assert len(bools) == 2
    assert {e.key for e in bools} == {"DEBUG", "DISABLED"}


def test_as_dict(sample_env):
    result = cast_env(sample_env, source="test")
    d = result.as_dict()
    assert d["PORT"] == 8080
    assert d["EMPTY"] is None


def test_format_text_contains_source(sample_env):
    result = cast_env(sample_env, source="staging.env")
    text = format_cast_text(result)
    assert "staging.env" in text


def test_format_text_shows_keys(sample_env):
    result = cast_env(sample_env, source="test")
    text = format_cast_text(result)
    assert "PORT" in text
    assert "RATIO" in text


def test_format_json_valid(sample_env):
    result = cast_env(sample_env, source="test")
    raw = format_cast_json(result)
    data = json.loads(raw)
    assert data["source"] == "test"
    assert "entries" in data
    assert "type_counts" in data


def test_format_comparison_multiple():
    r1 = cast_env({"A": "1"}, source="a.env")
    r2 = cast_env({"B": "hello"}, source="b.env")
    text = format_cast_comparison([r1, r2])
    assert "a.env" in text
    assert "b.env" in text


def test_empty_env_format():
    result = cast_env({}, source="empty.env")
    text = format_cast_text(result)
    assert "(no keys)" in text
