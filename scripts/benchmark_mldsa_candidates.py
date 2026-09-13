#!/usr/bin/env python3
"""Benchmark named ML-DSA verification candidates for Axven Bitcoin PQ Lab.

Research only. Not endorsed by Bitcoin Core and not intended for mainnet use.
This tool compares ML-DSA-44/65/87 as reversible research candidates. It does
not select a deployment parameter set, define Bitcoin Script/output semantics,
change consensus, or benchmark the classical+PQ combined authorization path.
"""

from __future__ import annotations

import argparse
import importlib.metadata
import json
import platform
import resource
import statistics
import subprocess
import sys
import time
import tracemalloc
from pathlib import Path

from scripts.benchmark_process_memory import normalize_maxrss

SOURCE_COMMIT = "b84df503a3cf57ede27f33a81185a63305579a95"
PACKAGE_VERSION = "1.0.1"

CANDIDATES = {
    "ML-DSA-44": {"file": "mldsa_44_verify_test.json", "public_key_bytes": 1312, "signature_bytes": 2420},
    "ML-DSA-65": {"file": "mldsa_65_verify_test.json", "public_key_bytes": 1952, "signature_bytes": 3309},
    "ML-DSA-87": {"file": "mldsa_87_verify_test.json", "public_key_bytes": 2592, "signature_bytes": 4627},
}


def _validate_positive_int(value: int, name: str) -> None:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")


def load_vector(path: Path, candidate: str) -> tuple[bytes, bytes, bytes, bytes]:
    if candidate not in CANDIDATES:
        raise ValueError(f"unsupported candidate: {candidate}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("algorithm") != candidate:
        raise ValueError(f"vector algorithm must be {candidate}")
    groups = data.get("testGroups")
    if not isinstance(groups, list):
        raise ValueError("testGroups must be a list")
    chosen = None
    for group in groups:
        tests = group.get("tests") if isinstance(group, dict) else None
        if not isinstance(tests, list):
            continue
        for test in tests:
            if isinstance(test, dict) and test.get("result") == "valid":
                chosen = (group, test)
                break
        if chosen is not None:
            break
    if chosen is None:
        raise ValueError("no valid verification vector found")
    group, test = chosen
    try:
        public_key = bytes.fromhex(group["publicKey"])
        signature = bytes.fromhex(test["sig"])
        message = bytes.fromhex(test["msg"])
        context = bytes.fromhex(test.get("ctx", ""))
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError("malformed verification vector") from exc
    spec = CANDIDATES[candidate]
    if len(public_key) != spec["public_key_bytes"]:
        raise ValueError("public-key length mismatch")
    if len(signature) != spec["signature_bytes"]:
        raise ValueError("signature length mismatch")
    if len(context) > 255:
        raise ValueError("context exceeds FIPS 204 limit")
    return public_key, signature, message, context


def _sample_rss_bytes() -> int:
    usage = resource.getrusage(resource.RUSAGE_SELF)
    return normalize_maxrss(usage.ru_maxrss, platform.system())


def run_worker(candidate: str, vector_file: Path, iterations: int, source_commit: str) -> dict:
    _validate_positive_int(iterations, "iterations")
    if source_commit != SOURCE_COMMIT:
        raise ValueError("unexpected ML-DSA source commit")
    installed = importlib.metadata.version("mldsa")
    if installed != PACKAGE_VERSION:
        raise ValueError(f"mldsa package must be {PACKAGE_VERSION}, got {installed}")

    from mldsa import VerificationError, VerificationKey

    public_key, signature, message, context = load_vector(vector_file, candidate)
    key = VerificationKey(public_key)

    # Correctness oracle is deliberately separate from timing.
    key.verify(signature, message, context=context)
    corrupted = bytearray(signature)
    corrupted[len(corrupted) // 2] ^= 0x01
    try:
        key.verify(bytes(corrupted), message, context=context)
    except VerificationError:
        negative_oracle_rejected = True
    else:
        raise ValueError("negative correctness oracle unexpectedly accepted")

    wall_ns: list[int] = []
    cpu_ns: list[int] = []
    rss_before = _sample_rss_bytes()
    tracemalloc.start()
    try:
        for _ in range(iterations):
            cpu_start = time.process_time_ns()
            wall_start = time.perf_counter_ns()
            key.verify(signature, message, context=context)
            wall_ns.append(time.perf_counter_ns() - wall_start)
            cpu_ns.append(time.process_time_ns() - cpu_start)
        _, python_peak = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()
    rss_after = _sample_rss_bytes()

    spec = CANDIDATES[candidate]
    return {
        "candidate": candidate,
        "iterations": iterations,
        "public_key_bytes": spec["public_key_bytes"],
        "signature_bytes": spec["signature_bytes"],
        "message_bytes": len(message),
        "context_bytes": len(context),
        "wall_median_ns": int(statistics.median(wall_ns)),
        "wall_min_ns": min(wall_ns),
        "wall_max_ns": max(wall_ns),
        "cpu_median_ns": int(statistics.median(cpu_ns)),
        "cpu_min_ns": min(cpu_ns),
        "cpu_max_ns": max(cpu_ns),
        "python_peak_alloc_bytes": python_peak,
        "process_maxrss_before_bytes": rss_before,
        "process_maxrss_after_bytes": rss_after,
        "process_maxrss_delta_bytes": max(0, rss_after - rss_before),
        "positive_oracle_verified": True,
        "negative_oracle_rejected": negative_oracle_rejected,
    }


def run_parent(testdata_dir: Path, iterations: int, source_commit: str) -> dict:
    _validate_positive_int(iterations, "iterations")
    if source_commit != SOURCE_COMMIT:
        raise ValueError("unexpected ML-DSA source commit")
    results = []
    for candidate, spec in CANDIDATES.items():
        vector_file = testdata_dir / spec["file"]
        if not vector_file.is_file():
            raise ValueError(f"missing pinned vector file: {vector_file}")
        completed = subprocess.run(
            [
                sys.executable,
                str(Path(__file__).resolve()),
                "--worker-candidate",
                candidate,
                "--vector-file",
                str(vector_file),
                "--iterations",
                str(iterations),
                "--source-commit",
                source_commit,
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        results.append(json.loads(completed.stdout))

    return {
        "schema_version": 1,
        "research_only": True,
        "endorsed_by_bitcoin_core": False,
        "mainnet_intended": False,
        "network_scope": "none-local-cryptographic-microbenchmark",
        "pq_candidate_family": "ML-DSA",
        "hybrid_research_semantics": "classical-and-pq",
        "parameter_set_selected": False,
        "deployment_winner_selected": False,
        "bitcoin_core_modified": False,
        "bitcoin_script_semantics_selected": False,
        "consensus_change_selected": False,
        "library": "mldsa",
        "library_version": PACKAGE_VERSION,
        "library_source_commit": SOURCE_COMMIT,
        "results": results,
        "warning": (
            "Named ML-DSA research-candidate verification measurements only; "
            "not a parameter-set selection, not Bitcoin Script/consensus cost, "
            "and not combined classical+PQ authorization performance."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--testdata-dir", type=Path)
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--source-commit", default=SOURCE_COMMIT)
    parser.add_argument("--worker-candidate", choices=tuple(CANDIDATES))
    parser.add_argument("--vector-file", type=Path)
    args = parser.parse_args()

    if args.worker_candidate:
        if args.vector_file is None:
            parser.error("--vector-file is required in worker mode")
        report = run_worker(
            args.worker_candidate, args.vector_file, args.iterations, args.source_commit
        )
    else:
        if args.testdata_dir is None:
            parser.error("--testdata-dir is required")
        report = run_parent(args.testdata_dir, args.iterations, args.source_commit)
    print(json.dumps(report, sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
