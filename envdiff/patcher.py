"""Apply patches to .env files: set, unset, or update specific keys."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from envdiff.parser import parse_env_file, parse_env_string


@dataclass
class PatchResult:
    source: str
    original: Dict[str, str]
    patched: Dict[str, str]
    added: List[str] = field(default_factory=list)
    updated: List[str] = field(default_factory=list)
    removed: List[str] = field(default_factory=list)

    def has_changes(self) -> bool:
        return bool(self.added or self.updated or self.removed)

    def as_env_string(self) -> str:
        lines = []
        for key, value in self.patched.items():
            if " " in value or value == "":
                lines.append(f'{key}="{value}"')
            else:
                lines.append(f"{key}={value}")
        return "\n".join(lines)


def _apply_ops(
    env: Dict[str, str],
    set_keys: Optional[Dict[str, str]] = None,
    unset_keys: Optional[List[str]] = None,
) -> tuple[Dict[str, str], List[str], List[str], List[str]]:
    patched = dict(env)
    added: List[str] = []
    updated: List[str] = []
    removed: List[str] = []

    for key, value in (set_keys or {}).items():
        if key in patched:
            if patched[key] != value:
                updated.append(key)
        else:
            added.append(key)
        patched[key] = value

    for key in unset_keys or []:
        if key in patched:
            del patched[key]
            removed.append(key)

    return patched, added, updated, removed


def patch_env_string(
    content: str,
    set_keys: Optional[Dict[str, str]] = None,
    unset_keys: Optional[List[str]] = None,
    source: str = "<string>",
) -> PatchResult:
    original = parse_env_string(content)
    patched, added, updated, removed = _apply_ops(original, set_keys, unset_keys)
    return PatchResult(
        source=source,
        original=original,
        patched=patched,
        added=added,
        updated=updated,
        removed=removed,
    )


def patch_env_file(
    path: str,
    set_keys: Optional[Dict[str, str]] = None,
    unset_keys: Optional[List[str]] = None,
) -> PatchResult:
    original = parse_env_file(path)
    patched, added, updated, removed = _apply_ops(original, set_keys, unset_keys)
    return PatchResult(
        source=path,
        original=original,
        patched=patched,
        added=added,
        updated=updated,
        removed=removed,
    )


def write_patch(result: PatchResult, path: str) -> None:
    """Write the patched env back to a file."""
    Path(path).write_text(result.as_env_string() + "\n", encoding="utf-8")
