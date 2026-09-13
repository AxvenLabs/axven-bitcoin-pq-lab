#!/usr/bin/env python3
"""Validate the isolated ML-DSA + classical-AND-PQ research policy.

Research only. Not endorsed by Bitcoin Core and not intended for mainnet use.
This validator freezes only the explicitly approved *regtest research candidate*
choices. It intentionally rejects accidental selection of parameter sets,
consensus/activation policy, legacy/lost UTXO treatment, recovery, trust roots,
key custody, or production security semantics.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

_REQUIRED_FALSE = (
    "parameter_set_selected",
    "bitcoin_consensus_change_selected",
    "activation_or_fork_selected",
    "legacy_utxo_treatment_selected",
    "lost_coin_treatment_selected",
    "recovery_authority_selected",
    "trust_root_selected",
    "key_custody_selected",
    "production_security_semantics_selected",
    "security_engine_source_used",
)


def validate_policy(policy: dict) -> None:
    if policy.get("schema_version") != 1:
        raise ValueError("schema_version must be 1")
    if policy.get("research_only") is not True:
        raise ValueError("research_only must be literal true")
    if policy.get("endorsed_by_bitcoin_core") is not False:
        raise ValueError("endorsed_by_bitcoin_core must be false")
    if policy.get("mainnet_intended") is not False:
        raise ValueError("mainnet_intended must be false")
    if policy.get("network_scope") != "isolated-regtest-only":
        raise ValueError("network_scope must be isolated-regtest-only")
    if policy.get("pq_candidate_family") != "ML-DSA":
        raise ValueError("pq_candidate_family must be ML-DSA")
    if policy.get("hybrid_authorization_semantics") != "classical-and-pq":
        raise ValueError("hybrid authorization must require classical AND PQ")
    if policy.get("selection_scope") != "reversible-research-candidate":
        raise ValueError("selection_scope must remain reversible-research-candidate")
    for field in _REQUIRED_FALSE:
        if policy.get(field) is not False:
            raise ValueError(f"{field} must remain false")


def load_policy(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("policy must be a JSON object")
    validate_policy(data)
    return data


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path",
        nargs="?",
        default="lab/regtest-demo-002-policy.json",
    )
    args = parser.parse_args()
    policy = load_policy(Path(args.path))
    print(json.dumps(policy, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
