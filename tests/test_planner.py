"""Tests for envdiff.planner and envdiff.plan_reporter."""
import json

import pytest

from envdiff.comparator import DiffResult
from envdiff.planner import MigrationPlan, PlanStep, plan_migration
from envdiff.plan_reporter import format_plan_text, format_plan_json


@pytest.fixture()
def clean_result() -> DiffResult:
    return DiffResult(missing_in_target=set(), missing_in_base=set(), mismatches={})


@pytest.fixture()
def dirty_result() -> DiffResult:
    return DiffResult(
        missing_in_target={"OLD_KEY"},
        missing_in_base={"NEW_KEY"},
        mismatches={"CHANGED": ("old_val", "new_val")},
    )


def test_no_steps_when_clean(clean_result):
    plan = plan_migration(clean_result)
    assert not plan.has_steps
    assert plan.step_count == 0


def test_remove_step_for_missing_in_target(dirty_result):
    plan = plan_migration(dirty_result)
    removes = plan.by_action("remove")
    assert len(removes) == 1
    assert removes[0].key == "OLD_KEY"
    assert removes[0].action == "remove"


def test_add_step_for_missing_in_base(dirty_result):
    plan = plan_migration(dirty_result)
    adds = plan.by_action("add")
    assert len(adds) == 1
    assert adds[0].key == "NEW_KEY"


def test_update_step_for_mismatch(dirty_result):
    plan = plan_migration(dirty_result)
    updates = plan.by_action("update")
    assert len(updates) == 1
    step = updates[0]
    assert step.key == "CHANGED"
    assert step.current_value == "old_val"
    assert step.target_value == "new_val"


def test_total_step_count(dirty_result):
    plan = plan_migration(dirty_result)
    assert plan.step_count == 3


def test_source_and_target_labels(dirty_result):
    plan = plan_migration(dirty_result, source="dev", target="prod")
    assert plan.source == "dev"
    assert plan.target == "prod"


def test_format_text_no_changes(clean_result):
    text = format_plan_text(plan_migration(clean_result), color=False)
    assert "No changes needed" in text


def test_format_text_shows_add(dirty_result):
    text = format_plan_text(plan_migration(dirty_result), color=False)
    assert "NEW_KEY" in text
    assert "+" in text


def test_format_text_shows_remove(dirty_result):
    text = format_plan_text(plan_migration(dirty_result), color=False)
    assert "OLD_KEY" in text
    assert "-" in text


def test_format_text_shows_update(dirty_result):
    text = format_plan_text(plan_migration(dirty_result), color=False)
    assert "CHANGED" in text
    assert "old_val" in text
    assert "new_val" in text


def test_format_json_valid(dirty_result):
    data = json.loads(format_plan_json(plan_migration(dirty_result)))
    assert "steps" in data
    assert data["step_count"] == 3


def test_as_dict_structure(dirty_result):
    plan = plan_migration(dirty_result, source="a", target="b")
    d = plan.as_dict()
    assert d["source"] == "a"
    assert d["target"] == "b"
    assert isinstance(d["steps"], list)
