"""Formatters for envdiff output (text, json, csv)."""

import json
import csv
import io
from typing import Literal
from envdiff.comparator import DiffResult

OutputFormat = Literal["text", "json", "csv"]


def format_text(result: DiffResult, base_name: str = "base", target_name: str = "target") -> str:
    """Format diff result as plain text."""
    lines = []

    if result.missing_in_target:
        lines.append(f"Missing in {target_name}:")
        for key in sorted(result.missing_in_target):
            lines.append(f"  - {key}")

    if result.missing_in_base:
        lines.append(f"Missing in {base_name}:")
        for key in sorted(result.missing_in_base):
            lines.append(f"  - {key}")

    if result.mismatched:
        lines.append("Value mismatches:")
        for key in sorted(result.mismatched):
            base_val, target_val = result.mismatched[key]
            lines.append(f"  ~ {key}: {base_name}={base_val!r} | {target_name}={target_val!r}")

    if not lines:
        lines.append("No differences found.")

    return "\n".join(lines)


def format_json(result: DiffResult, base_name: str = "base", target_name: str = "target") -> str:
    """Format diff result as JSON."""
    data = {
        f"missing_in_{target_name}": sorted(result.missing_in_target),
        f"missing_in_{base_name}": sorted(result.missing_in_base),
        "mismatched": {
            key: {base_name: bv, target_name: tv}
            for key, (bv, tv) in sorted(result.mismatched.items())
        },
    }
    return json.dumps(data, indent=2)


def format_csv(result: DiffResult, base_name: str = "base", target_name: str = "target") -> str:
    """Format diff result as CSV."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["type", "key", base_name, target_name])

    for key in sorted(result.missing_in_target):
        writer.writerow(["missing_in_target", key, "", ""])

    for key in sorted(result.missing_in_base):
        writer.writerow(["missing_in_base", key, "", ""])

    for key in sorted(result.mismatched):
        base_val, target_val = result.mismatched[key]
        writer.writerow(["mismatch", key, base_val, target_val])

    return buf.getvalue().rstrip("\n")


def format_result(
    result: DiffResult,
    fmt: OutputFormat = "text",
    base_name: str = "base",
    target_name: str = "target",
) -> str:
    """Dispatch to the appropriate formatter."""
    if fmt == "json":
        return format_json(result, base_name, target_name)
    if fmt == "csv":
        return format_csv(result, base_name, target_name)
    return format_text(result, base_name, target_name)
