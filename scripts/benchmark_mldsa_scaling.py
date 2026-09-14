#!/usr/bin/env python3
"""Research-only ML-DSA verification batch-scaling benchmark.

Not endorsed by Bitcoin Core. Not intended for mainnet deployment. This lab-only
benchmark compares named reversible ML-DSA-44/65/87 research candidates without
selecting a parameter set, defining Bitcoin Script/output semantics, or changing
Bitcoin Core consensus behavior.
"""

from __future__ import annotations

import argparse
import json
import math
import statistics
import time

from scripts.benchmark_mldsa_candidates import CANDIDATES, EXPECTED_SIZES, _rss_bytes

DEFAULT_BATCH_SIZES = (1, 10, 100)


def _median(values: list[int]) -> int:
    return int(statistics.median(values))


def _p95(values: list[int]) -> int:
    if len(values) < 3:
        raise ValueError("at least three samples are required")
    ordered = sorted(values)
    return ordered[max(1, math.ceil(0.95 * len(ordered))) - 1]


def _validate_batch_sizes(batch_sizes: tuple[int, ...]) -> None:
    if not batch_sizes:
        raise ValueError("at least one batch size is required")
    if tuple(sorted(set(batch_sizes))) != batch_sizes:
        raise ValueError("batch sizes must be unique and strictly increasing")
    if any(isinstance(v, bool) or not isinstance(v, int) or v < 1 for v in batch_sizes):
        raise ValueError("batch sizes must be positive integers")


def benchmark_candidate_scaling(
    name: str,
    repetitions: int = 5,
    batch_sizes: tuple[int, ...] = DEFAULT_BATCH_SIZES,
    message: bytes = b"axven-bitcoin-pq-lab-bench-016",
) -> dict:
    if name not in CANDIDATES:
        raise ValueError(f"unsupported candidate: {name}")
    if isinstance(repetitions, bool) or not isinstance(repetitions, int) or repetitions < 3:
        raise ValueError("repetitions must be an integer >= 3")
    if not isinstance(message, bytes) or not message:
        raise ValueError("message must be non-empty bytes")
    _validate_batch_sizes(batch_sizes)

    cls = CANDIDATES[name]
    seed = (name.encode("ascii") + b"|axven-bitcoin-pq-lab|bench-016").ljust(32, b"\0")[:32]
    private_key = cls.from_seed_bytes(seed)
    public_key = private_key.public_key()
    public_raw = public_key.public_bytes_raw()
    signature = private_key.sign(message)

    expected = EXPECTED_SIZES[name]
    if len(public_raw) != expected["public_key_bytes"] or len(signature) != expected["signature_bytes"]:
        raise RuntimeError("ML-DSA size contract drift")

    # Untimed preflight only. Negative/cross-candidate correctness remains in the
    # dedicated correctness-oracle checkpoint and is deliberately not benchmarked.
    public_key.verify(signature, message)

    rss_before = _rss_bytes()
    batches = []
    for batch_size in batch_sizes:
        wall_samples: list[int] = []
        cpu_samples: list[int] = []
        for _ in range(repetitions):
            cpu_start = time.process_time_ns()
            wall_start = time.perf_counter_ns()
            for _ in range(batch_size):
                public_key.verify(signature, message)
            wall_samples.append(time.perf_counter_ns() - wall_start)
            cpu_samples.append(time.process_time_ns() - cpu_start)
        batches.append(
            {
                "batch_size": batch_size,
                "repetitions": repetitions,
                "wall_total_samples_ns": wall_samples,
                "wall_total_median_ns": _median(wall_samples),
                "wall_total_p95_ns": _p95(wall_samples),
                "cpu_total_samples_ns": cpu_samples,
                "cpu_total_median_ns": _median(cpu_samples),
                "cpu_total_p95_ns": _p95(cpu_samples),
            }
        )
    rss_after = _rss_bytes()

    return {
        "candidate": name,
        "public_key_bytes": len(public_raw),
        "signature_bytes": len(signature),
        "process_max_rss_bytes": rss_after,
        "process_max_rss_delta_bytes": max(0, rss_after - rss_before),
        "batches": batches,
    }


def build_report(repetitions: int = 5, batch_sizes: tuple[int, ...] = DEFAULT_BATCH_SIZES) -> dict:
    _validate_batch_sizes(batch_sizes)
    return {
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
        "batch_sizes": list(batch_sizes),
        "repetitions": repetitions,
        "candidates": [
            benchmark_candidate_scaling(name, repetitions, batch_sizes) for name in CANDIDATES
        ],
        "warning": (
            "Research evidence only; batch scaling does not select an ML-DSA parameter set "
            "or define Bitcoin authorization/consensus semantics."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--batch-sizes", default="1,10,100")
    args = parser.parse_args()
    batch_sizes = tuple(int(v) for v in args.batch_sizes.split(",") if v)
    print(json.dumps(build_report(args.repetitions, batch_sizes), sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
