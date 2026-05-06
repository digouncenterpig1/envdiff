"""Tests for envdiff.watcher."""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from envdiff.watcher import _changed, _mtimes, watch


def test_mtimes_existing_file(tmp_path: Path) -> None:
    f = tmp_path / "a.env"
    f.write_text("A=1")
    result = _mtimes([f])
    assert f in result
    assert result[f] > 0


def test_mtimes_missing_file(tmp_path: Path) -> None:
    f = tmp_path / "missing.env"
    result = _mtimes([f])
    assert result[f] == -1.0


def test_changed_detects_new_mtime(tmp_path: Path) -> None:
    f = tmp_path / "a.env"
    f.write_text("A=1")
    old = {f: 0.0}
    new = _mtimes([f])
    assert f in _changed(old, new)


def test_changed_no_diff(tmp_path: Path) -> None:
    f = tmp_path / "a.env"
    f.write_text("A=1")
    snapshot = _mtimes([f])
    assert _changed(snapshot, snapshot) == []


def test_watch_calls_callback_on_change(tmp_path: Path) -> None:
    f = tmp_path / "test.env"
    f.write_text("X=1")

    called_with: list[list[Path]] = []

    def on_change(paths: list[Path]) -> None:
        called_with.append(paths)

    # Modify file between cycles using a side-effect in the callback setup.
    # We run 2 cycles; modify the file before the watcher starts so first
    # poll detects a change immediately.
    original_mtime = f.stat().st_mtime
    # Force a detectable mtime change.
    new_time = original_mtime - 10
    import os
    os.utime(f, (new_time, new_time))

    watch([f], on_change, interval=0.01, max_cycles=1)
    # After one cycle the callback should have fired.
    assert len(called_with) == 1
    assert f in called_with[0]


def test_watch_no_callback_when_unchanged(tmp_path: Path) -> None:
    f = tmp_path / "stable.env"
    f.write_text("Y=2")

    calls: list[int] = []
    watch([f], lambda _: calls.append(1), interval=0.01, max_cycles=2)
    assert calls == []
