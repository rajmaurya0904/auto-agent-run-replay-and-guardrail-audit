from pathlib import Path

import pytest

from auto_agent_run_replay_and_guardrail_audit.policy import Policy, load_policy

EXAMPLE_POLICY = Path(__file__).parent.parent / "examples" / "policy.yaml"


def test_load_policy_from_example_yaml() -> None:
    policy = load_policy(EXAMPLE_POLICY)

    assert policy == Policy(
        allowed_write_prefixes=["."],
        deny_network=True,
        allowed_network_hosts=[],
        allowed_shell_prefixes=["git", "pytest", "ruff"],
    )


def test_load_policy_unknown_key_raises(tmp_path: Path) -> None:
    policy_file = tmp_path / "policy.yaml"
    policy_file.write_text("allowed_write_prefixes: ['.']\nnot_a_real_key: true\n")

    with pytest.raises(ValueError, match="unknown policy key"):
        load_policy(policy_file)


def test_load_policy_malformed_value_raises(tmp_path: Path) -> None:
    policy_file = tmp_path / "policy.yaml"
    policy_file.write_text('deny_network: "yes"\n')

    with pytest.raises(ValueError, match="deny_network"):
        load_policy(policy_file)


def test_load_policy_minimal_file_uses_defaults(tmp_path: Path) -> None:
    policy_file = tmp_path / "policy.yaml"
    policy_file.write_text("{}\n")

    policy = load_policy(policy_file)

    assert policy == Policy(
        allowed_write_prefixes=[],
        deny_network=True,
        allowed_network_hosts=[],
        allowed_shell_prefixes=[],
    )
