import subprocess
import sys
from pathlib import Path

FIXTURE = Path(__file__).parent / "fixtures" / "session.jsonl"
EXAMPLE_SESSION = Path(__file__).parent.parent / "examples" / "session.jsonl"
EXAMPLE_POLICY = Path(__file__).parent.parent / "examples" / "policy.yaml"


def _run(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "auto_agent_run_replay_and_guardrail_audit.cli", *args],
        capture_output=True,
        text=True,
    )


def test_audit_reports_violations_and_exits_nonzero() -> None:
    result = _run("audit", str(EXAMPLE_SESSION), "--policy", str(EXAMPLE_POLICY))

    assert result.returncode == 1
    assert "write-outside-repo" in result.stdout
    assert "network-call-denied" in result.stdout


def test_audit_clean_session_exits_zero(tmp_path: Path) -> None:
    policy_file = tmp_path / "policy.yaml"
    policy_file.write_text(
        "allowed_shell_prefixes: ['ls']\n"
        "deny_network: false\n"
        "allowed_network_hosts: ['api.example.com']\n"
    )

    result = _run("audit", str(FIXTURE), "--policy", str(policy_file))

    assert result.returncode == 0
    assert "no violations" in result.stdout.lower()


def test_audit_missing_policy_file_exits_nonzero_with_stderr_message() -> None:
    result = _run("audit", str(FIXTURE), "--policy", "/nonexistent/policy.yaml")

    assert result.returncode != 0
    assert "error" in result.stderr.lower()
