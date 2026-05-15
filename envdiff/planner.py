"""Plan migration steps to bring one env in line with another."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from envdiff.comparator import DiffResult


@dataclass
class PlanStep:
    action: str          # 'add', 'remove', 'update'
    key: str
    current_value: str | None
    target_value: str | None

    def as_dict(self) -> dict:
        return {
            "action": self.action,
            "key": self.key,
            "current_value": self.current_value,
            "target_value": self.target_value,
        }


@dataclass
class MigrationPlan:
    source: str
    target: str
    steps: List[PlanStep] = field(default_factory=list)

    @property
    def has_steps(self) -> bool:
        return bool(self.steps)

    @property
    def step_count(self) -> int:
        return len(self.steps)

    def by_action(self, action: str) -> List[PlanStep]:
        return [s for s in self.steps if s.action == action]

    def as_dict(self) -> dict:
        return {
            "source": self.source,
            "target": self.target,
            "step_count": self.step_count,
            "steps": [s.as_dict() for s in self.steps],
        }


def plan_migration(result: DiffResult, source: str = "base", target: str = "target") -> MigrationPlan:
    """Produce an ordered list of steps to migrate *source* env to match *target*."""
    steps: List[PlanStep] = []

    for key in sorted(result.missing_in_target):
        steps.append(PlanStep(action="remove", key=key, current_value=None, target_value=None))

    for key in sorted(result.missing_in_base):
        steps.append(PlanStep(action="add", key=key, current_value=None, target_value=None))

    for key, (base_val, tgt_val) in sorted(result.mismatches.items()):
        steps.append(PlanStep(action="update", key=key, current_value=base_val, target_value=tgt_val))

    return MigrationPlan(source=source, target=target, steps=steps)
