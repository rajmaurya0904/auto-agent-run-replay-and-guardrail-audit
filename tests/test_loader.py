from pathlib import Path

from auto_agent_run_replay_and_guardrail_audit.events import (
    NetworkCallEvent,
    ShellCommandEvent,
    ToolCallEvent,
)
from auto_agent_run_replay_and_guardrail_audit.loader import load_session

FIXTURE = Path(__file__).parent / "fixtures" / "session.jsonl"


def test_load_session_returns_events_in_file_order() -> None:
    events = load_session(FIXTURE)

    assert len(events) == 3
    assert isinstance(events[0], ToolCallEvent)
    assert isinstance(events[1], ShellCommandEvent)
    assert isinstance(events[2], NetworkCallEvent)
    assert events[0].tool_name == "Read"
    assert events[1].command == "ls -la"
    assert events[2].host == "api.example.com"


def test_load_session_skips_blank_lines(tmp_path: Path) -> None:
    session_file = tmp_path / "session.jsonl"
    session_file.write_text(
        '{"type": "network_call", "timestamp": "t", "actor": "a", '
        '"host": "h", "method": "GET"}\n'
        "\n"
        "   \n"
        '{"type": "network_call", "timestamp": "t2", "actor": "a", '
        '"host": "h2", "method": "POST"}\n'
    )

    events = load_session(session_file)

    assert len(events) == 2
    assert events[0].timestamp == "t"
    assert events[1].timestamp == "t2"
