#!/usr/bin/env python3
"""Map named ML-DSA candidate sizes into the existing neutral structural model.

Research only. Not endorsed by Bitcoin Core and not intended for mainnet use.
This adapter does not define Bitcoin Script/output semantics, transaction layout,
consensus rules, activation policy, or a deployment winner. It only reuses the
existing opaque witness-item size model for candidate comparison.
"""

from __future__ import annotations

import json

from scripts.benchmark_auth_material_size import structural_case

EXPECTED_ORDER = ["ML-DSA-44", "ML-DSA-65", "ML-DSA-87"]
# FIPS 204 public-key/signature sizes are repeated here intentionally so this
# structural adapter remains independent of the optional cryptographic backend.
# The dedicated ML-DSA benchmark CI independently validates the same size
# contract against real cryptography==48.0.0 keys/signatures.
EXPECTED_SIZES = {
    "ML-DSA-44": {"public_key_bytes": 1312, "signature_bytes": 2420},
    "ML-DSA-65": {"public_key_bytes": 1952, "signature_bytes": 3309},
    "ML-DSA-87": {"public_key_bytes": 2592, "signature_bytes": 4627},
}


def build_report() -> dict:
    rows = []
    for name in EXPECTED_ORDER:
        sizes = EXPECTED_SIZES[name]
        rows.append(
            {
                "candidate": name,
                "public_key": structural_case(sizes["public_key_bytes"]),
                "signature": structural_case(sizes["signature_bytes"]),
            }
        )
    return {
        "schema_version": 1,
        "research_only": True,
        "endorsed_by_bitcoin_core": False,
        "mainnet_intended": False,
        "network_scope": "none-structural-model",
        "candidate_family": "ML-DSA",
        "hybrid_research_semantics": "classical-and-pq",
        "parameter_set_selected": False,
        "deployment_winner_selected": False,
        "bitcoin_script_semantics_selected": False,
        "output_commitment_semantics_selected": False,
        "consensus_change_selected": False,
        "measurement": "independent opaque witness-item structural overhead",
        "candidates": rows,
    }


def validate_report(report: dict) -> None:
    if not isinstance(report, dict):
        raise ValueError("report must be an object")
    protected = {
        "schema_version": 1,
        "research_only": True,
        "endorsed_by_bitcoin_core": False,
        "mainnet_intended": False,
        "network_scope": "none-structural-model",
        "candidate_family": "ML-DSA",
        "hybrid_research_semantics": "classical-and-pq",
        "parameter_set_selected": False,
        "deployment_winner_selected": False,
        "bitcoin_script_semantics_selected": False,
        "output_commitment_semantics_selected": False,
        "consensus_change_selected": False,
        "measurement": "independent opaque witness-item structural overhead",
    }
    for key, expected in protected.items():
        if report.get(key) != expected:
            raise ValueError(f"protected field drift: {key}")

    rows = report.get("candidates")
    if not isinstance(rows, list) or [row.get("candidate") for row in rows] != EXPECTED_ORDER:
        raise ValueError("candidate order drift")

    for row in rows:
        name = row["candidate"]
        expected = EXPECTED_SIZES[name]
        for field, size_key in (("public_key", "public_key_bytes"), ("signature", "signature_bytes")):
            observed = row.get(field)
            canonical = structural_case(expected[size_key])
            if observed != canonical:
                raise ValueError(f"structural size drift: {name}:{field}")


def main() -> int:
    report = build_report()
    validate_report(report)
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
