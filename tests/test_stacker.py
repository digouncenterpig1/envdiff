"""Tests for envdiff.stacker."""
import pytest

from envdiff.stacker import (
    StackLayer,
    stack_envs,
    stack_env_strings,
)


def _layer(source: str, **kv) -> StackLayer:
    return StackLayer(source=source, env=dict(kv))


def test_no_layers_returns_empty():
    result = stack_envs([])
    assert result.resolved == {}
    assert not result.has_overrides()


def test_single_layer_resolved():
    result = stack_envs([_layer("base", FOO="bar", BAZ="qux")])
    assert result.resolved == {"FOO": "bar", "BAZ": "qux"}
    assert not result.has_overrides()


def test_later_layer_wins():
    layers = [
        _layer("base", FOO="base_val"),
        _layer("prod", FOO="prod_val"),
    ]
    result = stack_envs(layers)
    assert result.resolved["FOO"] == "prod_val"


def test_override_recorded():
    layers = [
        _layer("base", FOO="one"),
        _layer("prod", FOO="two"),
    ]
    result = stack_envs(layers)
    assert result.has_overrides()
    assert "FOO" in result.overrides
    assert result.override_count() == 1


def test_override_history_order():
    layers = [
        _layer("a", KEY="v1"),
        _layer("b", KEY="v2"),
        _layer("c", KEY="v3"),
    ]
    result = stack_envs(layers)
    hist = result.overrides["KEY"]
    assert [src for src, _ in hist] == ["a", "b", "c"]
    assert hist[-1][1] == "v3"


def test_non_overlapping_keys_no_override():
    layers = [
        _layer("base", FOO="1"),
        _layer("prod", BAR="2"),
    ]
    result = stack_envs(layers)
    assert not result.has_overrides()
    assert result.resolved == {"FOO": "1", "BAR": "2"}


def test_as_env_string_contains_all_keys():
    layers = [_layer("base", A="1", B="2")]
    result = stack_envs(layers)
    s = result.as_env_string()
    assert "A=1" in s
    assert "B=2" in s


def test_stack_env_strings_parses_raw():
    raw_base = "DB_HOST=localhost\nDB_PORT=5432\n"
    raw_prod = "DB_HOST=prod.example.com\n"
    result = stack_env_strings([("base", raw_base), ("prod", raw_prod)])
    assert result.resolved["DB_HOST"] == "prod.example.com"
    assert result.resolved["DB_PORT"] == "5432"
    assert "DB_HOST" in result.overrides


def test_source_label_joined():
    layers = [_layer("a"), _layer("b")]
    result = stack_envs(layers, source="a > b")
    assert result.source == "a > b"
