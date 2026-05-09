"""Annotate .env keys with inline comments describing their type, status, or origin."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

_SECRET_HINTS = ("secret", "password", "passwd", "token", "key", "api_key", "auth", "credential", "private")
_URL_HINTS = ("url", "uri", "endpoint", "host", "dsn")
_FLAG_HINTS = ("enable", "disable", "debug", "verbose", "flag", "active", "enabled")


@dataclass
class Annotation:
    key: str
    value: str
    comment: str

    def as_line(self) -> str:
        return f"{self.key}={self.value}  # {self.comment}"


@dataclass
class AnnotateResult:
    source: str
    annotations: List[Annotation] = field(default_factory=list)

    def by_key(self, key: str) -> Optional[Annotation]:
        for a in self.annotations:
            if a.key == key:
                return a
        return None

    def as_env_string(self) -> str:
        return "\n".join(a.as_line() for a in self.annotations)


def _classify(key: str, value: str) -> str:
    lower = key.lower()
    if any(h in lower for h in _SECRET_HINTS):
        return "secret"
    if any(h in lower for h in _URL_HINTS):
        return "url"
    if any(h in lower for h in _FLAG_HINTS):
        return "flag"
    if value == "":
        return "empty"
    if value.isdigit():
        return "numeric"
    return "string"


def _build_comment(key: str, value: str, extra: Optional[Dict[str, str]] = None) -> str:
    if extra and key in extra:
        return extra[key]
    kind = _classify(key, value)
    labels = {
        "secret": "sensitive – do not commit",
        "url": "URL / endpoint",
        "flag": "boolean flag",
        "empty": "no value set",
        "numeric": "numeric value",
        "string": "string value",
    }
    return labels.get(kind, "string value")


def annotate_env(
    env: Dict[str, str],
    source: str = "<env>",
    extra_comments: Optional[Dict[str, str]] = None,
) -> AnnotateResult:
    """Return an AnnotateResult with a comment for every key in *env*."""
    result = AnnotateResult(source=source)
    for key, value in env.items():
        comment = _build_comment(key, value, extra_comments)
        result.annotations.append(Annotation(key=key, value=value, comment=comment))
    return result
