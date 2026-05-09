"""High-level summary statistics for multi-env diffs."""

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.differ import MultiDiff


@dataclass
class DiffSummary:
    total_pairs: int = 0
    pairs_with_differences: int = 0
    total_missing_in_target: int = 0
    total_missing_in_base: int = 0
    total_mismatches: int = 0
    keys_always_missing: List[str] = field(default_factory=list)
    keys_always_mismatched: List[str] = field(default_factory=list)

    @property
    def clean_pairs(self) -> int:
        return self.total_pairs - self.pairs_with_differences

    @property
    def total_issues(self) -> int:
        return (
            self.total_missing_in_target
            + self.total_missing_in_base
            + self.total_mismatches
        )

    def as_dict(self) -> Dict:
        return {
            "total_pairs": self.total_pairs,
            "pairs_with_differences": self.pairs_with_differences,
            "clean_pairs": self.clean_pairs,
            "total_missing_in_target": self.total_missing_in_target,
            "total_missing_in_base": self.total_missing_in_base,
            "total_mismatches": self.total_mismatches,
            "total_issues": self.total_issues,
            "keys_always_missing": self.keys_always_missing,
            "keys_always_mismatched": self.keys_always_mismatched,
        }


def summarize_multi_diff(multi: MultiDiff) -> DiffSummary:
    """Compute aggregate statistics across all pairs in a MultiDiff."""
    summary = DiffSummary(total_pairs=len(multi.pairs))

    missing_target_counts: Dict[str, int] = {}
    mismatch_counts: Dict[str, int] = {}

    for pair in multi.pairs:
        r = pair.result
        if r.missing_in_target or r.missing_in_base or r.mismatches:
            summary.pairs_with_differences += 1
        summary.total_missing_in_target += len(r.missing_in_target)
        summary.total_missing_in_base += len(r.missing_in_base)
        summary.total_mismatches += len(r.mismatches)

        for key in r.missing_in_target:
            missing_target_counts[key] = missing_target_counts.get(key, 0) + 1
        for key in r.mismatches:
            mismatch_counts[key] = mismatch_counts.get(key, 0) + 1

    n = len(multi.pairs)
    summary.keys_always_missing = sorted(
        k for k, v in missing_target_counts.items() if v == n
    )
    summary.keys_always_mismatched = sorted(
        k for k, v in mismatch_counts.items() if v == n
    )

    return summary
