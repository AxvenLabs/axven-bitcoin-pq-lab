#!/usr/bin/env python3
"""Replay Phase 2 E2E evidence and emit a deterministic, secret-free receipt."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from scripts.validate_regtest_e2e_evidence import validate_e2e_evidence

RECEIPT_SCHEMA_VERSION = 1


def _canonical_digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def replay_e2e_evidence(evidence: dict) -> dict:
    """Validate untrusted Phase 2 evidence and return only deterministic metadata."""
    validated_digest = validate_e2e_evidence(evidence)
    input_digest = _canonical_digest(evidence)
    if input_digest != validated_digest:
        raise ValueError("validated digest does not bind complete replay input")

    receipt = {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "input_e2e_sha256": input_digest,
        "validator_result": "accepted",
        "validator_schema_version": evidence["schema_version"],
        "research_only": True,
        "off_consensus": True,
        "bitcoin_core_modified": False,
        "mainnet_intended": False,
        "parameter_set_selected": False,
    }
    receipt["replay_receipt_sha256"] = _canonical_digest(receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    evidence = json.loads(args.report.read_text(encoding="utf-8"))
    print(json.dumps(replay_e2e_evidence(evidence), sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
