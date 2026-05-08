"""Tag keys in an env dict with metadata labels (e.g. 'secret', 'url', 'flag', 'numeric')."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, List, Set

_SECRET_PATTERNS = re.compile(
    r"(secret|password|passwd|token|api_key|apikey|private|auth|credential|cert|pem)",
    re.IGNORECASE,
)
_URL_PATTERNS = re.compile(r"(url|uri|endpoint|host|dsn|database_url)", re.IGNORECASE)
_FLAG_VALUE = re.compile(r"^(true|false|yes|no|1|0)$", re.IGNORECASE)
_NUMERIC_VALUE = re.compile(r"^-?\d+(\.\d+)?$")


@dataclass
class TagResult:
    source: str
    tags: Dict[str, Set[str]] = field(default_factory=dict)

    def keys_with_tag(self, tag: str) -> List[str]:
        return [k for k, t in self.tags.items() if tag in t]

    def all_tags(self) -> Set[str]:
        result: Set[str] = set()
        for t in self.tags.values():
            result |= t
        return result


def _tag_key_value(key: str, value: str) -> Set[str]:
    tags: Set[str] = set()
    if _SECRET_PATTERNS.search(key):
        tags.add("secret")
    if _URL_PATTERNS.search(key):
        tags.add("url")
    if _FLAG_VALUE.match(value):
        tags.add("flag")
    if _NUMERIC_VALUE.match(value):
        tags.add("numeric")
    if value == "":
        tags.add("empty")
    if not tags - {"empty"}:
        tags.add("plain")
    return tags


def tag_env(env: Dict[str, str], source: str = "<env>") -> TagResult:
    """Tag every key in *env* and return a TagResult."""
    result = TagResult(source=source)
    for key, value in env.items():
        result.tags[key] = _tag_key_value(key, value)
    return result


def tags_for_key(key: str, value: str) -> Set[str]:
    """Convenience: return the tag set for a single key/value pair."""
    return _tag_key_value(key, value)
