#!/usr/bin/env python3
"""Process-memory calibration for the Axven Bitcoin PQ Lab.

Research only. Not endorsed by Bitcoin Core and not intended for mainnet use.
This tool does not select a post-quantum scheme or define Bitcoin consensus,
authorization, migration, recovery, trust-root, or key-custody semantics.
"""

from __future__ import annotations

import argparse
import json
import os
import platform
import resource
from typing import Callable


def normalize_maxrss(raw_value: int | float, system: str) -> int:
    """Normalize resource.getrusage().ru_maxrss to bytes.

    Linux reports KiB; macOS reports bytes. Unknown systems fail closed rather
    than silently publishing incomparable evidence.
    """
    if isinstance(raw_value, bool) or not isinstance(raw_value, (int, float)):
        raise ValueError("ru_maxrss must be numeric")
    if raw_value < 0:
        raise ValueError("ru_maxrss must be non-negative")
    if system == "Linux":
        return int(raw_value * 1024)
    if system == "Darwin":
        return int(raw_value)
    raise ValueError(f"unsupported ru_maxrss platform: {system}")


def sample_process_maxrss_bytes(
    getrusage: Callable[[int], object] = resource.getrusage,
    system: str | None = None,
) -> int:
    usage = getrusage(resource.RUSAGE_SELF)
    raw = getattr(usage, "ru_maxrss", None)
    if raw is None:
        raise ValueError("ru_maxrss unavailable")
    return normalize_maxrss(raw, system or platform.system())


def touch_memory(mebibytes: int) -> int:
    if isinstance(mebibytes, bool) or not isinstance(mebibytes, int) or mebibytes <= 0:
        raise ValueError("mebibytes must be a positive integer")
    buf = bytearray(mebibytes * 1024 * 1024)
    stride = 4096
    checksum = 0
    for offset in range(0, len(buf), stride):
        buf[offset] = (offset // stride) & 0xFF
        checksum ^= buf[offset]
    return checksum


def build_report(mebibytes: int) -> dict:
    before = sample_process_maxrss_bytes()
    checksum = touch_memory(mebibytes)
    after = sample_process_maxrss_bytes()
    return {
        "schema_version": 1,
        "research_only": True,
        "endorsed_by_bitcoin_core": False,
        "mainnet_intended": False,
        "network_scope": "none-local-microbenchmark",
        "scheme_selected": False,
        "hybrid_semantics_selected": False,
        "pid": os.getpid(),
        "platform_system": platform.system(),
        "allocation_mebibytes": mebibytes,
        "maxrss_before_bytes": before,
        "maxrss_after_bytes": after,
        "maxrss_delta_bytes": max(0, after - before),
        "touch_checksum": checksum,
        "warning": "Process max-RSS calibration only; not PQ verification memory cost.",
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mebibytes", type=int, default=8)
    args = parser.parse_args()
    print(json.dumps(build_report(args.mebibytes), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
