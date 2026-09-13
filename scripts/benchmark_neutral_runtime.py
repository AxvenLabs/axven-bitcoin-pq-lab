#!/usr/bin/env python3
"""Scheme-neutral runtime and memory benchmark for reversible lab workloads.

Research only. Not endorsed by Bitcoin Core and not intended for mainnet use.
This benchmark does not select a post-quantum scheme or define Bitcoin
consensus/security semantics. It measures only a deterministic byte-processing
workload so the lab can exercise reproducible CPU/RAM reporting before any
cryptographic candidate is chosen.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import time
import tracemalloc


def deterministic_payload(size: int) -> bytes:
    if not isinstance(size, int) or isinstance(size, bool) or size <= 0:
        raise ValueError("size must be a positive integer")
    seed = b"axven-bitcoin-pq-lab|neutral-runtime-v1|"
    out = bytearray()
    counter = 0
    while len(out) < size:
        out.extend(hashlib.sha256(seed + counter.to_bytes(8, "big")).digest())
        counter += 1
    return bytes(out[:size])


def neutral_work(payload: bytes, iterations: int) -> bytes:
    if not isinstance(payload, (bytes, bytearray)) or not payload:
        raise ValueError("payload must be non-empty bytes")
    if not isinstance(iterations, int) or isinstance(iterations, bool) or iterations <= 0:
        raise ValueError("iterations must be a positive integer")
    state = bytes(payload)
    for _ in range(iterations):
        state = hashlib.sha256(state).digest()
    return state


def run_case(payload_bytes: int, iterations: int, rounds: int) -> dict:
    if not isinstance(rounds, int) or isinstance(rounds, bool) or rounds <= 0:
        raise ValueError("rounds must be a positive integer")
    payload = deterministic_payload(payload_bytes)
    durations_ns: list[int] = []
    peak_bytes: list[int] = []
    digest = None
    for _ in range(rounds):
        tracemalloc.start()
        start = time.perf_counter_ns()
        digest = neutral_work(payload, iterations)
        elapsed = time.perf_counter_ns() - start
        _, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        durations_ns.append(elapsed)
        peak_bytes.append(peak)
    return {
        "payload_bytes": payload_bytes,
        "iterations": iterations,
        "rounds": rounds,
        "median_duration_ns": int(statistics.median(durations_ns)),
        "min_duration_ns": min(durations_ns),
        "max_duration_ns": max(durations_ns),
        "median_peak_python_bytes": int(statistics.median(peak_bytes)),
        "max_peak_python_bytes": max(peak_bytes),
        "result_sha256_hex": digest.hex() if digest is not None else None,
    }


def build_report(payload_sizes: list[int], iterations: int, rounds: int) -> dict:
    if not isinstance(payload_sizes, list) or not payload_sizes:
        raise ValueError("at least one payload size is required")
    if len(set(payload_sizes)) != len(payload_sizes):
        raise ValueError("payload sizes must be unique")
    return {
        "schema_version": 1,
        "research_only": True,
        "endorsed_by_bitcoin_core": False,
        "mainnet_intended": False,
        "network_scope": "none-local-microbenchmark",
        "scheme_selected": False,
        "hybrid_semantics_selected": False,
        "measurement": "deterministic scheme-neutral CPU and Python-memory workload",
        "warning": "This is harness calibration, not cryptographic verification performance.",
        "cases": [run_case(size, iterations, rounds) for size in payload_sizes],
    }


def parse_sizes(raw: str) -> list[int]:
    try:
        values = [int(part.strip()) for part in raw.split(",") if part.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("sizes must be comma-separated integers") from exc
    if not values or any(value <= 0 for value in values):
        raise argparse.ArgumentTypeError("sizes must contain positive integers")
    return values


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sizes", type=parse_sizes, default=[64, 256, 1024, 4096])
    parser.add_argument("--iterations", type=int, default=500)
    parser.add_argument("--rounds", type=int, default=5)
    args = parser.parse_args()
    print(json.dumps(build_report(args.sizes, args.iterations, args.rounds), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
