"""Tests for envdiff.sorter."""

import pytest

from envdiff.sorter import SortResult, sort_env, sort_env_file


@pytest.fixture
def sample_env():
    return {
        "ZEBRA": "1",
        "APP_NAME": "myapp",
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "ALPHA": "first",
    }


def test_alpha_sort(sample_env):
    result = sort_env(sample_env, strategy="alpha")
    assert result.sorted_keys == sorted(sample_env.keys())


def test_alpha_desc_sort(sample_env):
    result = sort_env(sample_env, strategy="alpha_desc")
    assert result.sorted_keys == sorted(sample_env.keys(), reverse=True)


def test_by_prefix_groups_together(sample_env):
    result = sort_env(sample_env, strategy="by_prefix")
    # DB_ keys should be adjacent
    idx_db_host = result.sorted_keys.index("DB_HOST")
    idx_db_port = result.sorted_keys.index("DB_PORT")
    assert abs(idx_db_host - idx_db_port) == 1


def test_by_length_sort(sample_env):
    result = sort_env(sample_env, strategy="by_length")
    lengths = [len(k) for k in result.sorted_keys]
    assert lengths == sorted(lengths)


def test_original_order_preserved(sample_env):
    result = sort_env(sample_env, strategy="alpha")
    assert result.original == list(sample_env.keys())


def test_source_label(sample_env):
    result = sort_env(sample_env, source="staging.env", strategy="alpha")
    assert result.source == "staging.env"


def test_strategy_stored(sample_env):
    result = sort_env(sample_env, strategy="by_length")
    assert result.strategy == "by_length"


def test_as_env_string(sample_env):
    result = sort_env(sample_env, strategy="alpha")
    output = result.as_env_string()
    lines = output.splitlines()
    assert len(lines) == len(sample_env)
    for line in lines:
        assert "=" in line


def test_as_env_string_preserves_values(sample_env):
    result = sort_env(sample_env, strategy="alpha")
    output = result.as_env_string()
    for key, value in sample_env.items():
        assert f"{key}={value}" in output


def test_unknown_strategy_raises(sample_env):
    with pytest.raises(ValueError, match="Unknown sort strategy"):
        sort_env(sample_env, strategy="random")  # type: ignore


def test_sort_env_file(tmp_path, sample_env):
    env_file = tmp_path / "test.env"
    env_file.write_text("\n".join(f"{k}={v}" for k, v in sample_env.items()))
    result = sort_env_file(str(env_file), strategy="alpha")
    assert isinstance(result, SortResult)
    assert result.sorted_keys == sorted(sample_env.keys())
    assert result.source == str(env_file)
