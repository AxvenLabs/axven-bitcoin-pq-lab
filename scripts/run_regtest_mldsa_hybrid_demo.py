#!/usr/bin/env python3
"""Runnable off-consensus ML-DSA hybrid authorization lab harness.

Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.
This harness does not modify Bitcoin Core, define Script/output/witness semantics,
change consensus, select an ML-DSA parameter set, or create a coin/network.
The classical verifier result remains an external laboratory boolean oracle; no
classical production scheme is selected here.
"""

from __future__ import annotations

import argparse
import hashlib
import json

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric import mldsa

from scripts.regtest_hybrid_transcript import build_transcript
from scripts.validate_regtest_hybrid_evidence import build_evidence, validate_evidence


CANDIDATES = {
    "ML-DSA-44": mldsa.MLDSA44PrivateKey,
    "ML-DSA-65": mldsa.MLDSA65PrivateKey,
    "ML-DSA-87": mldsa.MLDSA87PrivateKey,
}
EXPECTED_SIGNATURE_BYTES = {
    "ML-DSA-44": 2420,
    "ML-DSA-65": 3309,
    "ML-DSA-87": 4627,
}


def _sha256_hex(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _candidate_key(candidate: str):
    if candidate not in CANDIDATES:
        raise ValueError("candidate must be one of ML-DSA-44/65/87")
    seed = (candidate.encode("ascii") + b"|axven-bitcoin-pq-lab|regtest-demo-005").ljust(32, b"\0")[:32]
    return CANDIDATES[candidate].from_seed_bytes(seed)


def run_demo(*, txid: str, vout: int, message_digest: str, candidate: str, classical_valid: bool) -> dict:
    """Run one isolated candidate without selecting it for deployment."""
    if type(classical_valid) is not bool:
        raise TypeError("classical_valid must be a boolean laboratory oracle result")

    transcript = build_transcript(
        txid=txid,
        vout=vout,
        message_digest=message_digest,
        candidate=candidate,
    )
    signed_message = bytes.fromhex(transcript["transcript_sha256"])

    private_key = _candidate_key(candidate)
    public_key = private_key.public_key()
    public_raw = public_key.public_bytes_raw()
    signature = private_key.sign(signed_message)
    if len(signature) != EXPECTED_SIGNATURE_BYTES[candidate]:
        raise RuntimeError("unexpected ML-DSA signature size")

    public_key.verify(signature, signed_message)
    try:
        public_key.verify(signature, bytes([signed_message[0] ^ 1]) + signed_message[1:])
    except InvalidSignature:
        altered_transcript_rejected = True
    else:
        raise RuntimeError("ML-DSA failure path accepted an altered transcript")

    evidence = build_evidence(
        transcript=transcript,
        classical_valid=classical_valid,
        pq_valid=True,
    )
    validate_evidence(evidence)

    payload = {
        "schema_version": 1,
        "research_only": True,
        "network": "regtest",
        "endorsed_by_bitcoin_core": False,
        "mainnet_intended": False,
        "off_consensus": True,
        "candidate": candidate,
        "parameter_set_selected": False,
        "hybrid_research_semantics": "classical-and-pq",
        "classical_verifier_kind": "external-laboratory-boolean-oracle",
        "bitcoin_core_modified": False,
        "script_semantics_defined": False,
        "consensus_changed": False,
        "public_key_sha256": _sha256_hex(public_raw),
        "signature_bytes": len(signature),
        "pq_valid_signature_accepted": True,
        "pq_altered_transcript_rejected": altered_transcript_rejected,
        "evidence": evidence,
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return {**payload, "demo_sha256": _sha256_hex(encoded)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate", choices=tuple(CANDIDATES), required=True)
    parser.add_argument("--txid", default="11" * 32)
    parser.add_argument("--vout", type=int, default=0)
    parser.add_argument("--message-digest", default="22" * 32)
    parser.add_argument("--classical-valid", action="store_true")
    args = parser.parse_args()
    report = run_demo(
        txid=args.txid,
        vout=args.vout,
        message_digest=args.message_digest,
        candidate=args.candidate,
        classical_valid=args.classical_valid,
    )
    print(json.dumps(report, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
