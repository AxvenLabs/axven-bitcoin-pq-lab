#!/usr/bin/env python3
"""Validate deterministic Phase 3 evidence-replay receipts."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

EXPECTED_KEYS = {
    "schema_version",
    "input_e2e_sha256",
    "validator_result",
    "validator_schema_version",
    "research_only",
    "off_consensus",
    "bitcoin_core_modified",
    "mainnet_intended",
    "parameter_set_selected",
    "replay_receipt_sha256",
}
EXPECTED_SCHEMA_VERSION = 1
EXPECTED_VALIDATOR_SCHEMA_VERSION = 1
MAX_RECEIPT_BYTES = 64 * 1024


def _canonical_digest(value: object) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(encoded).hexdigest()


def _is_canonical_sha256(value: object) -> bool:
    if not isinstance(value, str) or len(value) != 64 or value != value.lower():
        return False
    try:
        raw = bytes.fromhex(value)
    except ValueError:
        return False
    return len(raw) == 32


def _reject_duplicate_pairs(pairs: list[tuple[str, object]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate replay receipt field: {key}")
        result[key] = value
    return result


def load_replay_receipt(path: Path) -> object:
    """Load a bounded receipt JSON without accepting duplicate object keys."""
    with path.open("rb") as handle:
        raw = handle.read(MAX_RECEIPT_BYTES + 1)
    if len(raw) > MAX_RECEIPT_BYTES:
        raise ValueError("replay receipt exceeds size limit")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("replay receipt is not valid UTF-8") from exc
    return json.loads(text, object_pairs_hook=_reject_duplicate_pairs)


def validate_replay_receipt(receipt: dict) -> str:
    """Fail closed unless a receipt is canonical, complete, and research-only."""
    if not isinstance(receipt, dict) or set(receipt) != EXPECTED_KEYS:
        raise ValueError("unexpected replay receipt fields")
    schema_version = receipt["schema_version"]
    if type(schema_version) is not int or schema_version != EXPECTED_SCHEMA_VERSION:
        raise ValueError("unsupported replay receipt schema")
    validator_schema_version = receipt["validator_schema_version"]
    if type(validator_schema_version) is not int or validator_schema_version != EXPECTED_VALIDATOR_SCHEMA_VERSION:
        raise ValueError("unsupported validator schema version")
    digest = receipt["input_e2e_sha256"]
    if not _is_canonical_sha256(digest):
        raise ValueError("invalid input evidence digest")
    if receipt["validator_result"] != "accepted":
        raise ValueError("replay receipt is not accepted")
    expected_safety = {
        "research_only": True,
        "off_consensus": True,
        "bitcoin_core_modified": False,
        "mainnet_intended": False,
        "parameter_set_selected": False,
    }
    for key, expected in expected_safety.items():
        if receipt[key] is not expected:
            raise ValueError(f"invalid safety boundary: {key}")

    claimed = receipt["replay_receipt_sha256"]
    if not _is_canonical_sha256(claimed):
        raise ValueError("invalid replay receipt digest")
    unsigned = dict(receipt)
    del unsigned["replay_receipt_sha256"]
    actual = _canonical_digest(unsigned)
    if claimed != actual:
        raise ValueError("replay receipt digest mismatch")
    return actual


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", type=Path)
    args = parser.parse_args()
    receipt = load_replay_receipt(args.receipt)
    print(validate_replay_receipt(receipt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
