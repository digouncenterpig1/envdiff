"""Scores .env file health based on lint, profile, and diff results."""

from dataclasses import dataclass, field
from typing import Optional

from envdiff.linter import LintResult
from envdiff.profiler import EnvProfile
from envdiff.comparator import DiffResult


@dataclass
class HealthScore:
    source: str
    total: int = 100
    deductions: dict = field(default_factory=dict)
    notes: list = field(default_factory=list)

    @property
    def score(self) -> int:
        return max(0, self.total - sum(self.deductions.values()))

    @property
    def grade(self) -> str:
        s = self.score
        if s >= 90:
            return "A"
        elif s >= 75:
            return "B"
        elif s >= 60:
            return "C"
        elif s >= 40:
            return "D"
        return "F"


def score_env(
    source: str,
    lint_result: Optional[LintResult] = None,
    profile: Optional[EnvProfile] = None,
    diff_result: Optional[DiffResult] = None,
) -> HealthScore:
    hs = HealthScore(source=source)

    if lint_result is not None:
        issue_count = len(lint_result.issues)
        if issue_count > 0:
            penalty = min(40, issue_count * 5)
            hs.deductions["lint_issues"] = penalty
            hs.notes.append(f"{issue_count} lint issue(s) found (-{penalty} pts)")

    if profile is not None:
        empty = profile.empty_count
        if empty > 0:
            penalty = min(20, empty * 3)
            hs.deductions["empty_values"] = penalty
            hs.notes.append(f"{empty} empty value(s) (-{penalty} pts)")
        if profile.secrets_hint_count > 0:
            hs.notes.append(
                f"{profile.secrets_hint_count} potential secret key(s) detected (informational)"
            )

    if diff_result is not None:
        missing = len(diff_result.missing_in_target)
        mismatched = len(diff_result.mismatched)
        if missing > 0:
            penalty = min(20, missing * 4)
            hs.deductions["missing_keys"] = penalty
            hs.notes.append(f"{missing} missing key(s) in target (-{penalty} pts)")
        if mismatched > 0:
            penalty = min(20, mismatched * 4)
            hs.deductions["mismatched_keys"] = penalty
            hs.notes.append(f"{mismatched} mismatched key(s) (-{penalty} pts)")

    return hs
