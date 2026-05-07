"""Multi-file diff: compare N env files pairwise against a base."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from envdiff.comparator import DiffResult, compare_envs
from envdiff.parser import parse_env_file, parse_env_string


@dataclass
class PairDiff:
    """Diff result between base and one target."""
    base_label: str
    target_label: str
    result: DiffResult


@dataclass
class MultiDiff:
    """Collection of pairwise diffs from a single base."""
    base_label: str
    pairs: List[PairDiff] = field(default_factory=list)

    def any_differences(self) -> bool:
        return any(p.result.missing_in_target or p.result.missing_in_base or p.result.mismatches
                   for p in self.pairs)

    def summary(self) -> Dict[str, int]:
        """Return per-target counts of issues."""
        return {
            p.target_label: (
                len(p.result.missing_in_target)
                + len(p.result.missing_in_base)
                + len(p.result.mismatches)
            )
            for p in self.pairs
        }


def diff_files(base_path: str, target_paths: List[str]) -> MultiDiff:
    """Compare base env file against each target file."""
    base_env = parse_env_file(base_path)
    multi = MultiDiff(base_label=base_path)
    for tp in target_paths:
        target_env = parse_env_file(tp)
        result = compare_envs(base_env, target_env)
        multi.pairs.append(PairDiff(base_label=base_path, target_label=tp, result=result))
    return multi


def diff_strings(
    base_label: str,
    base_content: str,
    targets: List[Tuple[str, str]],
) -> MultiDiff:
    """Compare base env string against each (label, content) target pair."""
    base_env = parse_env_string(base_content)
    multi = MultiDiff(base_label=base_label)
    for label, content in targets:
        target_env = parse_env_string(content)
        result = compare_envs(base_env, target_env)
        multi.pairs.append(PairDiff(base_label=base_label, target_label=label, result=result))
    return multi
