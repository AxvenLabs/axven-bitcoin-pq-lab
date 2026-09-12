#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import platform
import statistics
import time
import tracemalloc

from lab.model import Authorization, Context, Mode, UtxoAuthState


def run(iterations: int, rounds: int) -> dict[str, object]:
    context = Context(
        chain_id="bitcoin-regtest-research",
        txid="11" * 32,
        vout=1,
        epoch=1,
        destination_commitment="22" * 32,
        mode=Mode.HYBRID,
    )
    state = UtxoAuthState(mode=Mode.HYBRID, epoch=1)
    auth = Authorization(
        transcript_hash=context.transcript_hash(), legacy_ok=True, pq_ok=True
    )

    canonical_size = len(context.canonical_bytes())
    timings_ns: list[int] = []

    tracemalloc.start()
    for _ in range(rounds):
        start = time.perf_counter_ns()
        accepted = 0
        for _ in range(iterations):
            accepted += int(state.authorize(context, auth))
        elapsed = time.perf_counter_ns() - start
        if accepted != iterations:
            raise RuntimeError("benchmark authorization unexpectedly failed")
        timings_ns.append(elapsed)
    _, peak_bytes = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    per_op = [elapsed / iterations for elapsed in timings_ns]
    return {
        "benchmark": "authorization-state-model",
        "scope": "non-cryptographic-model-only",
        "cryptographic_scheme": None,
        "iterations_per_round": iterations,
        "rounds": rounds,
        "canonical_context_bytes": canonical_size,
        "authorize_ns_per_op_median": statistics.median(per_op),
        "authorize_ns_per_op_min": min(per_op),
        "peak_tracemalloc_bytes": peak_bytes,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "warning": (
            "This measures Python model/transcript overhead only. It does not "
            "measure Bitcoin script validation or any classical/PQ signature primitive."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Benchmark the scheme-neutral lab model.")
    parser.add_argument("--iterations", type=int, default=10_000)
    parser.add_argument("--rounds", type=int, default=7)
    args = parser.parse_args()
    if args.iterations <= 0 or args.rounds <= 0:
        raise SystemExit("iterations and rounds must be positive")
    print(json.dumps(run(args.iterations, args.rounds), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
