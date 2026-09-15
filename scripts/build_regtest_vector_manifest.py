#!/usr/bin/env python3
"""Build a deterministic manifest for validated public regtest vectors.

Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.
No ML-DSA parameter set, Script/output/witness semantics, consensus, activation,
legacy-UTXO treatment, recovery, trust, custody, or production semantics are selected.
"""
from __future__ import annotations

import hashlib
import json

from scripts.build_regtest_mldsa_vector_bundle import build_bundle
from scripts.validate_regtest_mldsa_vector_bundle import validate_bundle


def _digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def build_manifest() -> dict:
    bundle = build_bundle()
    validated_digest = validate_bundle(bundle)
    if validated_digest != bundle["bundle_sha256"]:
        raise RuntimeError("validated bundle digest mismatch")
    payload = {
        "schema_version": 1,
        "research_only": True,
        "network": "regtest",
        "endorsed_by_bitcoin_core": False,
        "mainnet_intended": False,
        "off_consensus": True,
        "candidate_family": "ML-DSA",
        "candidates": ["ML-DSA-44", "ML-DSA-65", "ML-DSA-87"],
        "parameter_set_selected": False,
        "hybrid_research_semantics": "classical-and-pq",
        "bitcoin_core_modified": False,
        "script_semantics_defined": False,
        "consensus_changed": False,
        "source_bundle_sha256": validated_digest,
        "vector_count": len(bundle["vectors"]),
        "correctness_oracle_separate": True,
        "timing_data_included": False,
    }
    return {**payload, "manifest_sha256": _digest(payload)}


if __name__ == "__main__":
    print(json.dumps(build_manifest(), sort_keys=True, indent=2))
