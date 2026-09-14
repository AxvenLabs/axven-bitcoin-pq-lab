#!/usr/bin/env python3
"""Fail-closed validator for candidate-neutral ML-DSA benchmark summaries.

Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.
This validates presentation-layer evidence only. It does not select an ML-DSA
parameter set or define Bitcoin Script, consensus, activation, recovery, trust,
key-custody, or production security semantics.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

EXPECTED_CANDIDATES = ("ML-DSA-44", "ML-DSA-65", "ML-DSA-87")
EXPECTED_SIZES = {
    "ML-DSA-44": (1312, 2420),
    "ML-DSA-65": (1952, 3309),
    "ML-DSA-87": (2592, 4627),
}
EXPECTED_BATCHES = (1, 10, 100)
FORBIDDEN_KEYS = {
    "winner",
    "recommended",
    "recommendation",
    "rank",
    "score",
    "selected",
    "preferred",
}


def _reject_selection_fields(value: object) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key.lower() in FORBIDDEN_KEYS:
                raise ValueError(f"candidate-selection field forbidden: {key}")
            _reject_selection_fields(item)
    elif isinstance(value, list):
        for item in value:
            _reject_selection_fields(item)


def validate_summary(summary: object) -> None:
    if not isinstance(summary, dict):
        raise ValueError("summary must be an object")
    _reject_selection_fields(summary)

    expected_flags = {
        "schema_version": 1,
        "research_only": True,
        "endorsed_by_bitcoin_core": False,
        "mainnet_intended": False,
        "candidate_family": "ML-DSA",
        "hybrid_research_semantics": "classical-and-pq",
        "parameter_set_selected": False,
        "deployment_winner_selected": False,
        "ranking_performed": False,
    }
    for key, expected in expected_flags.items():
        if summary.get(key) != expected:
            raise ValueError(f"invalid {key}")

    candidates = summary.get("candidates")
    if not isinstance(candidates, list):
        raise ValueError("candidates must be a list")
    names = [row.get("candidate") if isinstance(row, dict) else None for row in candidates]
    if tuple(names) != EXPECTED_CANDIDATES:
        raise ValueError("candidate order mismatch")

    for row in candidates:
        if not isinstance(row, dict):
            raise ValueError("candidate row must be an object")
        name = row["candidate"]
        expected_pk, expected_sig = EXPECTED_SIZES[name]
        if row.get("public_key_bytes") != expected_pk:
            raise ValueError(f"public-key size mismatch for {name}")
        if row.get("signature_bytes") != expected_sig:
            raise ValueError(f"signature size mismatch for {name}")
        for rss_key in ("process_max_rss_bytes", "process_max_rss_delta_bytes"):
            rss = row.get(rss_key)
            if not isinstance(rss, int) or rss < 0:
                raise ValueError(f"invalid {rss_key} for {name}")

        batches = row.get("batches")
        if not isinstance(batches, list):
            raise ValueError(f"batches missing for {name}")
        batch_sizes = [b.get("batch_size") if isinstance(b, dict) else None for b in batches]
        if tuple(batch_sizes) != EXPECTED_BATCHES:
            raise ValueError(f"batch order mismatch for {name}")
        for batch in batches:
            if not isinstance(batch, dict):
                raise ValueError("batch must be an object")
            size = batch["batch_size"]
            for key in (
                "wall_total_median_ns",
                "wall_median_ns_per_verification",
                "cpu_total_median_ns",
                "cpu_median_ns_per_verification",
            ):
                value = batch.get(key)
                if not isinstance(value, int) or value < 0:
                    raise ValueError(f"invalid {key} for {name}/{size}")
            if batch["wall_median_ns_per_verification"] != batch["wall_total_median_ns"] // size:
                raise ValueError(f"wall derived timing mismatch for {name}/{size}")
            if batch["cpu_median_ns_per_verification"] != batch["cpu_total_median_ns"] // size:
                raise ValueError(f"cpu derived timing mismatch for {name}/{size}")


def canonical_digest(summary: object) -> str:
    validate_summary(summary)
    encoded = json.dumps(summary, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("summary", type=Path)
    args = parser.parse_args()
    summary = json.loads(args.summary.read_text(encoding="utf-8"))
    digest = canonical_digest(summary)
    print(json.dumps({"ok": True, "sha256": digest}, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
