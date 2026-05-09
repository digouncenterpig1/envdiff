"""Pin current env values as a baseline for drift detection."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List


@dataclass
class PinResult:
    source: str
    pinned: Dict[str, str] = field(default_factory=dict)
    drifted: List[str] = field(default_factory=list)  # keys whose values changed
    new_keys: List[str] = field(default_factory=list)  # keys not in pin
    removed_keys: List[str] = field(default_factory=list)  # keys in pin but gone

    def has_drift(self) -> bool:
        return bool(self.drifted or self.new_keys or self.removed_keys)


def save_pin(env: Dict[str, str], path: str | Path, source: str = "") -> None:
    """Persist env dict as a pin file (JSON)."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    payload = {"source": source, "values": env}
    p.write_text(json.dumps(payload, indent=2))


def load_pin(path: str | Path) -> Dict[str, str]:
    """Load pinned values from a pin file. Returns empty dict if missing."""
    p = Path(path)
    if not p.exists():
        return {}
    data = json.loads(p.read_text())
    return data.get("values", {})


def pin_exists(path: str | Path) -> bool:
    return Path(path).exists()


def diff_with_pin(current: Dict[str, str], pin_path: str | Path, source: str = "") -> PinResult:
    """Compare current env against a saved pin and return drift info."""
    pinned = load_pin(pin_path)
    result = PinResult(source=source, pinned=pinned)

    for key, value in current.items():
        if key not in pinned:
            result.new_keys.append(key)
        elif pinned[key] != value:
            result.drifted.append(key)

    for key in pinned:
        if key not in current:
            result.removed_keys.append(key)

    return result
