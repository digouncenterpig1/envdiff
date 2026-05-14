"""Tests for envdiff.interpolator."""
import pytest
from envdiff.interpolator import (
    InterpolateResult,
    _refs_in,
    _substitute,
    interpolate_env,
)


def test_refs_in_curly_syntax():
    assert _refs_in("${HOST}:${PORT}") == ["HOST", "PORT"]


def test_refs_in_bare_syntax():
    assert _refs_in("$HOST:$PORT") == ["HOST", "PORT"]


def test_refs_in_no_refs():
    assert _refs_in("plain_value") == []


def test_substitute_resolves_known_ref():
    assert _substitute("${PROTO}://localhost", {"PROTO": "https"}) == "https://localhost"


def test_substitute_leaves_unknown_ref():
    assert _substitute("${MISSING}", {}) == "${MISSING}"


def test_interpolate_simple_reference():
    env = {"HOST": "localhost", "URL": "http://${HOST}/api"}
    result = interpolate_env(env, source="test")
    assert result.resolved["URL"] == "http://localhost/api"
    assert not result.has_unresolved


def test_interpolate_chain():
    env = {"A": "hello", "B": "${A}_world", "C": "${B}!"}
    result = interpolate_env(env)
    assert result.resolved["C"] == "hello_world!"


def test_interpolate_unresolved_ref_recorded():
    env = {"URL": "http://${UNKNOWN_HOST}/path"}
    result = interpolate_env(env)
    assert result.has_unresolved
    assert "URL" in result.unresolved_refs
    assert "UNKNOWN_HOST" in result.unresolved_refs["URL"]


def test_interpolate_unresolved_count():
    env = {"A": "${X}", "B": "${Y}/${Z}"}
    result = interpolate_env(env)
    assert result.unresolved_count == 3


def test_interpolate_no_refs_passes_through():
    env = {"KEY": "value", "OTHER": "123"}
    result = interpolate_env(env)
    assert result.resolved == env
    assert not result.has_unresolved


def test_interpolate_source_stored():
    result = interpolate_env({}, source="staging.env")
    assert result.source == "staging.env"


def test_interpolate_empty_env():
    result = interpolate_env({})
    assert result.resolved == {}
    assert result.unresolved_count == 0
