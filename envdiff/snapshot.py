"""Persist and restore parsed .env snapshots for later diffing."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


SnapshotData = dict[str, str]


def save_snapshot(env: SnapshotData, path: Path, *, label: str = "") -> None:
    """Serialize *env* to a JSON snapshot file at *path*."""
    path.parent.mkdir(parents=True, exist_ok=True)
    payload: dict[str, Any] = {"label": label, "env": env}
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")


def load_snapshot(path: Path) -> SnapshotData:
    """Load and return the env mapping from a snapshot file."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    if "env" not in raw:
        raise ValueError(f"Invalid snapshot format in {path}: missing 'env' key.")
    return raw["env"]


def load_snapshot_label(path: Path) -> str:
    """Return the label stored in *path*, or an empty string if absent."""
    raw = json.loads(path.read_text(encoding="utf-8"))
    return raw.get("label", "")


def snapshot_exists(path: Path) -> bool:
    """Return ``True`` if *path* points to an existing snapshot file."""
    return path.is_file()


def diff_with_snapshot(
    current: SnapshotData,
    snapshot_path: Path,
) -> tuple[set[str], set[str], dict[str, tuple[str, str]]]:
    """Compare *current* env against a saved snapshot.

    Returns
    -------
    (new_keys, removed_keys, changed_keys)
        new_keys:     keys present in *current* but not in snapshot
        removed_keys: keys present in snapshot but not in *current*
        changed_keys: mapping of key -> (snapshot_value, current_value)
    """
    saved = load_snapshot(snapshot_path)
    new_keys = set(current) - set(saved)
    removed_keys = set(saved) - set(current)
    changed: dict[str, tuple[str, str]] = {
        k: (saved[k], current[k])
        for k in set(current) & set(saved)
        if saved[k] != current[k]
    }
    return new_keys, removed_keys, changed
