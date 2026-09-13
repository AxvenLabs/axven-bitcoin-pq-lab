#!/usr/bin/env python3
"""Fail-closed manifest validation for migration research scenarios.

Research only. This module does not select a post-quantum scheme, define hybrid
Bitcoin authorization semantics, change consensus, define activation, assign
recovery authority, or specify treatment of legacy/lost UTXOs.
"""

from __future__ import annotations


_ALLOWED_PHASES = {"baseline", "prepare", "exercise", "rollback", "recovery"}
_ALLOWED_EXPECTATIONS = {"accept", "reject", "unchanged", "observe"}
_FORBIDDEN_DECISION_FIELDS = {
    "pq_scheme",
    "hybrid_semantics",
    "mainnet_activation",
    "fork_deployment",
    "legacy_utxo_policy",
    "lost_coin_policy",
    "recovery_authority",
    "trust_root",
    "key_custody",
}


def _nonempty_string(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def validate_scenario(scenario: dict) -> dict:
    if not isinstance(scenario, dict):
        raise ValueError("scenario must be an object")
    if scenario.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    if scenario.get("research_only") is not True:
        raise ValueError("research_only must be true")
    if scenario.get("network") != "regtest":
        raise ValueError("network must be regtest")
    if scenario.get("upstream_behavior_outside_experiment") != "preserved":
        raise ValueError("upstream_behavior_outside_experiment must be preserved")

    for field in _FORBIDDEN_DECISION_FIELDS:
        if field in scenario:
            raise ValueError(f"high-impact decision field is not permitted: {field}")

    _nonempty_string(scenario.get("scenario_id"), "scenario_id")
    _nonempty_string(scenario.get("title"), "title")
    _nonempty_string(scenario.get("purpose"), "purpose")

    assumptions = scenario.get("assumptions")
    if not isinstance(assumptions, list) or not assumptions:
        raise ValueError("assumptions must be a non-empty list")
    for index, assumption in enumerate(assumptions):
        _nonempty_string(assumption, f"assumptions[{index}]")

    steps = scenario.get("steps")
    if not isinstance(steps, list) or not steps:
        raise ValueError("steps must be a non-empty list")

    seen_ids: set[str] = set()
    for index, step in enumerate(steps):
        if not isinstance(step, dict):
            raise ValueError(f"steps[{index}] must be an object")
        step_id = _nonempty_string(step.get("id"), f"steps[{index}].id")
        if step_id in seen_ids:
            raise ValueError(f"duplicate step id: {step_id}")
        seen_ids.add(step_id)
        phase = step.get("phase")
        if phase not in _ALLOWED_PHASES:
            raise ValueError(f"steps[{index}].phase is invalid")
        expectation = step.get("expectation")
        if expectation not in _ALLOWED_EXPECTATIONS:
            raise ValueError(f"steps[{index}].expectation is invalid")
        _nonempty_string(step.get("action"), f"steps[{index}].action")
        _nonempty_string(step.get("evidence"), f"steps[{index}].evidence")

    decision_gates = scenario.get("decision_gates")
    if not isinstance(decision_gates, list) or not decision_gates:
        raise ValueError("decision_gates must be a non-empty list")
    for index, gate in enumerate(decision_gates):
        _nonempty_string(gate, f"decision_gates[{index}]")

    return scenario
