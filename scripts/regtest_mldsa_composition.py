#!/usr/bin/env python3
"""Compose candidate-neutral ML-DSA evidence for a real regtest outpoint.

Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.
Bitcoin Core/Script/consensus are unmodified and Bitcoin Core does not validate
ML-DSA. The classical result is an external laboratory boolean oracle.
"""
from __future__ import annotations

import argparse
import hashlib
import json

from scripts.run_regtest_mldsa_hybrid_demo import CANDIDATES, run_demo


def _sha256(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def build_composition(*, txid: str, vout: int, message_digest: str) -> dict:
    candidates = {}
    for candidate in CANDIDATES:
        positive = run_demo(txid=txid, vout=vout, message_digest=message_digest,
                            candidate=candidate, classical_valid=True)
        negative = run_demo(txid=txid, vout=vout, message_digest=message_digest,
                            candidate=candidate, classical_valid=False)
        if not positive["evidence"]["verification"]["authorized"]:
            raise RuntimeError("positive Classical AND PQ case was not authorized")
        if negative["evidence"]["verification"]["authorized"]:
            raise RuntimeError("negative Classical AND PQ case was authorized")
        if not positive["pq_altered_transcript_rejected"]:
            raise RuntimeError("altered transcript was not rejected")
        # ML-DSA signatures are randomized. Keep per-run demo digests out of the
        # canonical composition so identical research inputs produce identical
        # composition evidence without pretending signature bytes are deterministic.
        candidates[candidate] = {
            "public_key_sha256": positive["public_key_sha256"],
            "signature_bytes": positive["signature_bytes"],
            "valid_signature_accepted": positive["pq_valid_signature_accepted"],
            "altered_transcript_rejected": positive["pq_altered_transcript_rejected"],
            "classical_and_pq_positive_authorized": positive["evidence"]["verification"]["authorized"],
            "classical_false_pq_true_authorized": negative["evidence"]["verification"]["authorized"],
        }

    payload = {
        "schema_version": 1,
        "research_only": True,
        "network": "regtest",
        "endorsed_by_bitcoin_core": False,
        "mainnet_intended": False,
        "off_consensus": True,
        "bitcoin_core_modified": False,
        "script_semantics_defined": False,
        "consensus_changed": False,
        "parameter_set_selected": False,
        "hybrid_research_semantics": "classical-and-pq",
        "classical_verifier_kind": "external-laboratory-boolean-oracle",
        "outpoint": {"txid": txid, "vout": vout},
        "message_digest": message_digest,
        "candidates": candidates,
    }
    return {**payload, "composition_sha256": _sha256(payload)}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--txid", required=True)
    p.add_argument("--vout", type=int, required=True)
    p.add_argument("--message-digest", required=True)
    a = p.parse_args()
    print(json.dumps(build_composition(txid=a.txid, vout=a.vout, message_digest=a.message_digest),
                     sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
