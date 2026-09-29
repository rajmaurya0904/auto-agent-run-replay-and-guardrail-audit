"""Smoke test: package imports cleanly. Replace/extend as modules land."""

import auto_agent_run_replay_and_guardrail_audit


def test_version_is_set() -> None:
    assert auto_agent_run_replay_and_guardrail_audit.__version__
