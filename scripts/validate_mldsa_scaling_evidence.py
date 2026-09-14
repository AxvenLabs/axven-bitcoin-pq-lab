#!/usr/bin/env python3
"""Fail-closed validator for BENCH-MLDSA-016 scaling evidence.

Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.
This validates benchmark evidence only; it does not select an ML-DSA parameter
set or define Bitcoin Script, output commitment, consensus, or activation rules.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import statistics
from pathlib import Path

EXPECTED_CANDIDATES = ("ML-DSA-44", "ML-DSA-65", "ML-DSA-87")
EXPECTED_SIZES = {
    "ML-DSA-44": {"public_key_bytes": 1312, "signature_bytes": 2420},
    "ML-DSA-65": {"public_key_bytes": 1952, "signature_bytes": 3309},
    "ML-DSA-87": {"public_key_bytes": 2592, "signature_bytes": 4627},
}


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _median(values: list[int]) -> int:
    return int(statistics.median(values))


def _p95(values: list[int]) -> int:
    _require(len(values) >= 3, "at least three samples are required")
    ordered = sorted(values)
    return ordered[max(1, math.ceil(0.95 * len(ordered))) - 1]


def _validate_positive_int_samples(values: object, repetitions: int, label: str) -> list[int]:
    _require(isinstance(values, list), f"{label} must be a list")
    _require(len(values) == repetitions, f"{label} count must equal repetitions")
    _require(all(type(v) is int and v > 0 for v in values), f"{label} must contain positive integers")
    return values


def validate_report(report: object) -> None:
    _require(isinstance(report, dict), "report must be an object")

    required_exact = {
        "schema_version": 1,
        "research_only": True,
        "endorsed_by_bitcoin_core": False,
        "mainnet_intended": False,
        "network_scope": "none-local-cryptographic-benchmark",
        "candidate_family": "ML-DSA",
        "hybrid_research_semantics": "classical-and-pq",
        "parameter_set_selected": False,
        "deployment_winner_selected": False,
        "bitcoin_core_modified": False,
        "bitcoin_script_semantics_selected": False,
        "output_commitment_semantics_selected": False,
        "consensus_change_selected": False,
        "correctness_oracle_separate": True,
    }
    for key, expected in required_exact.items():
        _require(key in report, f"missing field: {key}")
        _require(report[key] == expected, f"unexpected {key}")

    repetitions = report.get("repetitions")
    _require(type(repetitions) is int and repetitions >= 3, "repetitions must be integer >= 3")

    batch_sizes = report.get("batch_sizes")
    _require(isinstance(batch_sizes, list) and batch_sizes, "batch_sizes must be a non-empty list")
    _require(all(type(v) is int and v > 0 for v in batch_sizes), "batch_sizes must be positive integers")
    _require(batch_sizes == sorted(set(batch_sizes)), "batch_sizes must be unique and strictly increasing")

    candidates = report.get("candidates")
    _require(isinstance(candidates, list), "candidates must be a list")
    _require([row.get("candidate") if isinstance(row, dict) else None for row in candidates] == list(EXPECTED_CANDIDATES),
             "candidate order or set changed")

    for row in candidates:
        name = row["candidate"]
        expected_sizes = EXPECTED_SIZES[name]
        _require(row.get("public_key_bytes") == expected_sizes["public_key_bytes"], f"{name} public-key size mismatch")
        _require(row.get("signature_bytes") == expected_sizes["signature_bytes"], f"{name} signature size mismatch")
        _require(type(row.get("process_max_rss_bytes")) is int and row["process_max_rss_bytes"] > 0,
                 f"{name} process_max_rss_bytes invalid")
        _require(type(row.get("process_max_rss_delta_bytes")) is int and row["process_max_rss_delta_bytes"] >= 0,
                 f"{name} process_max_rss_delta_bytes invalid")

        batches = row.get("batches")
        _require(isinstance(batches, list), f"{name} batches must be a list")
        _require([b.get("batch_size") if isinstance(b, dict) else None for b in batches] == batch_sizes,
                 f"{name} batch set/order mismatch")

        for batch in batches:
            size = batch["batch_size"]
            _require(batch.get("repetitions") == repetitions, f"{name}/{size} repetitions mismatch")
            wall = _validate_positive_int_samples(batch.get("wall_total_samples_ns"), repetitions, f"{name}/{size} wall samples")
            cpu = _validate_positive_int_samples(batch.get("cpu_total_samples_ns"), repetitions, f"{name}/{size} cpu samples")
            _require(batch.get("wall_total_median_ns") == _median(wall), f"{name}/{size} wall median mismatch")
            _require(batch.get("wall_total_p95_ns") == _p95(wall), f"{name}/{size} wall p95 mismatch")
            _require(batch.get("cpu_total_median_ns") == _median(cpu), f"{name}/{size} cpu median mismatch")
            _require(batch.get("cpu_total_p95_ns") == _p95(cpu), f"{name}/{size} cpu p95 mismatch")


def canonical_evidence_digest(report: object) -> str:
    validate_report(report)
    canonical = json.dumps(report, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    digest = canonical_evidence_digest(report)
    print(json.dumps({"ok": True, "sha256": digest}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
