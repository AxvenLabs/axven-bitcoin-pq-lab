#!/usr/bin/env python3
"""Fail-closed negative correctness oracle for ML-DSA research candidates.

Research only. Not endorsed by Bitcoin Core and not intended for mainnet.
This module does not select an ML-DSA parameter set, define Bitcoin Script or
consensus semantics, choose activation/fork policy, or modify Bitcoin Core.
"""

from __future__ import annotations

import json

from cryptography.exceptions import InvalidSignature

from scripts.benchmark_mldsa_candidates import CANDIDATES, EXPECTED_SIZES

MESSAGE = b"axven-bitcoin-pq-lab-negative-oracle-v1"


def _keypair(name: str, suffix: bytes = b"primary"):
    cls = CANDIDATES[name]
    seed = (name.encode("ascii") + b"|negative-oracle|" + suffix).ljust(32, b"\0")[:32]
    private_key = cls.from_seed_bytes(seed)
    return private_key, private_key.public_key()


def _expect_rejected(public_key, signature: bytes, message: bytes) -> bool:
    try:
        public_key.verify(signature, message)
    except (InvalidSignature, ValueError):
        return True
    raise RuntimeError("negative correctness oracle accepted invalid authorization material")


def candidate_oracle(name: str) -> dict:
    if name not in CANDIDATES:
        raise ValueError(f"unsupported candidate: {name}")

    private_key, public_key = _keypair(name)
    _, wrong_public_key = _keypair(name, b"wrong-key")
    signature = private_key.sign(MESSAGE)

    expected = EXPECTED_SIZES[name]
    public_raw = public_key.public_bytes_raw()
    if len(public_raw) != expected["public_key_bytes"]:
        raise RuntimeError("unexpected ML-DSA public-key size")
    if len(signature) != expected["signature_bytes"]:
        raise RuntimeError("unexpected ML-DSA signature size")

    public_key.verify(signature, MESSAGE)

    altered_message = MESSAGE[:-1] + bytes([MESSAGE[-1] ^ 1])
    corrupted_signature = bytearray(signature)
    corrupted_signature[len(corrupted_signature) // 2] ^= 1

    return {
        "candidate": name,
        "valid_signature_accepted": True,
        "altered_message_rejected": _expect_rejected(public_key, signature, altered_message),
        "corrupted_signature_rejected": _expect_rejected(public_key, bytes(corrupted_signature), MESSAGE),
        "wrong_public_key_rejected": _expect_rejected(wrong_public_key, signature, MESSAGE),
        "truncated_signature_rejected": _expect_rejected(public_key, signature[:-1], MESSAGE),
        "oversized_signature_rejected": _expect_rejected(public_key, signature + b"\0", MESSAGE),
    }


def build_oracle_report() -> dict:
    rows = [candidate_oracle(name) for name in CANDIDATES]
    return {
        "schema_version": 1,
        "research_only": True,
        "endorsed_by_bitcoin_core": False,
        "mainnet_intended": False,
        "network_scope": "none-local-cryptographic-correctness-oracle",
        "candidate_family": "ML-DSA",
        "hybrid_research_semantics": "classical-and-pq",
        "parameter_set_selected": False,
        "deployment_winner_selected": False,
        "bitcoin_core_modified": False,
        "bitcoin_script_semantics_selected": False,
        "consensus_change_selected": False,
        "candidates": rows,
    }


def validate_oracle_report(report: dict) -> None:
    if not isinstance(report, dict):
        raise ValueError("oracle report must be an object")
    protected = {
        "research_only": True,
        "endorsed_by_bitcoin_core": False,
        "mainnet_intended": False,
        "candidate_family": "ML-DSA",
        "hybrid_research_semantics": "classical-and-pq",
        "parameter_set_selected": False,
        "deployment_winner_selected": False,
        "bitcoin_core_modified": False,
        "bitcoin_script_semantics_selected": False,
        "consensus_change_selected": False,
    }
    for key, expected in protected.items():
        if report.get(key) != expected:
            raise ValueError(f"protected oracle field changed: {key}")

    rows = report.get("candidates")
    if not isinstance(rows, list) or [row.get("candidate") for row in rows] != list(CANDIDATES):
        raise ValueError("candidate set/order must remain ML-DSA-44/65/87")

    checks = (
        "valid_signature_accepted",
        "altered_message_rejected",
        "corrupted_signature_rejected",
        "wrong_public_key_rejected",
        "truncated_signature_rejected",
        "oversized_signature_rejected",
    )
    for row in rows:
        for check in checks:
            if row.get(check) is not True:
                raise ValueError(f"correctness oracle check failed: {row['candidate']}:{check}")


def main() -> int:
    report = build_oracle_report()
    validate_oracle_report(report)
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
