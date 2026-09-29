# Tasks

## 1. Define core event data model (complex)

Add `auto_agent_run_replay_and_guardrail_audit/events.py` with typed event classes (e.g. dataclasses or a discriminated union) for the kinds of recorded actions: ToolCallEvent, ShellCommandEvent, FileEditEvent, NetworkCallEvent. Each carries a timestamp, actor/session id, and kind-specific payload (e.g. file path + diff for edits, command + cwd for shell, host + method for network). Include a `from_dict`/`to_dict` pair per event and a top-level `parse_event(dict) -> Event` dispatcher keyed on a `type` field.

**Acceptance:** `python -c "from auto_agent_run_replay_and_guardrail_audit.events import parse_event"` succeeds; round-tripping a sample dict through `parse_event(...).to_dict()` returns an equal dict.

## 2. Test event data model round-trip and validation (simple)

Add `tests/test_events.py` covering: valid dict for each event kind parses to the right class, unknown `type` raises a clear `ValueError`, and missing required fields raise a clear error. Include a round-trip test (`to_dict` after `parse_event` reproduces the input).

**Acceptance:** `pytest -q tests/test_events.py` passes.

## 3. Implement session recording loader (complex)

Add `auto_agent_run_replay_and_guardrail_audit/loader.py` with `load_session(path) -> list[Event]` that reads a JSONL file (one JSON object per line, each parsed via `parse_event`), skipping blank lines and preserving file order.

**Acceptance:** Given a fixture JSONL file with 3 valid lines, `load_session(path)` returns a list of 3 Event objects in file order.

## 4. Test session loader edge cases (simple)

Add `tests/test_loader.py` covering: a well-formed multi-line JSONL file, a file with blank lines interspersed, an empty file (returns `[]`), a file with one malformed JSON line (raises with the offending line number in the message), and a missing file path (raises `FileNotFoundError`).

**Acceptance:** `pytest -q tests/test_loader.py` passes.

## 5. Implement human-readable timeline renderer (complex)

Add `auto_agent_run_replay_and_guardrail_audit/timeline.py` with `render_timeline(events: list[Event]) -> str` that formats events chronologically, one line per event, showing timestamp, event kind, and a short kind-specific summary (e.g. `WRITE /tmp/x.py`, `SHELL rm -rf build`, `NET GET https://api.example.com`).

**Acceptance:** `render_timeline([...])` on a 3-event fixture list returns a string with exactly 3 non-empty lines in chronological order, each containing the event's timestamp and kind.

## 6. Test timeline renderer output (simple)

Add `tests/test_timeline.py` verifying line count matches event count, chronological ordering is preserved even if input events are out of order (renderer sorts by timestamp), and each event kind produces the expected summary substring.

**Acceptance:** `pytest -q tests/test_timeline.py` passes.

## 7. Design guardrail policy schema and loader (complex)

Add `auto_agent_run_replay_and_guardrail_audit/policy.py` defining a `Policy` dataclass (allowed write path prefixes, e.g. repo root; allowed network hosts or a `deny_network: bool`; allowed shell command prefixes/patterns) plus `load_policy(path) -> Policy` that reads a YAML or TOML file into it, raising a clear error on unknown keys or malformed values. Add `pyyaml` (or use `tomllib` for TOML, stdlib in 3.11+) as needed.

**Acceptance:** `load_policy("examples/policy.yaml")` (a fixture policy file added in this task) returns a `Policy` object with the expected fields populated; loading a file with an unknown key raises `ValueError`.

## 8. Test policy loading and validation errors (simple)

Add `tests/test_policy.py` covering: a valid policy file loads correctly, a file with an unknown top-level key raises, a file with a wrong-typed value (e.g. `deny_network: "yes"` instead of bool) raises, and a minimal policy file (all defaults) loads with sane defaults (deny nothing outside explicit rules, or documented default-deny — pick one and assert it).

**Acceptance:** `pytest -q tests/test_policy.py` passes.

## 9. Implement guardrail checker (complex)

Add `auto_agent_run_replay_and_guardrail_audit/guardrail.py` with `check_events(events: list[Event], policy: Policy) -> list[Violation]`, where `Violation` records the offending event, a rule name (e.g. `write-outside-repo`, `network-call-denied`, `shell-command-denied`), and a human-readable message. Evaluate FileEditEvent paths against allowed prefixes, NetworkCallEvent hosts against policy, and ShellCommandEvent text against denied patterns.

**Acceptance:** Given a fixture event list with one in-policy write, one out-of-repo write, and one disallowed network call, `check_events` returns exactly 2 violations with the correct rule names.

## 10. Test guardrail checker rules (simple)

Add `tests/test_guardrail.py` covering each rule independently (write outside repo flagged, write inside repo not flagged, network call to disallowed host flagged, network call to allowlisted host not flagged, denied shell command pattern flagged) plus a clean-session case that produces zero violations (no false positives).

**Acceptance:** `pytest -q tests/test_guardrail.py` passes.

## 11. Add CLI `replay` command (complex)

Add `auto_agent_run_replay_and_guardrail_audit/cli.py` using `argparse`, with a `replay <session_file>` subcommand that loads the session and prints `render_timeline(...)` to stdout. Wire it up as a console script `agent-audit` via `[project.scripts]` in `pyproject.toml`.

**Acceptance:** After `pip install -e ".[dev]"`, running `agent-audit replay examples/session.jsonl` exits 0 and prints one line per recorded event.

## 12. Test CLI replay command (simple)

Add `tests/test_cli_replay.py` invoking the CLI via `subprocess.run([sys.executable, "-m", "auto_agent_run_replay_and_guardrail_audit.cli", "replay", ...])` (add a `__main__.py` if needed for module invocation), asserting exit code 0 and expected output lines for a fixture session file, and a nonzero exit code with a stderr message for a missing file.

**Acceptance:** `pytest -q tests/test_cli_replay.py` passes.

## 13. Add CLI `audit` command (complex)

Extend `cli.py` with an `audit <session_file> --policy <policy_file>` subcommand that loads the session and policy, runs `check_events`, prints each violation (rule name, event summary, message), and exits with code 1 if any violations are found, 0 otherwise -- suitable for CI gating.

**Acceptance:** `agent-audit audit examples/session.jsonl --policy examples/policy.yaml` exits nonzero and lists violations when the fixture session contains an out-of-policy event; exits 0 and prints a clean-run message for a fixture with no violations.

## 14. Test CLI audit command exit codes (simple)

Add `tests/test_cli_audit.py` asserting exit code 1 with violation text on stdout for a fixture session/policy pair with known violations, and exit code 0 for a clean fixture pair.

**Acceptance:** `pytest -q tests/test_cli_audit.py` passes.

## 15. Add `--only-violations` timeline annotation flag (complex)

Extend `timeline.render_timeline` to accept an optional `violations` argument that inline-marks flagged events (e.g. prefix `[VIOLATION: rule-name]`), and add a `--only-violations` flag to the CLI `replay` command that runs the guardrail checker (requires `--policy`) and filters the timeline to only flagged events.

**Acceptance:** `agent-audit replay examples/session.jsonl --policy examples/policy.yaml --only-violations` prints only the flagged event lines, each prefixed with its rule name.

## 16. Test `--only-violations` flag (simple)

Add a test in `tests/test_cli_replay.py` (or a new `tests/test_cli_annotate.py`) verifying that with `--only-violations` set, output line count equals the number of violations from `check_events` on the same fixture, and each printed line contains its rule name.

**Acceptance:** `pytest -q` includes and passes the new annotation test.

## 17. Add example session and policy fixtures (simple)

Add `examples/session.jsonl` (a realistic recorded session mixing safe and policy-violating events) and `examples/policy.yaml` (a representative repo-scoped policy) used by the CLI tests and README. Ensure both files load cleanly via `load_session`/`load_policy`.

**Acceptance:** `python -c "from auto_agent_run_replay_and_guardrail_audit.loader import load_session; from auto_agent_run_replay_and_guardrail_audit.policy import load_policy; load_session('examples/session.jsonl'); load_policy('examples/policy.yaml')"` exits 0.

## 18. Write README usage, example, and FAQ sections (simple)

Replace the TODO placeholders in `README.md` with a real Usage section documenting `agent-audit replay` and `agent-audit audit` (including `--policy` and `--only-violations`), an Example section walking through `examples/session.jsonl` + `examples/policy.yaml` with sample output, and an FAQ covering supported event types, the policy file format, and CI exit-code behavior.

**Acceptance:** `README.md` contains no remaining `TODO` markers and includes literal `agent-audit replay` and `agent-audit audit` command examples that match the actual CLI flags.

## 19. Harden error handling for malformed sessions and unknown event types (simple)

Review `loader.py`, `events.py`, and `guardrail.py` for unhandled edge cases: truncated/non-JSON lines, an event `type` not recognized by `parse_event`, and empty policy files. Ensure each raises a specific, actionable exception (not a bare `KeyError`/`json.JSONDecodeError` traceback) and add regression tests for each.

**Acceptance:** New tests in `tests/test_loader.py` and `tests/test_events.py` assert the specific exception type and that the message names the file/line or offending field; `pytest -q` passes.

## 20. Add CHANGELOG and finalize v0.1.0 release prep (simple)

Add `CHANGELOG.md` summarizing the v0.1.0 feature set (event model, session replay, policy-based guardrail audit, CLI). Confirm `pyproject.toml` version matches, and run the full check suite.

**Acceptance:** `CHANGELOG.md` exists with a `## 0.1.0` section; `pytest -q` and `ruff check .` both exit 0.
