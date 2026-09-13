#!/usr/bin/env python3
"""Research-only ML-DSA candidate benchmark for Axven Bitcoin PQ Lab.

This measures ML-DSA-44/65/87 as named reversible research candidates. It does
not select a deployment winner, define Bitcoin Script/consensus semantics, or
modify Bitcoin Core. Not endorsed by Bitcoin Core; not intended for mainnet.
"""

from __future__ import annotations

import argparse
import json
import platform
import resource
import statistics
import time

import cryptography
from cryptography.hazmat.backends.openssl.backend import backend
from cryptography.hazmat.primitives.asymmetric import mldsa

CANDIDATES = {
    "ML-DSA-44": mldsa.MLDSA44PrivateKey,
    "ML-DSA-65": mldsa.MLDSA65PrivateKey,
    "ML-DSA-87": mldsa.MLDSA87PrivateKey,
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


def benchmark_candidate(name: str, iterations: int, message: bytes) -> dict:
    if name not in CANDIDATES:
        raise ValueError(f"unsupported candidate: {name}")
    if isinstance(iterations, bool) or not isinstance(iterations, int) or iterations < 3:
        raise ValueError("iterations must be an integer >= 3")
    if not isinstance(message, bytes) or not message:
        raise ValueError("message must be non-empty bytes")

    cls = CANDIDATES[name]
    # Deterministic per-candidate seed for reproducible key identity. This is lab-only.
    seed_tag = name.encode("ascii")
    seed = (seed_tag + b"|axven-bitcoin-pq-lab|bench-008").ljust(32, b"\0")[:32]
    private_key = cls.from_seed_bytes(seed)
    public_key = private_key.public_key()
    public_raw = public_key.public_bytes_raw()
    signature = private_key.sign(message)

    # Correctness oracle is deliberately separate from timing collection.
    public_key.verify(signature, message)
    altered = message[:-1] + bytes([message[-1] ^ 1])
    invalid_rejected = False
    try:
        public_key.verify(signature, altered)
    except Exception:
        invalid_rejected = True
    if not invalid_rejected:
        raise RuntimeError("correctness oracle failed: altered message was accepted")

    timings: list[int] = []
    rss_before = _rss_bytes()
    for _ in range(iterations):
        start = time.perf_counter_ns()
        public_key.verify(signature, message)
        timings.append(time.perf_counter_ns() - start)
    rss_after = _rss_bytes()

    return {
        "candidate": name,
        "public_key_bytes": len(public_raw),
        "signature_bytes": len(signature),
        "iterations": iterations,
        "verify_median_ns": _median(timings),
        "verify_min_ns": min(timings),
        "verify_max_ns": max(timings),
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
        "consensus_change_selected": False,
        "cryptography_version": cryptography.__version__,
        "openssl_version": backend.openssl_version_text(),
        "python_version": platform.python_version(),
        "platform": platform.platform(),
        "message_bytes": len(message),
        "candidates": rows,
        "warning": "Candidate measurements are research evidence only and do not select an ML-DSA parameter set for Bitcoin or production deployment.",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=25)
    args = parser.parse_args()
    print(json.dumps(build_report(args.iterations), sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
