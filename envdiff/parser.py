"""Parser for .env files."""

import re
from pathlib import Path
from typing import Dict, Optional


COMMENT_RE = re.compile(r"^\s*#.*$")
BLANK_RE = re.compile(r"^\s*$")
KEY_VALUE_RE = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$")


def _strip_quotes(value: str) -> str:
    """Remove surrounding single or double quotes from a value."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
        return value[1:-1]
    return value


def parse_env_file(path: str) -> Dict[str, Optional[str]]:
    """
    Parse a .env file and return a dict of key -> value.

    Lines starting with # are comments and are ignored.
    Empty lines are ignored.
    Values may be quoted with single or double quotes.
    """
    env_path = Path(path)
    if not env_path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    result: Dict[str, Optional[str]] = {}

    with env_path.open("r", encoding="utf-8") as f:
        for lineno, line in enumerate(f, start=1):
            line = line.rstrip("\n")

            if COMMENT_RE.match(line) or BLANK_RE.match(line):
                continue

            match = KEY_VALUE_RE.match(line)
            if match:
                key = match.group(1)
                value = _strip_quotes(match.group(2).strip())
                result[key] = value if value != "" else None
            else:
                raise ValueError(
                    f"Invalid line {lineno} in {path!r}: {line!r}"
                )

    return result
