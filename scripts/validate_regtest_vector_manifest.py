#!/usr/bin/env python3
"""Fail-closed validator for the deterministic public regtest vector manifest.

Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.
No ML-DSA parameter set, Script/output/witness semantics, consensus, activation,
legacy-UTXO treatment, recovery, trust, custody, or production semantics are selected.
"""
from __future__ import annotations

import hashlib
import json

EXPECTED_CANDIDATES = ["ML-DSA-44", "ML-DSA-65", "ML-DSA-87"]
FORBIDDEN_KEYS = {
    "winner", "recommended", "recommendation", "rank", "score", "selected", "preferred",
    "private_key", "private_key_bytes", "secret", "seed", "raw_signature", "signature_hex",
}


def _digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _reject_forbidden(value: object) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key.lower() in FORBIDDEN_KEYS:
                raise ValueError(f"forbidden manifest field: {key}")
            _reject_forbidden(item)
    elif isinstance(value, list):
        for item in value:
            _reject_forbidden(item)


def validate_manifest(manifest: object) -> str:
    if not isinstance(manifest, dict):
        raise ValueError("manifest must be an object")
    _reject_forbidden(manifest)

    expected = {
        "schema_version": 1,
        "research_only": True,
        "network": "regtest",
        "endorsed_by_bitcoin_core": False,
        "mainnet_intended": False,
        "off_consensus": True,
        "candidate_family": "ML-DSA",
        "candidates": EXPECTED_CANDIDATES,
        "parameter_set_selected": False,
        "hybrid_research_semantics": "classical-and-pq",
        "bitcoin_core_modified": False,
        "script_semantics_defined": False,
        "consensus_changed": False,
        "vector_count": 6,
        "correctness_oracle_separate": True,
        "timing_data_included": False,
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise ValueError(f"invalid {key}")

    source_digest = manifest.get("source_bundle_sha256")
    if not isinstance(source_digest, str) or len(source_digest) != 64:
        raise ValueError("invalid source_bundle_sha256")
    try:
        bytes.fromhex(source_digest)
    except ValueError as exc:
        raise ValueError("invalid source_bundle_sha256") from exc

    claimed = manifest.get("manifest_sha256")
    if not isinstance(claimed, str) or len(claimed) != 64:
        raise ValueError("invalid manifest_sha256")
    payload = {key: value for key, value in manifest.items() if key != "manifest_sha256"}
    actual = _digest(payload)
    if claimed != actual:
        raise ValueError("manifest digest mismatch")
    return actual


if __name__ == "__main__":
    from scripts.build_regtest_vector_manifest import build_manifest

    value = build_manifest()
    print(validate_manifest(value))
