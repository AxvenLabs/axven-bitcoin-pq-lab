#!/usr/bin/env python3
"""Validate scheme-neutral Axven Bitcoin PQ Lab research vectors.

Research only. Not endorsed by Bitcoin Core and not intended for mainnet use.
This validator deliberately rejects fields that would silently freeze high-impact
Bitcoin migration or security decisions.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REQUIRED_GATES = {
    "cryptographic_scheme_selection",
    "hybrid_authorization_semantics",
    "bitcoin_consensus_or_activation",
    "legacy_or_lost_utxo_treatment",
    "recovery_authority",
    "trust_roots",
    "key_custody",
    "production_security_semantics",
}

FORBIDDEN_DECISION_FIELDS = {
    "pq_scheme",
    "hybrid_semantics",
    "activation_height",
    "fork_height",
    "legacy_utxo_policy",
    "lost_coin_policy",
    "recovery_key",
    "trust_root",
    "custody_model",
}

ALLOWED_CATEGORIES = {"rollback", "failure-recovery", "replay", "migration"}


def validate(document: dict) -> dict:
    if not isinstance(document, dict):
        raise ValueError("vector document must be an object")
    if document.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    if document.get("research_only") is not True:
        raise ValueError("research_only must be true")
    if document.get("endorsement") != "not endorsed by Bitcoin Core":
        raise ValueError("Bitcoin Core non-endorsement label is required")
    scope = document.get("deployment_scope", "")
    if not isinstance(scope, str) or "regtest" not in scope or "not intended for mainnet" not in scope:
        raise ValueError("deployment_scope must explicitly restrict the vectors to regtest/lab")
    if document.get("preserve_upstream_outside_experiment") is not True:
        raise ValueError("upstream preservation must be explicit")

    vectors = document.get("vectors")
    if not isinstance(vectors, list) or not vectors:
        raise ValueError("vectors must be a non-empty list")

    seen = set()
    migration_vector = None
    for vector in vectors:
        if not isinstance(vector, dict):
            raise ValueError("each vector must be an object")
        overlap = FORBIDDEN_DECISION_FIELDS.intersection(vector)
        if overlap:
            raise ValueError(f"forbidden high-impact decision fields: {sorted(overlap)}")
        vector_id = vector.get("id")
        if not isinstance(vector_id, str) or not vector_id.strip() or vector_id in seen:
            raise ValueError("vector ids must be unique non-empty strings")
        seen.add(vector_id)
        category = vector.get("category")
        if category not in ALLOWED_CATEGORIES:
            raise ValueError(f"unsupported vector category: {category!r}")
        for key in ("precondition", "action", "expected"):
            value = vector.get(key)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{vector_id}.{key} must be a non-empty string")
        gates = vector.get("decision_gates")
        if not isinstance(gates, list) or not all(isinstance(gate, str) for gate in gates):
            raise ValueError(f"{vector_id}.decision_gates must be a list of strings")
        if category == "migration":
            migration_vector = vector

    if migration_vector is None:
        raise ValueError("a migration decision-gate vector is required")
    gates = set(migration_vector["decision_gates"])
    if gates != REQUIRED_GATES:
        missing = sorted(REQUIRED_GATES - gates)
        extra = sorted(gates - REQUIRED_GATES)
        raise ValueError(f"migration decision gates mismatch; missing={missing}, extra={extra}")

    return document


def main(argv: list[str]) -> int:
    path = Path(argv[1]) if len(argv) > 1 else Path("vectors/research-scenario-vectors-v1.json")
    with path.open("r", encoding="utf-8") as handle:
        document = json.load(handle)
    validate(document)
    print(json.dumps({"ok": True, "vectors": len(document["vectors"]), "schema_version": 1}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
