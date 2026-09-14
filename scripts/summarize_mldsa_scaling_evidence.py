#!/usr/bin/env python3
"""Deterministic candidate-neutral summary for ML-DSA scaling evidence.

Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.
This tool summarizes already-validated benchmark evidence. It does not rank or
select an ML-DSA parameter set and does not define Bitcoin deployment semantics.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from scripts.validate_mldsa_scaling_evidence import validate_report

FORBIDDEN_KEYS = {
    "winner",
    "recommended",
    "recommendation",
    "rank",
    "score",
    "selected",
    "preferred",
}


def summarize(report: object) -> dict:
    validate_report(report)
    assert isinstance(report, dict)

    rows = []
    for candidate in report["candidates"]:
        batches = []
        for batch in candidate["batches"]:
            size = batch["batch_size"]
            batches.append(
                {
                    "batch_size": size,
                    "wall_total_median_ns": batch["wall_total_median_ns"],
                    "wall_median_ns_per_verification": batch["wall_total_median_ns"] // size,
                    "cpu_total_median_ns": batch["cpu_total_median_ns"],
                    "cpu_median_ns_per_verification": batch["cpu_total_median_ns"] // size,
                }
            )
        rows.append(
            {
                "candidate": candidate["candidate"],
                "public_key_bytes": candidate["public_key_bytes"],
                "signature_bytes": candidate["signature_bytes"],
                "process_max_rss_bytes": candidate["process_max_rss_bytes"],
                "process_max_rss_delta_bytes": candidate["process_max_rss_delta_bytes"],
                "batches": batches,
            }
        )

    summary = {
        "schema_version": 1,
        "research_only": True,
        "endorsed_by_bitcoin_core": False,
        "mainnet_intended": False,
        "candidate_family": "ML-DSA",
        "hybrid_research_semantics": "classical-and-pq",
        "parameter_set_selected": False,
        "deployment_winner_selected": False,
        "ranking_performed": False,
        "candidates": rows,
    }
    _assert_candidate_neutral(summary)
    return summary


def _assert_candidate_neutral(value: object) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key.lower() in FORBIDDEN_KEYS:
                raise ValueError(f"candidate-selection field forbidden: {key}")
            _assert_candidate_neutral(item)
    elif isinstance(value, list):
        for item in value:
            _assert_candidate_neutral(item)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("report", type=Path)
    args = parser.parse_args()
    report = json.loads(args.report.read_text(encoding="utf-8"))
    summary = summarize(report)
    print(json.dumps(summary, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
