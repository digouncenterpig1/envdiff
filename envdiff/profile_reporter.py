"""Render EnvProfile summaries to text or JSON."""
from __future__ import annotations

import json
from typing import List

from envdiff.profiler import EnvProfile


def _section(title: str, lines: List[str]) -> str:
    bar = "-" * 40
    body = "\n".join(f"  {l}" for l in lines)
    return f"{bar}\n{title}\n{bar}\n{body}\n"


def format_profile_text(profile: EnvProfile) -> str:
    lines: List[str] = []
    lines.append(f"Source       : {profile.source}")
    lines.append(f"Total keys   : {profile.total_keys}")
    lines.append(f"Empty values : {profile.empty_count}")
    if profile.empty_values:
        lines.append("  Empty keys : " + ", ".join(profile.empty_values))
    lines.append(f"Top prefix   : {profile.top_prefix or 'n/a'}")
    if profile.prefixes:
        top5 = sorted(profile.prefixes.items(), key=lambda x: -x[1])[:5]
        lines.append("  Prefixes   : " + ", ".join(f"{p}({c})" for p, c in top5))
    lines.append(f"Longest key  : {profile.longest_key or 'n/a'}")
    lines.append(f"Secrets hint : {'yes' if profile.has_secrets_hint else 'no'}")
    return _section("ENV PROFILE", lines)


def format_profile_json(profile: EnvProfile) -> str:
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
    return json.dumps(data, indent=2)


def format_profiles_comparison(profiles: List[EnvProfile]) -> str:
    parts = [format_profile_text(p) for p in profiles]
    return "\n".join(parts)
