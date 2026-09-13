#!/usr/bin/env python3
"""Validate the Axven Bitcoin PQ Lab research-only threat model contract.

This validator intentionally does not select a PQ scheme or define Bitcoin
consensus, activation, legacy UTXO policy, recovery authority, trust roots,
key custody, or production security semantics.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED_DECISION_GATES = {
    "consensus_or_mainnet_activation",
    "fork_deployment",
    "cryptographic_scheme_selection",
    "legacy_utxo_treatment",
    "lost_coin_treatment",
    "recovery_authority",
    "trust_roots",
    "key_custody",
    "production_security_semantics",
}

REQUIRED_PROPERTIES = {
    "fail_closed_on_malformed_experimental_evidence",
    "bind_experimental_evidence_to_explicit_regtest_context",
    "preserve_vanilla_behavior_when_experiment_is_off",
    "make_replay_rollback_and_restart_results_reproducible",
    "measure_size_cpu_and_memory_costs_without_claiming_production_security",
    "keep_all_high_impact_design_choices_as_explicit_decision_gates",
}


def _string_set(value: object, name: str) -> set[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{name} must be a non-empty list")
    if any(not isinstance(item, str) or not item.strip() for item in value):
        raise ValueError(f"{name} must contain non-empty strings")
    if len(set(value)) != len(value):
        raise ValueError(f"{name} must not contain duplicates")
    return set(value)


def validate(model: dict) -> dict:
    if not isinstance(model, dict):
        raise ValueError("threat model must be an object")
    if model.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    if model.get("research_only") is not True:
        raise ValueError("research_only must be true")
    if model.get("bitcoin_core_endorsement") is not False:
        raise ValueError("bitcoin_core_endorsement must be false")
    if model.get("mainnet_deployment") is not False:
        raise ValueError("mainnet_deployment must be false")
    if model.get("scope") != "isolated-regtest-authorization-migration-research":
        raise ValueError("scope must remain isolated regtest research")
    if model.get("preserve_upstream_outside_experiment") is not True:
        raise ValueError("upstream behavior must be preserved outside the experiment")

    _string_set(model.get("assets"), "assets")
    _string_set(model.get("adversary_capabilities"), "adversary_capabilities")
    properties = _string_set(model.get("required_properties"), "required_properties")
    _string_set(model.get("out_of_scope"), "out_of_scope")
    gates = _string_set(model.get("decision_gates"), "decision_gates")

    missing_properties = REQUIRED_PROPERTIES - properties
    if missing_properties:
        raise ValueError(f"missing required properties: {sorted(missing_properties)}")
    missing_gates = REQUIRED_DECISION_GATES - gates
    if missing_gates:
        raise ValueError(f"missing decision gates: {sorted(missing_gates)}")
    return model


def main(argv: list[str]) -> int:
    path = Path(argv[1] if len(argv) > 1 else "lab/threat-model-v1.json")
    model = json.loads(path.read_text(encoding="utf-8"))
    validate(model)
    print(json.dumps({"ok": True, "path": str(path)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
