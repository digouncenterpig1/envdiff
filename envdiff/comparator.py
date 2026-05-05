"""Compare parsed .env dictionaries and surface differences."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set


@dataclass
class DiffResult:
    """Holds the result of comparing two .env files."""

    base_name: str
    target_name: str
    missing_in_target: List[str] = field(default_factory=list)
    missing_in_base: List[str] = field(default_factory=list)
    value_mismatches: Dict[str, tuple] = field(default_factory=dict)

    @property
    def has_differences(self) -> bool:
        return bool(
            self.missing_in_target
            or self.missing_in_base
            or self.value_mismatches
        )


def compare_envs(
    base: Dict[str, Optional[str]],
    target: Dict[str, Optional[str]],
    base_name: str = "base",
    target_name: str = "target",
    ignore_values: bool = False,
) -> DiffResult:
    """
    Compare two env dicts.

    Args:
        base: The reference env dict.
        target: The env dict to compare against base.
        base_name: Label for the base file.
        target_name: Label for the target file.
        ignore_values: If True, only check for key presence, not value equality.

    Returns:
        A DiffResult describing the differences.
    """
    result = DiffResult(base_name=base_name, target_name=target_name)

    base_keys: Set[str] = set(base.keys())
    target_keys: Set[str] = set(target.keys())

    result.missing_in_target = sorted(base_keys - target_keys)
    result.missing_in_base = sorted(target_keys - base_keys)

    if not ignore_values:
        common_keys = base_keys & target_keys
        for key in sorted(common_keys):
            if base[key] != target[key]:
                result.value_mismatches[key] = (base[key], target[key])

    return result
