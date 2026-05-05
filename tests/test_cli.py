"""Tests for the CLI entry point."""

import pytest
from pathlib import Path

from envdiff.cli import run


@pytest.fixture()
def tmp_envs(tmp_path: Path):
    """Return a helper that writes named env files under tmp_path."""

    def _write(name: str, content: str) -> Path:
        p = tmp_path / name
        p.write_text(content)
        return p

    return _write


def test_no_differences_exits_zero(tmp_envs):
    base = tmp_envs(".env.base", "KEY=value\nFOO=bar\n")
    target = tmp_envs(".env.target", "KEY=value\nFOO=bar\n")
    assert run([str(base), str(target)]) == 0


def test_differences_exits_zero_without_flag(tmp_envs):
    base = tmp_envs(".env.base", "KEY=value\nMISSING=x\n")
    target = tmp_envs(".env.target", "KEY=value\n")
    # differences exist but --exit-code not passed
    assert run([str(base), str(target)]) == 0


def test_differences_exits_one_with_exit_code_flag(tmp_envs):
    base = tmp_envs(".env.base", "KEY=value\nMISSING=x\n")
    target = tmp_envs(".env.target", "KEY=value\n")
    assert run([str(base), str(target), "--exit-code"]) == 1


def test_missing_base_file_exits_two(tmp_envs, tmp_path):
    target = tmp_envs(".env.target", "KEY=value\n")
    assert run([str(tmp_path / "nonexistent.env"), str(target)]) == 2


def test_missing_target_file_exits_two(tmp_envs, tmp_path):
    base = tmp_envs(".env.base", "KEY=value\n")
    assert run([str(base), str(tmp_path / "nonexistent.env")]) == 2


def test_no_color_flag_accepted(tmp_envs):
    base = tmp_envs(".env.base", "KEY=value\n")
    target = tmp_envs(".env.target", "KEY=value\n")
    assert run([str(base), str(target), "--no-color"]) == 0


def test_values_flag_accepted(tmp_envs):
    base = tmp_envs(".env.base", "KEY=hello\n")
    target = tmp_envs(".env.target", "KEY=world\n")
    # should not raise, just shows values
    assert run([str(base), str(target), "--values", "--exit-code"]) == 1
