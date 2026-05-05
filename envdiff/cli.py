"""CLI entry point for envdiff."""

import argparse
import sys

from envdiff.parser import parse_env_file
from envdiff.comparator import compare_envs, has_differences
from envdiff.formatter import format_result
from envdiff.validator import validate_env_file


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare .env files across environments.",
    )
    parser.add_argument("base", help="Base .env file")
    parser.add_argument("target", help="Target .env file to compare against base")
    parser.add_argument(
        "--format",
        choices=["text", "json", "csv"],
        default="text",
        help="Output format (default: text)",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        help="Exit with code 1 when differences are found",
    )
    parser.add_argument(
        "--validate",
        action="store_true",
        help="Validate .env files before comparing",
    )
    return parser


def _run_validation(path: str, label: str) -> bool:
    """Validate a file and print issues. Returns True if valid."""
    result = validate_env_file(path)
    if not result.is_valid:
        print(f"Validation errors in {label} ({path}):")
        for issue in result.issues:
            print(f"  {issue}")
        return False
    return True


def run(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.validate:
        base_ok = _run_validation(args.base, "base")
        target_ok = _run_validation(args.target, "target")
        if not base_ok or not target_ok:
            return 1

    base_env = parse_env_file(args.base)
    target_env = parse_env_file(args.target)

    diff = compare_envs(base_env, target_env)
    output = format_result(diff, fmt=args.format)
    print(output)

    if args.exit_code and has_differences(diff):
        return 1
    return 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
