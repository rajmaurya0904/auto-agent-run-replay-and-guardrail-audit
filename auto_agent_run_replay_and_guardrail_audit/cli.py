"""Command-line interface for replaying recorded agent run sessions."""

from __future__ import annotations

import argparse
import sys

from .loader import load_session
from .timeline import render_timeline


def _replay(args: argparse.Namespace) -> int:
    events = load_session(args.session_file)
    print(render_timeline(events))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agent-audit")
    subparsers = parser.add_subparsers(dest="command", required=True)

    replay_parser = subparsers.add_parser(
        "replay", help="Print a recorded session as a human-readable timeline"
    )
    replay_parser.add_argument("session_file", help="Path to a JSONL session recording")
    replay_parser.set_defaults(func=_replay)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (OSError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
