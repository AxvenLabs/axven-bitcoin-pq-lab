#!/usr/bin/env python3
"""Fail-closed validator for deterministic public regtest ML-DSA vectors.

Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.
This validates off-consensus public laboratory evidence only. It does not select an
ML-DSA parameter set or define Script/output/witness, consensus, activation,
legacy UTXO, recovery, trust, custody, or production security semantics.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from scripts.build_regtest_mldsa_vector_bundle import CANDIDATES, MESSAGE_DIGEST, TXID, VOUT

EXPECTED_SIGNATURE_BYTES = {"ML-DSA-44": 2420, "ML-DSA-65": 3309, "ML-DSA-87": 4627}
FORBIDDEN_KEYS = {"winner", "recommended", "recommendation", "rank", "score", "selected", "preferred", "private_key", "seed", "signature"}


def _digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _reject_forbidden(value: object) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key.lower() in FORBIDDEN_KEYS:
                raise ValueError(f"forbidden field: {key}")
            _reject_forbidden(item)
    elif isinstance(value, list):
        for item in value:
            _reject_forbidden(item)


def _hex64(value: object, name: str) -> None:
    if not isinstance(value, str) or len(value) != 64:
        raise ValueError(f"invalid {name}")
    try:
        bytes.fromhex(value)
    except ValueError as exc:
        raise ValueError(f"invalid {name}") from exc


def validate_bundle(bundle: object) -> str:
    if not isinstance(bundle, dict):
        raise ValueError("bundle must be an object")
    _reject_forbidden(bundle)
    expected = {
        "schema_version": 1,
        "research_only": True,
        "network": "regtest",
        "endorsed_by_bitcoin_core": False,
        "mainnet_intended": False,
        "off_consensus": True,
        "candidate_family": "ML-DSA",
        "candidates": list(CANDIDATES),
        "parameter_set_selected": False,
        "hybrid_research_semantics": "classical-and-pq",
        "bitcoin_core_modified": False,
        "script_semantics_defined": False,
        "consensus_changed": False,
        "correctness_oracle_separate": True,
        "input": {"txid": TXID, "vout": VOUT, "message_digest": MESSAGE_DIGEST},
    }
    for key, value in expected.items():
        if bundle.get(key) != value:
            raise ValueError(f"invalid {key}")

    vectors = bundle.get("vectors")
    if not isinstance(vectors, list) or len(vectors) != 6:
        raise ValueError("expected six vectors")
    expected_pairs = [(name, flag) for name in CANDIDATES for flag in (False, True)]
    actual_pairs = []
    for row in vectors:
        if not isinstance(row, dict) or set(row) != {"candidate", "classical_valid", "authorized", "demo_sha256", "transcript_sha256", "public_key_sha256", "signature_bytes", "pq_altered_transcript_rejected"}:
            raise ValueError("invalid vector schema")
        candidate = row.get("candidate")
        classical = row.get("classical_valid")
        if candidate not in CANDIDATES or type(classical) is not bool:
            raise ValueError("invalid vector identity")
        actual_pairs.append((candidate, classical))
        if row.get("authorized") is not classical:
            raise ValueError("Classical AND PQ result mismatch")
        if row.get("pq_altered_transcript_rejected") is not True:
            raise ValueError("altered transcript was not rejected")
        if row.get("signature_bytes") != EXPECTED_SIGNATURE_BYTES[candidate]:
            raise ValueError("signature size mismatch")
        for key in ("demo_sha256", "transcript_sha256", "public_key_sha256"):
            _hex64(row.get(key), key)
    if actual_pairs != expected_pairs:
        raise ValueError("candidate/classical vector order mismatch")

    supplied = bundle.get("bundle_sha256")
    _hex64(supplied, "bundle_sha256")
    unsigned = dict(bundle)
    unsigned.pop("bundle_sha256", None)
    recomputed = _digest(unsigned)
    if supplied != recomputed:
        raise ValueError("bundle digest mismatch")
    return recomputed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args()
    print(validate_bundle(json.loads(args.bundle.read_text(encoding="utf-8"))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
