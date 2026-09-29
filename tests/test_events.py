import pytest

from auto_agent_run_replay_and_guardrail_audit.events import (
    FileEditEvent,
    NetworkCallEvent,
    ShellCommandEvent,
    ToolCallEvent,
    parse_event,
)

SAMPLES = [
    (
        {
            "type": "tool_call",
            "timestamp": "2026-01-01T00:00:00Z",
            "actor": "agent-1",
            "tool_name": "Read",
            "arguments": {"path": "foo.py"},
        },
        ToolCallEvent,
    ),
    (
        {
            "type": "shell_command",
            "timestamp": "2026-01-01T00:00:01Z",
            "actor": "agent-1",
            "command": "ls -la",
            "cwd": "/tmp",
        },
        ShellCommandEvent,
    ),
    (
        {
            "type": "file_edit",
            "timestamp": "2026-01-01T00:00:02Z",
            "actor": "agent-1",
            "path": "foo.py",
            "diff": "-old\n+new",
        },
        FileEditEvent,
    ),
    (
        {
            "type": "network_call",
            "timestamp": "2026-01-01T00:00:03Z",
            "actor": "agent-1",
            "host": "api.example.com",
            "method": "GET",
        },
        NetworkCallEvent,
    ),
]


@pytest.mark.parametrize("data,expected_cls", SAMPLES)
def test_parse_event_dispatches_to_expected_class(data, expected_cls) -> None:
    event = parse_event(data)
    assert isinstance(event, expected_cls)


@pytest.mark.parametrize("data,_expected_cls", SAMPLES)
def test_round_trip_to_dict(data, _expected_cls) -> None:
    assert parse_event(data).to_dict() == data


def test_unknown_type_raises_value_error() -> None:
    with pytest.raises(ValueError, match="unknown event type"):
        parse_event({"type": "bogus"})


def test_missing_type_raises_value_error() -> None:
    with pytest.raises(ValueError, match="missing required field 'type'"):
        parse_event({"actor": "agent-1"})


def test_missing_field_raises_value_error() -> None:
    with pytest.raises(ValueError, match="missing required field"):
        parse_event({"type": "shell_command", "timestamp": "t", "actor": "a"})
