from auto_agent_run_replay_and_guardrail_audit.events import (
    FileEditEvent,
    NetworkCallEvent,
    ShellCommandEvent,
)
from auto_agent_run_replay_and_guardrail_audit.timeline import render_timeline

EVENTS = [
    FileEditEvent(
        timestamp="2026-01-01T00:00:00Z",
        actor="agent-1",
        path="/tmp/x.py",
        diff="-old\n+new",
    ),
    ShellCommandEvent(
        timestamp="2026-01-01T00:00:01Z",
        actor="agent-1",
        command="rm -rf build",
        cwd="/tmp",
    ),
    NetworkCallEvent(
        timestamp="2026-01-01T00:00:02Z",
        actor="agent-1",
        host="https://api.example.com",
        method="GET",
    ),
]


def test_render_timeline_has_one_line_per_event_in_order() -> None:
    """Three-event fixture renders exactly 3 non-empty lines, chronologically."""
    output = render_timeline(EVENTS)
    lines = output.split("\n")
    assert len(lines) == 3
    assert all(line.strip() for line in lines)
    kind_labels = ["WRITE", "SHELL", "NET"]
    for event, label, line in zip(EVENTS, kind_labels, lines, strict=True):
        assert event.timestamp in line
        assert label in line


def test_render_timeline_kind_specific_summaries() -> None:
    """Each line shows a short kind-specific summary of the event."""
    output = render_timeline(EVENTS)
    lines = output.split("\n")
    assert lines[0] == "2026-01-01T00:00:00Z WRITE /tmp/x.py"
    assert lines[1] == "2026-01-01T00:00:01Z SHELL rm -rf build"
    assert lines[2] == "2026-01-01T00:00:02Z NET GET https://api.example.com"


def test_render_timeline_empty_list() -> None:
    assert render_timeline([]) == ""
