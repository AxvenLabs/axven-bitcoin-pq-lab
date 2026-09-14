#!/usr/bin/env python3
"""Validate ML-DSA benchmark evidence without selecting a deployment winner.

Research only. Not endorsed by Bitcoin Core and not intended for mainnet use.
This validates the existing ML-DSA-44/65/87 benchmark evidence as an external
consumer would. It does not define Bitcoin Script/consensus semantics or select
an ML-DSA parameter set for deployment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path
from typing import Any

EXPECTED_SIZES = {
    "ML-DSA-44": (1312, 2420),
    "ML-DSA-65": (1952, 3309),
    "ML-DSA-87": (2592, 4627),
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _nearest_rank_p95(values: list[int]) -> int:
    _require(len(values) >= 3, "at least three timing samples are required")
    rank = max(1, math.ceil(0.95 * len(values)))
    return sorted(values)[rank - 1]


def canonical_evidence_sha256(report: dict[str, Any]) -> str:
    encoded = json.dumps(report, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def validate_report(report: dict[str, Any]) -> None:
    _require(isinstance(report, dict), "report must be a JSON object")
    _require(report.get("schema_version") == 3, "schema_version must be 3")
    _require(report.get("research_only") is True, "research_only must be true")
    _require(report.get("endorsed_by_bitcoin_core") is False, "endorsed_by_bitcoin_core must be false")
    _require(report.get("mainnet_intended") is False, "mainnet_intended must be false")
    _require(report.get("candidate_family") == "ML-DSA", "candidate_family must be ML-DSA")
    _require(report.get("hybrid_research_semantics") == "classical-and-pq", "hybrid research semantics must be classical-and-pq")
    _require(report.get("parameter_set_selected") is False, "parameter_set_selected must remain false")
    _require(report.get("deployment_winner_selected") is False, "deployment_winner_selected must remain false")
    _require(report.get("bitcoin_core_modified") is False, "bitcoin_core_modified must remain false")
    _require(report.get("bitcoin_script_semantics_selected") is False, "bitcoin_script_semantics_selected must remain false")
    _require(report.get("consensus_change_selected") is False, "consensus_change_selected must remain false")
    _require(report.get("raw_sample_evidence") is True, "raw_sample_evidence must be true")
    _require(report.get("percentile_method") == "nearest-rank", "percentile_method must be nearest-rank")

    for field in ("cryptography_version", "openssl_version", "python_version", "platform"):
        _require(isinstance(report.get(field), str) and bool(report[field].strip()), f"{field} must be non-empty")
    _require(type(report.get("message_bytes")) is int and report["message_bytes"] > 0, "message_bytes must be positive")

    candidates = report.get("candidates")
    _require(isinstance(candidates, list), "candidates must be a list")
    rows = {row.get("candidate"): row for row in candidates if isinstance(row, dict)}
    _require(set(rows) == set(EXPECTED_SIZES), "candidate set must be exactly ML-DSA-44/65/87")
    _require(len(candidates) == len(rows), "candidate rows must be unique objects")

    for name, row in rows.items():
        public_size, signature_size = EXPECTED_SIZES[name]
        _require(row.get("public_key_bytes") == public_size, f"{name} public-key size mismatch")
        _require(row.get("signature_bytes") == signature_size, f"{name} signature size mismatch")
        iterations = row.get("iterations")
        _require(type(iterations) is int and iterations >= 3, f"{name} iterations must be >= 3")

        for prefix in ("verify_wall", "verify_cpu"):
            samples = row.get(f"{prefix}_samples_ns")
            _require(isinstance(samples, list) and len(samples) == iterations, f"{name} {prefix} sample count mismatch")
            _require(all(type(value) is int and value > 0 for value in samples), f"{name} {prefix} samples must be positive integers")
            _require(row.get(f"{prefix}_median_ns") == int(statistics.median(samples)), f"{name} {prefix} median mismatch")
            _require(row.get(f"{prefix}_p95_ns") == _nearest_rank_p95(samples), f"{name} {prefix} p95 mismatch")
            _require(row.get(f"{prefix}_min_ns") == min(samples), f"{name} {prefix} min mismatch")
            _require(row.get(f"{prefix}_max_ns") == max(samples), f"{name} {prefix} max mismatch")

        _require(type(row.get("python_peak_alloc_bytes")) is int and row["python_peak_alloc_bytes"] >= 0, f"{name} python peak allocation invalid")
        _require(type(row.get("process_max_rss_bytes")) is int and row["process_max_rss_bytes"] > 0, f"{name} process RSS invalid")
        _require(type(row.get("process_max_rss_delta_bytes")) is int and row["process_max_rss_delta_bytes"] >= 0, f"{name} RSS delta invalid")
        oracle = row.get("correctness_oracle")
        _require(isinstance(oracle, dict), f"{name} correctness_oracle missing")
        _require(oracle.get("valid_signature_accepted") is True, f"{name} valid signature oracle failed")
        _require(oracle.get("altered_message_rejected") is True, f"{name} altered-message oracle failed")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    validate_report(report)
    print(json.dumps({"ok": True, "canonical_evidence_sha256": canonical_evidence_sha256(report)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
