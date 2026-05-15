"""Statistical summary utilities for diff results across multiple env pairs."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List

from envdiff.differ import MultiDiff


@dataclass
class DiffStats:
    source: str
    total_pairs: int
    clean_pairs: int
    pairs_with_missing_in_target: int
    pairs_with_missing_in_base: int
    pairs_with_mismatches: int
    total_missing_in_target: int
    total_missing_in_base: int
    total_mismatches: int
    most_affected_key: str | None = None

    @property
    def dirty_pairs(self) -> int:
        return self.total_pairs - self.clean_pairs

    @property
    def health_ratio(self) -> float:
        if self.total_pairs == 0:
            return 1.0
        return round(self.clean_pairs / self.total_pairs, 4)

    def as_dict(self) -> dict:
        return {
            "source": self.source,
            "total_pairs": self.total_pairs,
            "clean_pairs": self.clean_pairs,
            "dirty_pairs": self.dirty_pairs,
            "pairs_with_missing_in_target": self.pairs_with_missing_in_target,
            "pairs_with_missing_in_base": self.pairs_with_missing_in_base,
            "pairs_with_mismatches": self.pairs_with_mismatches,
            "total_missing_in_target": self.total_missing_in_target,
            "total_missing_in_base": self.total_missing_in_base,
            "total_mismatches": self.total_mismatches,
            "most_affected_key": self.most_affected_key,
            "health_ratio": self.health_ratio,
        }


def compute_stats(multi: MultiDiff, source: str = "multi") -> DiffStats:
    from collections import Counter

    key_freq: Counter = Counter()
    clean = 0
    mit = 0
    mib = 0
    mm = 0
    total_mit = 0
    total_mib = 0
    total_mm = 0

    for pair in multi.pairs:
        r = pair.result
        has_issue = False
        if r.missing_in_target:
            mit += 1
            has_issue = True
            total_mit += len(r.missing_in_target)
            key_freq.update(r.missing_in_target)
        if r.missing_in_base:
            mib += 1
            has_issue = True
            total_mib += len(r.missing_in_base)
            key_freq.update(r.missing_in_base)
        if r.mismatches:
            mm += 1
            has_issue = True
            total_mm += len(r.mismatches)
            key_freq.update(r.mismatches.keys())
        if not has_issue:
            clean += 1

    most_affected = key_freq.most_common(1)[0][0] if key_freq else None

    return DiffStats(
        source=source,
        total_pairs=len(multi.pairs),
        clean_pairs=clean,
        pairs_with_missing_in_target=mit,
        pairs_with_missing_in_base=mib,
        pairs_with_mismatches=mm,
        total_missing_in_target=total_mit,
        total_missing_in_base=total_mib,
        total_mismatches=total_mm,
        most_affected_key=most_affected,
    )
