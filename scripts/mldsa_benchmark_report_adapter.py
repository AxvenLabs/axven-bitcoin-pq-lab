#!/usr/bin/env python3
"""Adapt ML-DSA candidate measurements to the generic benchmark report contract.

Research only. Not endorsed by Bitcoin Core and not intended for mainnet.
This adapter does not select an ML-DSA parameter set, define Bitcoin Script or
consensus semantics, choose activation/fork policy, or alter Bitcoin Core.
"""

from __future__ import annotations

import argparse
import json

from scripts.benchmark_environment import collect_environment
from scripts.benchmark_report import validate_report

EXPECTED_CANDIDATES = ("ML-DSA-44", "ML-DSA-65", "ML-DSA-87")


def _nonempty_string(value: object, name: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value.strip()


def adapt_report(
    raw: dict,
    *,
    source_identity: str,
    timestamp_utc: str,
    environment: dict,
) -> list[dict]:
    """Return validated generic wall/CPU reports for every named candidate."""
    if not isinstance(raw, dict):
        raise ValueError("raw report must be an object")
    if raw.get("research_only") is not True:
        raise ValueError("raw report must remain research-only")
    if raw.get("candidate_family") != "ML-DSA":
        raise ValueError("raw report candidate_family must be ML-DSA")
    if raw.get("hybrid_research_semantics") != "classical-and-pq":
        raise ValueError("raw report hybrid semantics must be classical-and-pq")
    if raw.get("parameter_set_selected") is not False:
        raise ValueError("parameter_set_selected must remain false")
    if raw.get("deployment_winner_selected") is not False:
        raise ValueError("deployment_winner_selected must remain false")
    if raw.get("bitcoin_core_modified") is not False:
        raise ValueError("bitcoin_core_modified must remain false")
    if raw.get("bitcoin_script_semantics_selected") is not False:
        raise ValueError("bitcoin_script_semantics_selected must remain false")
    if raw.get("consensus_change_selected") is not False:
        raise ValueError("consensus_change_selected must remain false")

    source_identity = _nonempty_string(source_identity, "source_identity")
    timestamp_utc = _nonempty_string(timestamp_utc, "timestamp_utc")
    if not isinstance(environment, dict):
        raise ValueError("environment must be an object")

    rows = raw.get("candidates")
    if not isinstance(rows, list) or [row.get("candidate") for row in rows] != list(EXPECTED_CANDIDATES):
        raise ValueError("candidate set/order must be exactly ML-DSA-44/65/87")

    reports: list[dict] = []
    for row in rows:
        name = row["candidate"]
        iterations = row.get("iterations")
        if not isinstance(iterations, int) or isinstance(iterations, bool) or iterations < 3:
            raise ValueError("candidate iterations must be an integer >= 3")

        for metric_name, sample_key in (
            ("verify-wall", "verify_wall_samples_ns"),
            ("verify-cpu", "verify_cpu_samples_ns"),
        ):
            samples = row.get(sample_key)
            report = {
                "schema_version": 1,
                "research_only": True,
                "benchmark_name": f"{name}-{metric_name}",
                "category": "post-quantum-verification-research-candidate",
                "source_identity": source_identity,
                "timestamp_utc": timestamp_utc,
                "unit": "ns",
                "environment": dict(environment),
                "warmups": 0,
                "repetitions": iterations,
                "samples": samples,
                "median": row.get(f"{metric_name.replace('-', '_')}_median_ns"),
                "p95": row.get(f"{metric_name.replace('-', '_')}_p95_ns"),
            }
            validate_report(report)
            reports.append(report)

    return reports


def main() -> int:
    # Import the optional ML-DSA backend only when the executable benchmark path
    # is used. The pure adapter contract stays testable without that dependency.
    from scripts.benchmark_mldsa_candidates import build_report

    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=25)
    parser.add_argument("--source-identity", required=True)
    parser.add_argument("--timestamp-utc", required=True)
    args = parser.parse_args()

    raw = build_report(args.iterations)
    reports = adapt_report(
        raw,
        source_identity=args.source_identity,
        timestamp_utc=args.timestamp_utc,
        environment=collect_environment(),
    )
    print(json.dumps(reports, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
