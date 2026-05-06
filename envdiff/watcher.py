"""Watch .env files for changes and re-run comparison automatically."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Callable


ModifiedCallback = Callable[[list[Path]], None]


def _mtimes(paths: list[Path]) -> dict[Path, float]:
    result: dict[Path, float] = {}
    for p in paths:
        try:
            result[p] = p.stat().st_mtime
        except FileNotFoundError:
            result[p] = -1.0
    return result


def _changed(old: dict[Path, float], new: dict[Path, float]) -> list[Path]:
    return [p for p, mtime in new.items() if old.get(p) != mtime]


def watch(
    paths: list[Path],
    callback: ModifiedCallback,
    *,
    interval: float = 1.0,
    max_cycles: int | None = None,
) -> None:
    """Poll *paths* every *interval* seconds; call *callback* with changed paths.

    Parameters
    ----------
    paths:      Files to monitor.
    callback:   Called with a list of paths that changed since last poll.
    interval:   Seconds between polls.
    max_cycles: Stop after this many cycles (useful for testing; ``None`` = forever).
    """
    previous = _mtimes(paths)
    cycles = 0
    while max_cycles is None or cycles < max_cycles:
        time.sleep(interval)
        current = _mtimes(paths)
        changed = _changed(previous, current)
        if changed:
            callback(changed)
        previous = current
        cycles += 1
