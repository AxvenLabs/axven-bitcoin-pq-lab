#!/usr/bin/env python3
"""Scheme-neutral verifier benchmark harness for Axven Bitcoin PQ Lab.

Research only. Not endorsed by Bitcoin Core and not intended for mainnet use.
This module measures a generic verifier-call path only. It does not select a
post-quantum scheme, define Bitcoin authorization semantics, or modify Bitcoin
Core, consensus, activation, legacy UTXO treatment, recovery, trust roots, or
key custody.
"""

from __future__ import annotations

import argparse
import json
import statistics
import time
import tracemalloc
from dataclasses import dataclass
from typing import Callable

Verifier = Callable[[bytes, bytes, bytes], bool]


@dataclass(frozen=True)
class VerificationSample:
    message: bytes
    signature: bytes
    public_key: bytes


def benchmark_verifier(
    verifier: Verifier,
    sample: VerificationSample,
    iterations: int = 100,
) -> dict:
    if isinstance(iterations, bool) or not isinstance(iterations, int) or iterations <= 0:
        raise ValueError("iterations must be a positive integer")
    if not callable(verifier):
        raise ValueError("verifier must be callable")

    timings_ns: list[int] = []
    tracemalloc.start()
    try:
        for _ in range(iterations):
            start = time.perf_counter_ns()
            accepted = verifier(sample.message, sample.signature, sample.public_key)
            elapsed = time.perf_counter_ns() - start
            if accepted is not True:
                raise ValueError("calibration verifier must return literal True")
            timings_ns.append(elapsed)
        _, peak_bytes = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()

    return {
        "schema_version": 1,
        "research_only": True,
        "endorsed_by_bitcoin_core": False,
        "mainnet_intended": False,
        "network_scope": "none-local-microbenchmark",
        "scheme_selected": False,
        "hybrid_semantics_selected": False,
        "measurement_scope": "generic-verifier-call-harness",
        "iterations": iterations,
        "message_bytes": len(sample.message),
        "signature_bytes": len(sample.signature),
        "public_key_bytes": len(sample.public_key),
        "median_ns": int(statistics.median(timings_ns)),
        "min_ns": min(timings_ns),
        "max_ns": max(timings_ns),
        "python_peak_alloc_bytes": peak_bytes,
        "warning": (
            "Harness calibration only; these values are not PQ signature "
            "verification costs and must not be presented as such."
        ),
    }


def calibration_verifier(message: bytes, signature: bytes, public_key: bytes) -> bool:
    """Deterministic non-cryptographic callable used only to exercise the harness."""
    return bool(message) and bool(signature) and bool(public_key)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=100)
    parser.add_argument("--message-bytes", type=int, default=32)
    parser.add_argument("--signature-bytes", type=int, default=64)
    parser.add_argument("--public-key-bytes", type=int, default=32)
    args = parser.parse_args()

    for name, value in (
        ("message-bytes", args.message_bytes),
        ("signature-bytes", args.signature_bytes),
        ("public-key-bytes", args.public_key_bytes),
    ):
        if value <= 0:
            raise ValueError(f"{name} must be positive")

    sample = VerificationSample(
        message=b"m" * args.message_bytes,
        signature=b"s" * args.signature_bytes,
        public_key=b"k" * args.public_key_bytes,
    )
    print(
        json.dumps(
            benchmark_verifier(calibration_verifier, sample, args.iterations),
            sort_keys=True,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
