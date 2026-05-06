"""Lint .env files for common style and convention issues."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class LintIssue:
    line_number: int
    key: str
    message: str
    severity: str = "warning"  # "warning" | "error"

    def __str__(self) -> str:
        return f"[{self.severity.upper()}] line {self.line_number}: {self.key!r} — {self.message}"


@dataclass
class LintResult:
    source: str
    issues: List[LintIssue] = field(default_factory=list)

    @property
    def is_clean(self) -> bool:
        return len(self.issues) == 0

    def add(self, issue: LintIssue) -> None:
        self.issues.append(issue)

    def errors(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "error"]

    def warnings(self) -> List[LintIssue]:
        return [i for i in self.issues if i.severity == "warning"]


def lint_env_string(content: str, source: str = "<string>") -> LintResult:
    """Lint raw .env content and return a LintResult."""
    result = LintResult(source=source)

    for lineno, raw in enumerate(content.splitlines(), start=1):
        line = raw.strip()

        # Skip blanks and comments
        if not line or line.startswith("#"):
            continue

        if "=" not in line:
            continue

        key, _, value = line.partition("=")
        key = key.strip()
        value = value.strip()

        # Trailing whitespace in key
        if key != key.rstrip():
            result.add(LintIssue(lineno, key.rstrip(), "key has trailing whitespace", "warning"))

        # ALL_CAPS convention
        if key and not key.isupper():
            result.add(LintIssue(lineno, key, "key is not ALL_CAPS", "warning"))

        # Unquoted value with spaces
        if " " in value and not (value.startswith('"') or value.startswith("'")):
            result.add(LintIssue(lineno, key, "value contains spaces but is not quoted", "warning"))

        # Duplicate export prefix
        if key.startswith("export "):
            result.add(LintIssue(lineno, key, "key uses 'export' prefix — strip it for plain .env files", "warning"))

        # Very long values (>256 chars) flagged as info-level warning
        if len(value) > 256:
            result.add(LintIssue(lineno, key, "value exceeds 256 characters", "warning"))

    return result


def lint_env_file(path: str) -> LintResult:
    """Read a file and lint its contents."""
    try:
        with open(path, "r", encoding="utf-8") as fh:
            content = fh.read()
    except OSError as exc:
        result = LintResult(source=path)
        result.add(LintIssue(0, "", f"could not read file: {exc}", "error"))
        return result
    return lint_env_string(content, source=path)
