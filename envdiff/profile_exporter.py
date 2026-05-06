"""Export EnvProfile results to disk."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

from envdiff.profiler import EnvProfile
from envdiff.profile_reporter import format_profile_text


def _ensure_parent(path: str) -> None:
    Path(path).parent.mkdir(parents=True, exist_ok=True)


def export_profile_text(profile: EnvProfile, output: str) -> None:
    _ensure_parent(output)
    Path(output).write_text(format_profile_text(profile), encoding="utf-8")


def export_profile_json(profile: EnvProfile, output: str) -> None:
    _ensure_parent(output)
    data = {
        "source": profile.source,
        "total_keys": profile.total_keys,
        "empty_count": profile.empty_count,
        "empty_keys": profile.empty_values,
        "prefixes": profile.prefixes,
        "top_prefix": profile.top_prefix,
        "longest_key": profile.longest_key,
        "longest_value_key": profile.longest_value_key,
        "has_secrets_hint": profile.has_secrets_hint,
    }
    Path(output).write_text(json.dumps(data, indent=2), encoding="utf-8")


def export_profiles_json(profiles: List[EnvProfile], output: str) -> None:
    _ensure_parent(output)
    all_data = []
    for p in profiles:
        all_data.append({
            "source": p.source,
            "total_keys": p.total_keys,
            "empty_count": p.empty_count,
            "empty_keys": p.empty_values,
            "prefixes": p.prefixes,
            "top_prefix": p.top_prefix,
            "longest_key": p.longest_key,
            "longest_value_key": p.longest_value_key,
            "has_secrets_hint": p.has_secrets_hint,
        })
    Path(output).write_text(json.dumps(all_data, indent=2), encoding="utf-8")
