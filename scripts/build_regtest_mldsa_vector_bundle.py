#!/usr/bin/env python3
"""Build deterministic public vectors for the isolated ML-DSA regtest lab.

Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.
This does not select an ML-DSA parameter set or define Bitcoin Script, output,
witness, consensus, activation, recovery, trust, custody, or production semantics.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from scripts.run_regtest_mldsa_hybrid_demo import run_demo
from scripts.validate_regtest_mldsa_hybrid_demo import validate_demo_report

CANDIDATES = ("ML-DSA-44", "ML-DSA-65", "ML-DSA-87")
TXID = "11" * 32
MESSAGE_DIGEST = "22" * 32
VOUT = 7


def _digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def build_bundle() -> dict:
    vectors = []
    for candidate in CANDIDATES:
        for classical_valid in (False, True):
            report = run_demo(
                txid=TXID,
                vout=VOUT,
                message_digest=MESSAGE_DIGEST,
                candidate=candidate,
                classical_valid=classical_valid,
            )
            validated = validate_demo_report(report)
            if validated != report["demo_sha256"]:
                raise RuntimeError("validated demo digest mismatch")
            vectors.append(
                {
                    "candidate": candidate,
                    "classical_valid": classical_valid,
                    "authorized": report["evidence"]["verification"]["authorized"],
                    "demo_sha256": report["demo_sha256"],
                    "transcript_sha256": report["evidence"]["transcript"]["transcript_sha256"],
                    "public_key_sha256": report["public_key_sha256"],
                    "signature_bytes": report["signature_bytes"],
                    "pq_altered_transcript_rejected": report["pq_altered_transcript_rejected"],
                }
            )

    payload = {
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
        "vectors": vectors,
    }
    return {**payload, "bundle_sha256": _digest(payload)}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    bundle = build_bundle()
    text = json.dumps(bundle, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
