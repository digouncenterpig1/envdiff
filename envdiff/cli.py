"""Command-line interface for envdiff."""

import argparse
import sys
from pathlib import Path

from envdiff.parser import parse_env_file
from envdiff.comparator import compare_envs, has_differences
from envdiff.reporter import print_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="envdiff",
        description="Compare .env files across environments and surface missing or mismatched keys.",
    )
    parser.add_argument(
        "base",
        metavar="BASE",
        help="Path to the base .env file (e.g. .env.example)",
    )
    parser.add_argument(
        "target",
        metavar="TARGET",
        help="Path to the target .env file to compare against base",
    )
    parser.add_argument(
        "--no-color",
        action="store_true",
        default=False,
        help="Disable colored output",
    )
    parser.add_argument(
        "--values",
        action="store_true",
        default=False,
        help="Show values in the diff output (hidden by default)",
    )
    parser.add_argument(
        "--exit-code",
        action="store_true",
        default=False,
        help="Exit with code 1 if differences are found",
    )
    return parser


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    base_path = Path(args.base)
    target_path = Path(args.target)

    for path in (base_path, target_path):
        if not path.exists():
            print(f"envdiff: error: file not found: {path}", file=sys.stderr)
            return 2
        if not path.is_file():
            print(f"envdiff: error: not a file: {path}", file=sys.stderr)
            return 2

    base_env = parse_env_file(base_path)
    target_env = parse_env_file(target_path)

    result = compare_envs(base_env, target_env)

    print_report(
        result,
        base_label=str(base_path),
        target_label=str(target_path),
        show_values=args.values,
        color=not args.no_color,
    )

    if args.exit_code and has_differences(result):
        return 1
    return 0


def main() -> None:
    sys.exit(run())


if __name__ == "__main__":
    main()
