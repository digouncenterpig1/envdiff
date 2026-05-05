"""Format and print DiffResult to the terminal."""

from envdiff.comparator import DiffResult

GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"


def _colorize(text: str, color: str) -> str:
    return f"{color}{text}{RESET}"


def report(diff: DiffResult, no_color: bool = False) -> str:
    """
    Build a human-readable report string from a DiffResult.

    Args:
        diff: The DiffResult to format.
        no_color: If True, strip ANSI color codes.

    Returns:
        A formatted string report.
    """
    def c(text: str, color: str) -> str:
        return text if no_color else _colorize(text, color)

    lines = []
    header = f"Comparing {c(diff.base_name, CYAN)} → {c(diff.target_name, CYAN)}"
    lines.append(header)
    lines.append("-" * 50)

    if not diff.has_differences:
        lines.append(c("✓ No differences found.", GREEN))
        return "\n".join(lines)

    if diff.missing_in_target:
        lines.append(c(f"Keys missing in {diff.target_name}:", RED))
        for key in diff.missing_in_target:
            lines.append(f"  {c('-', RED)} {key}")

    if diff.missing_in_base:
        lines.append(c(f"Keys missing in {diff.base_name}:", YELLOW))
        for key in diff.missing_in_base:
            lines.append(f"  {c('+', YELLOW)} {key}")

    if diff.value_mismatches:
        lines.append(c("Value mismatches:", BOLD))
        for key, (base_val, target_val) in diff.value_mismatches.items():
            lines.append(f"  {c('~', CYAN)} {key}")
            lines.append(f"      {diff.base_name}: {base_val!r}")
            lines.append(f"      {diff.target_name}: {target_val!r}")

    return "\n".join(lines)


def print_report(diff: DiffResult, no_color: bool = False) -> None:
    """Print the diff report to stdout."""
    print(report(diff, no_color=no_color))
