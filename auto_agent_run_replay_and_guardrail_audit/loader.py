"""Load recorded agent session events from a JSONL file."""

from __future__ import annotations

import json
from os import PathLike

from .events import Event, parse_event


def load_session(path: str | PathLike[str]) -> list[Event]:
    """Read a JSONL session recording into a list of Events, in file order.

    Blank lines are skipped. Each non-blank line is parsed as a JSON object
    and dispatched to the appropriate Event subclass via `parse_event`.
    """
    events: list[Event] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            stripped = line.strip()
            if not stripped:
                continue
            events.append(parse_event(json.loads(stripped)))
    return events
