"""Classify env keys into semantic categories based on name and value patterns."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List

_CATEGORY_PATTERNS: Dict[str, List[str]] = {
    "secret": [
        r"(?i)(secret|password|passwd|token|api_key|apikey|private_key|auth|credential|cert|jwt)"
    ],
    "url": [r"(?i)(url|uri|endpoint|host|hostname|base_path)"],
    "port": [r"(?i)port$"],
    "flag": [r"(?i)(enable|disable|flag|toggle|feature)"],
    "path": [r"(?i)(path|dir|directory|folder|root|home)"],
    "email": [r"(?i)(email|mail)"],
    "timeout": [r"(?i)(timeout|ttl|expiry|expiration|max_age)"],
    "numeric": [],
    "unknown": [],
}

_VALUE_NUMERIC = re.compile(r"^-?\d+(\.\d+)?$")
_VALUE_URL = re.compile(r"^https?://")
_VALUE_EMAIL = re.compile(r"^[\w.+-]+@[\w.-]+\.[a-z]{2,}$", re.IGNORECASE)


@dataclass
class ClassifyEntry:
    key: str
    value: str
    category: str


@dataclass
class ClassifyResult:
    source: str
    entries: List[ClassifyEntry] = field(default_factory=list)

    def by_category(self) -> Dict[str, List[ClassifyEntry]]:
        out: Dict[str, List[ClassifyEntry]] = {}
        for e in self.entries:
            out.setdefault(e.category, []).append(e)
        return out

    def category_counts(self) -> Dict[str, int]:
        return {cat: len(items) for cat, items in self.by_category().items()}

    def keys_in(self, category: str) -> List[str]:
        return [e.key for e in self.entries if e.category == category]


def _classify_key(key: str, value: str) -> str:
    for category, patterns in _CATEGORY_PATTERNS.items():
        if category in ("numeric", "unknown"):
            continue
        for pat in patterns:
            if re.search(pat, key):
                return category
    # fall back to value-based detection
    if _VALUE_URL.match(value):
        return "url"
    if _VALUE_EMAIL.match(value):
        return "email"
    if _VALUE_NUMERIC.match(value):
        return "numeric"
    return "unknown"


def classify_env(env: Dict[str, str], source: str = "env") -> ClassifyResult:
    """Classify all keys in an env dict and return a ClassifyResult."""
    result = ClassifyResult(source=source)
    for key, value in env.items():
        category = _classify_key(key, value)
        result.entries.append(ClassifyEntry(key=key, value=value, category=category))
    return result
