#!/usr/bin/env python3
"""Fail-closed validator for off-consensus regtest hybrid authorization evidence.

Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.
This module validates laboratory evidence only. It does not modify Bitcoin Core,
define Script/output commitment semantics, change consensus, select an ML-DSA
parameter set, or create a coin/network.
"""

from __future__ import annotations

import hashlib
import json

from scripts.regtest_hybrid_transcript import build_transcript, hybrid_gate


_ALLOWED_CANDIDATES = ("ML-DSA-44", "ML-DSA-65", "ML-DSA-87")


def _canonical_sha256(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_transcript(transcript: object) -> dict:
    """Return a canonical validated transcript or fail closed."""
    if not isinstance(transcript, dict):
        raise ValueError("transcript must be an object")

    outpoint = transcript.get("outpoint")
    if not isinstance(outpoint, dict):
        raise ValueError("outpoint must be an object")

    candidate = transcript.get("candidate")
    if candidate not in _ALLOWED_CANDIDATES:
        raise ValueError("candidate must be one of ML-DSA-44/65/87")

    expected = build_transcript(
        txid=outpoint.get("txid"),
        vout=outpoint.get("vout"),
        message_digest=transcript.get("message_digest"),
        candidate=candidate,
    )
    if transcript != expected:
        raise ValueError("transcript does not match canonical research transcript")
    return expected


def build_evidence(*, transcript: object, classical_valid: bool, pq_valid: bool) -> dict:
    """Validate a transcript and bind the Classical AND PQ gate result to evidence."""
    validated = validate_transcript(transcript)
    authorized = hybrid_gate(classical_valid=classical_valid, pq_valid=pq_valid)

    payload = {
        "schema_version": 1,
        "research_only": True,
        "network": "regtest",
        "endorsed_by_bitcoin_core": False,
        "mainnet_intended": False,
        "off_consensus": True,
        "transcript": validated,
        "verification": {
            "classical_valid": classical_valid,
            "pq_valid": pq_valid,
            "hybrid_research_semantics": "classical-and-pq",
            "authorized": authorized,
        },
        "parameter_set_selected": False,
        "script_semantics_defined": False,
        "consensus_changed": False,
    }
    return {**payload, "evidence_sha256": _canonical_sha256(payload)}


def validate_evidence(evidence: object) -> dict:
    """Rebuild evidence from validated inputs and reject any drift or extra fields."""
    if not isinstance(evidence, dict):
        raise ValueError("evidence must be an object")
    verification = evidence.get("verification")
    if not isinstance(verification, dict):
        raise ValueError("verification must be an object")

    expected = build_evidence(
        transcript=evidence.get("transcript"),
        classical_valid=verification.get("classical_valid"),
        pq_valid=verification.get("pq_valid"),
    )
    if evidence != expected:
        raise ValueError("evidence does not match canonical research evidence")
    return expected
