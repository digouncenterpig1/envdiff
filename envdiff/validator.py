"""Validate .env files for common issues before comparison."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class ValidationIssue:
    line_number: int
    line: str
    message: str

    def __str__(self) -> str:
        return f"Line {self.line_number}: {self.message!r} -> {self.line!r}"


@dataclass
class ValidationResult:
    issues: List[ValidationIssue] = field(default_factory=list)

    @property
    def is_valid(self) -> bool:
        return len(self.issues) == 0

    def add(self, line_number: int, line: str, message: str) -> None:
        self.issues.append(ValidationIssue(line_number, line, message))


def validate_env_string(content: str) -> ValidationResult:
    """Validate raw .env content and return a ValidationResult."""
    result = ValidationResult()

    for i, raw_line in enumerate(content.splitlines(), start=1):
        line = raw_line.strip()

        # skip blanks and comments
        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            result.add(i, raw_line, "missing '=' separator")
            continue

        key, _, value = line.partition("=")
        key = key.strip()

        if not key:
            result.add(i, raw_line, "empty key")
            continue

        if " " in key:
            result.add(i, raw_line, "key contains whitespace")

        if not key[0].isalpha() and key[0] != "_":
            result.add(i, raw_line, "key must start with a letter or underscore")

        # unmatched quotes
        stripped_value = value.strip()
        if stripped_value and stripped_value[0] in ('"', "'"):
            quote_char = stripped_value[0]
            if not stripped_value.endswith(quote_char) or len(stripped_value) < 2:
                result.add(i, raw_line, "unmatched quote in value")

    return result


def validate_env_file(path: str) -> ValidationResult:
    """Read a file and validate its contents."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            content = fh.read()
    except OSError as exc:
        result = ValidationResult()
        result.add(0, "", f"cannot read file: {exc}")
        return result

    return validate_env_string(content)
