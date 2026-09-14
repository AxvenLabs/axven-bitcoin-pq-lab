#!/usr/bin/env python3
"""Deterministic, off-consensus hybrid authorization transcript for regtest research.

Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.
This module does not modify Bitcoin Core, define Script/output commitment semantics,
change consensus, select an ML-DSA parameter set, or create a coin/network.
"""

from __future__ import annotations

import hashlib
import json

DOMAIN = "axven-bitcoin-pq-lab/regtest-hybrid-transcript/v1"
_ALLOWED_CANDIDATES = {"ML-DSA-44", "ML-DSA-65", "ML-DSA-87"}


def _hex(value: object, name: str, length: int) -> str:
    if not isinstance(value, str) or len(value) != length:
        raise ValueError(f"{name} must be {length} hex characters")
    try:
        bytes.fromhex(value)
    except ValueError as exc:
        raise ValueError(f"{name} must be hexadecimal") from exc
    return value.lower()


def build_transcript(*, txid: str, vout: int, message_digest: str, candidate: str) -> dict:
    """Build a deterministic laboratory transcript bound to a regtest outpoint.

    The transcript is deliberately off-consensus: it is evidence for a test harness,
    not a Bitcoin transaction, Script program, output commitment, or activation rule.
    """
    txid = _hex(txid, "txid", 64)
    message_digest = _hex(message_digest, "message_digest", 64)
    if not isinstance(vout, int) or isinstance(vout, bool) or vout < 0 or vout > 0xFFFFFFFF:
        raise ValueError("vout must be a uint32")
    if candidate not in _ALLOWED_CANDIDATES:
        raise ValueError("candidate must be one of ML-DSA-44/65/87")

    payload = {
        "schema_version": 1,
        "research_only": True,
        "network": "regtest",
        "endorsed_by_bitcoin_core": False,
        "mainnet_intended": False,
        "domain": DOMAIN,
        "outpoint": {"txid": txid, "vout": vout},
        "message_digest": message_digest,
        "candidate": candidate,
        "hybrid_research_semantics": "classical-and-pq",
        "parameter_set_selected": False,
        "script_semantics_defined": False,
        "consensus_changed": False,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {**payload, "transcript_sha256": hashlib.sha256(encoded).hexdigest()}


def hybrid_gate(*, classical_valid: bool, pq_valid: bool) -> bool:
    """Research-candidate AND gate; both independent verifiers must succeed."""
    if type(classical_valid) is not bool or type(pq_valid) is not bool:
        raise TypeError("verification results must be booleans")
    return classical_valid and pq_valid
