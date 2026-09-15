#!/usr/bin/env python3
"""Validate REGTEST-DEMO-005 reports independently and fail closed.

Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.
This validator does not select an ML-DSA parameter set or define Bitcoin Script,
output/witness, consensus, activation, recovery, trust, custody, or production semantics.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from scripts.validate_regtest_hybrid_evidence import validate_evidence

EXPECTED_CANDIDATES = ("ML-DSA-44", "ML-DSA-65", "ML-DSA-87")
EXPECTED_SIGNATURE_BYTES = {"ML-DSA-44": 2420, "ML-DSA-65": 3309, "ML-DSA-87": 4627}
FORBIDDEN_KEYS = {"winner", "recommended", "recommendation", "rank", "score", "selected", "preferred"}


def _reject_selection_fields(value: object) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key.lower() in FORBIDDEN_KEYS:
                raise ValueError(f"candidate-selection field forbidden: {key}")
            _reject_selection_fields(item)
    elif isinstance(value, list):
        for item in value:
            _reject_selection_fields(item)


def _canonical_sha256(value: dict) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_demo_report(report: object) -> str:
    if not isinstance(report, dict):
        raise ValueError("report must be an object")
    _reject_selection_fields(report)

    expected = {
        "schema_version": 1,
        "research_only": True,
        "network": "regtest",
        "endorsed_by_bitcoin_core": False,
        "mainnet_intended": False,
        "off_consensus": True,
        "parameter_set_selected": False,
        "hybrid_research_semantics": "classical-and-pq",
        "classical_verifier_kind": "external-laboratory-boolean-oracle",
        "bitcoin_core_modified": False,
        "script_semantics_defined": False,
        "consensus_changed": False,
        "pq_valid_signature_accepted": True,
        "pq_altered_transcript_rejected": True,
    }
    for key, value in expected.items():
        if report.get(key) != value:
            raise ValueError(f"invalid {key}")

    candidate = report.get("candidate")
    if candidate not in EXPECTED_CANDIDATES:
        raise ValueError("invalid candidate")
    if report.get("signature_bytes") != EXPECTED_SIGNATURE_BYTES[candidate]:
        raise ValueError("signature size mismatch")
    public_hash = report.get("public_key_sha256")
    if not isinstance(public_hash, str) or len(public_hash) != 64:
        raise ValueError("invalid public-key digest")
    try:
        bytes.fromhex(public_hash)
    except ValueError as exc:
        raise ValueError("invalid public-key digest") from exc

    evidence = report.get("evidence")
    validate_evidence(evidence)
    if not isinstance(evidence, dict):
        raise ValueError("evidence must be an object")
    transcript = evidence.get("transcript")
    if not isinstance(transcript, dict) or transcript.get("candidate") != candidate:
        raise ValueError("candidate/evidence mismatch")
    verification = evidence.get("verification")
    if not isinstance(verification, dict) or verification.get("pq_valid") is not True:
        raise ValueError("PQ evidence must be valid")
    classical = verification.get("classical_valid")
    if type(classical) is not bool:
        raise ValueError("classical evidence must be boolean")
    if verification.get("authorized") is not (classical and True):
        raise ValueError("Classical AND PQ authorization mismatch")

    supplied_digest = report.get("demo_sha256")
    if not isinstance(supplied_digest, str):
        raise ValueError("demo digest missing")
    unsigned = dict(report)
    unsigned.pop("demo_sha256", None)
    recomputed = _canonical_sha256(unsigned)
    if supplied_digest != recomputed:
        raise ValueError("demo digest mismatch")
    return recomputed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    print(validate_demo_report(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
