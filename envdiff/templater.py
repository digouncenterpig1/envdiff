"""Generate .env.example templates from parsed env files."""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from envdiff.parser import parse_env_file, parse_env_string


@dataclass
class EnvTemplate:
    """A sanitized template derived from a real .env file."""
    keys: list[str] = field(default_factory=list)
    placeholders: dict[str, str] = field(default_factory=dict)
    source: Optional[str] = None

    def to_string(self) -> str:
        lines = []
        for key in self.keys:
            placeholder = self.placeholders.get(key, "")
            lines.append(f"{key}={placeholder}")
        return "\n".join(lines) + ("\n" if lines else "")


def _make_placeholder(key: str, value: str) -> str:
    """Return a safe placeholder; preserve empty values as-is."""
    if value == "":
        return ""
    lower = key.lower()
    if any(hint in lower for hint in ("secret", "password", "token", "key", "pass", "pwd")):
        return "<secret>"
    return "<value>"


def build_template(
    env: dict[str, str],
    source: Optional[str] = None,
    preserve_values: bool = False,
) -> EnvTemplate:
    """Build an EnvTemplate from a parsed env dict."""
    keys = list(env.keys())
    placeholders = {}
    for k, v in env.items():
        if preserve_values:
            placeholders[k] = v
        else:
            placeholders[k] = _make_placeholder(k, v)
    return EnvTemplate(keys=keys, placeholders=placeholders, source=source)


def template_from_file(
    path: str | Path,
    preserve_values: bool = False,
) -> EnvTemplate:
    """Parse a .env file and return a sanitized template."""
    p = Path(path)
    env = parse_env_file(p)
    return build_template(env, source=str(p), preserve_values=preserve_values)


def template_from_string(
    content: str,
    preserve_values: bool = False,
) -> EnvTemplate:
    """Parse env content from a string and return a sanitized template."""
    env = parse_env_string(content)
    return build_template(env, preserve_values=preserve_values)


def write_template(template: EnvTemplate, dest: str | Path) -> None:
    """Write the template to a file, creating parent dirs as needed."""
    dest = Path(dest)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(template.to_string(), encoding="utf-8")
