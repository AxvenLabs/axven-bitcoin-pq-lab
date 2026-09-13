#!/usr/bin/env python3
"""Research-only ML-DSA candidate benchmark for Axven Bitcoin PQ Lab.

This measures ML-DSA-44/65/87 as named reversible research candidates. It does
not select a deployment winner, define Bitcoin Script/consensus semantics, or
modify Bitcoin Core. Not endorsed by Bitcoin Core; not intended for mainnet.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import resource
import statistics
import time
import tracemalloc

import cryptography
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends.openssl.backend import backend
from cryptography.hazmat.primitives.asymmetric import mldsa

CANDIDATES = {
    "ML-DSA-44": mldsa.MLDSA44PrivateKey,
    "ML-DSA-65": mldsa.MLDSA65PrivateKey,
    "ML-DSA-87": mldsa.MLDSA87PrivateKey,
}

EXPECTED_SIZES = {
    "ML-DSA-44": {"public_key_bytes": 1312, "signature_bytes": 2420},
    "ML-DSA-65": {"public_key_bytes": 1952, "signature_bytes": 3309},
    "ML-DSA-87": {"public_key_bytes": 2592, "signature_bytes": 4627},
}


def _rss_bytes() -> int:
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if platform.system() == "Darwin":
        return int(value)
    if platform.system() == "Linux":
        return int(value) * 1024
    raise RuntimeError("unsupported platform for ru_maxrss normalization")


def _median(values: list[int]) -> int:
    return int(statistics.median(values))


def _p95(values: list[int]) -> int:
    if len(values) < 3:
        raise ValueError("at least three samples are required")
    ordered = sorted(values)
    rank = max(1, math.ceil(0.95 * len(ordered)))
    return ordered[rank - 1]


def benchmark_candidate(name: str, iterations: int, message: bytes) -> dict:
    if name not in CANDIDATES:
        raise ValueError(f"unsupported candidate: {name}")
    if isinstance(iterations, bool) or not isinstance(iterations, int) or iterations < 3:
        raise ValueError("iterations must be an integer >= 3")
    if not isinstance(message, bytes) or not message:
        raise ValueError("message must be non-empty bytes")

    cls = CANDIDATES[name]
    # Deterministic public lab seed for reproducible key identity only.
    seed_tag = name.encode("ascii")
    seed = (seed_tag + b"|axven-bitcoin-pq-lab|bench-008").ljust(32, b"\0")[:32]
    private_key = cls.from_seed_bytes(seed)
    public_key = private_key.public_key()
    public_raw = public_key.public_bytes_raw()
    signature = private_key.sign(message)

    expected = EXPECTED_SIZES[name]
    if len(public_raw) != expected["public_key_bytes"]:
        raise RuntimeError("unexpected ML-DSA public-key size")
    if len(signature) != expected["signature_bytes"]:
        raise RuntimeError("unexpected ML-DSA signature size")

    # Correctness oracle is deliberately separate from timing collection.
    public_key.verify(signature, message)
    altered = message[:-1] + bytes([message[-1] ^ 1])
    try:
        public_key.verify(signature, altered)
    except InvalidSignature:
        invalid_rejected = True
    else:
        raise RuntimeError("correctness oracle failed: altered message was accepted")

    wall_timings: list[int] = []
    cpu_timings: list[int] = []
    rss_before = _rss_bytes()
    tracemalloc.start()
    try:
        for _ in range(iterations):
            cpu_start = time.process_time_ns()
            wall_start = time.perf_counter_ns()
            public_key.verify(signature, message)
            wall_timings.append(time.perf_counter_ns() - wall_start)
            cpu_timings.append(time.process_time_ns() - cpu_start)
        _, python_peak_alloc = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    rss_after = _rss_bytes()

    return {
        "candidate": name,
        "public_key_bytes": len(public_raw),
        "signature_bytes": len(signature),
        "iterations": iterations,
        "verify_wall_samples_ns": wall_timings,
        "verify_wall_median_ns": _median(wall_timings),
        "verify_wall_p95_ns": _p95(wall_timings),
        "verify_wall_min_ns": min(wall_timings),
        "verify_wall_max_ns": max(wall_timings),
        "verify_cpu_samples_ns": cpu_timings,
        "verify_cpu_median_ns": _median(cpu_timings),
        "verify_cpu_p95_ns": _p95(cpu_timings),
        "verify_cpu_min_ns": min(cpu_timings),
        "verify_cpu_max_ns": max(cpu_timings),
        "python_peak_alloc_bytes": python_peak_alloc,
        "process_max_rss_bytes": rss_after,
        "process_max_rss_delta_bytes": max(0, rss_after - rss_before),
        "correctness_oracle": {
            "valid_signature_accepted": True,
            "altered_message_rejected": invalid_rejected,
        },
    }


def build_report(iterations: int = 25, message: bytes = b"axven-bitcoin-pq-lab-bench-008") -> dict:
    rows = [benchmark_candidate(name, iterations, message) for name in CANDIDATES]
    return {
        "schema_version": 3,
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
        "consensus_change_selected": False,
        "raw_sample_evidence": True,
        "percentile_method": "nearest-rank",
        "cryptography_version": cryptography.__version__,
        "openssl_version": backend.openssl_version_text(),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "message_bytes": len(message),
        "candidates": rows,
        "warning": (
            "Candidate measurements are research evidence only and do not select "
            "an ML-DSA parameter set for Bitcoin or production deployment."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=25)
    args = parser.parse_args()
    print(json.dumps(build_report(args.iterations), sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
