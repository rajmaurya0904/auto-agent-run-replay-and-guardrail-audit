from auto_agent_run_replay_and_guardrail_audit.events import (
    FileEditEvent,
    NetworkCallEvent,
    ShellCommandEvent,
    ToolCallEvent,
)
from auto_agent_run_replay_and_guardrail_audit.guardrail import Violation, check_events
from auto_agent_run_replay_and_guardrail_audit.policy import Policy

POLICY = Policy(
    allowed_write_prefixes=["."],
    deny_network=True,
    allowed_network_hosts=[],
    allowed_shell_prefixes=["git", "pytest"],
)


def _events() -> list:
    return [
        FileEditEvent(
            timestamp="2026-01-01T00:00:00Z",
            actor="agent-1",
            path="./src/main.py",
            diff="-old\n+new",
        ),
        FileEditEvent(
            timestamp="2026-01-01T00:00:01Z",
            actor="agent-1",
            path="/etc/passwd",
            diff="-old\n+new",
        ),
        NetworkCallEvent(
            timestamp="2026-01-01T00:00:02Z",
            actor="agent-1",
            host="api.example.com",
            method="GET",
        ),
    ]


def test_check_events_returns_two_violations_with_correct_rule_names() -> None:
    violations = check_events(_events(), POLICY)

    assert len(violations) == 2
    assert [v.rule for v in violations] == ["write-outside-repo", "network-call-denied"]
    assert violations[0].event.path == "/etc/passwd"
    assert violations[1].event.host == "api.example.com"


def test_check_events_no_violations_when_all_in_policy() -> None:
    events = [
        FileEditEvent(
            timestamp="2026-01-01T00:00:00Z",
            actor="agent-1",
            path="./src/main.py",
            diff="-old\n+new",
        ),
        ShellCommandEvent(
            timestamp="2026-01-01T00:00:01Z",
            actor="agent-1",
            command="git status",
            cwd="/repo",
        ),
    ]

    assert check_events(events, POLICY) == []


def test_shell_command_outside_allowed_prefixes_is_denied() -> None:
    events = [
        ShellCommandEvent(
            timestamp="2026-01-01T00:00:00Z",
            actor="agent-1",
            command="rm -rf /",
            cwd="/repo",
        ),
    ]

    violations = check_events(events, POLICY)

    assert len(violations) == 1
    assert violations[0].rule == "shell-command-denied"
    assert violations[0].event.command == "rm -rf /"


def test_network_call_allowed_when_host_matches_and_network_not_denied() -> None:
    policy = Policy(
        allowed_write_prefixes=["."],
        deny_network=False,
        allowed_network_hosts=["api.example.com"],
        allowed_shell_prefixes=[],
    )
    events = [
        NetworkCallEvent(
            timestamp="2026-01-01T00:00:00Z",
            actor="agent-1",
            host="api.example.com",
            method="GET",
        ),
    ]

    assert check_events(events, policy) == []


def test_network_call_denied_when_host_not_in_allowlist() -> None:
    policy = Policy(
        allowed_write_prefixes=["."],
        deny_network=False,
        allowed_network_hosts=["api.example.com"],
        allowed_shell_prefixes=[],
    )
    events = [
        NetworkCallEvent(
            timestamp="2026-01-01T00:00:00Z",
            actor="agent-1",
            host="evil.example.com",
            method="GET",
        ),
    ]

    violations = check_events(events, policy)

    assert len(violations) == 1
    assert violations[0].rule == "network-call-denied"


def test_tool_call_events_are_not_evaluated() -> None:
    events = [
        ToolCallEvent(
            timestamp="2026-01-01T00:00:00Z",
            actor="agent-1",
            tool_name="Read",
            arguments={"path": "foo.py"},
        ),
    ]

    assert check_events(events, POLICY) == []


def test_violation_is_a_dataclass_with_event_rule_and_message() -> None:
    event = FileEditEvent(
        timestamp="2026-01-01T00:00:00Z",
        actor="agent-1",
        path="/etc/passwd",
        diff="-old\n+new",
    )
    violations = check_events([event], POLICY)

    assert len(violations) == 1
    violation = violations[0]
    assert isinstance(violation, Violation)
    assert violation.event is event
    assert violation.rule == "write-outside-repo"
    assert "path" in violation.message or "/etc/passwd" in violation.message
