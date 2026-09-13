#!/usr/bin/env python3
"""Research-only regtest lab entry point.

The only supported mode is ``off``. It delegates to the pinned vanilla Bitcoin
Core baseline without patching Bitcoin Core or defining PQ/consensus semantics.
All other modes fail closed until a separately reviewed experiment exists.
"""

from __future__ import annotations

import argparse
import subprocess
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", required=True, choices=("off", "on"))
    parser.add_argument("--bin-dir", required=True)
    args = parser.parse_args()

    if args.mode != "off":
        parser.error(
            "experimental mode is intentionally unavailable: no PQ scheme, "
            "hybrid authorization semantics, activation policy, or consensus "
            "change has been selected"
        )

    script = Path(__file__).with_name("run_vanilla_regtest_baseline.sh")
    completed = subprocess.run(
        ["bash", str(script), args.bin_dir],
        check=False,
    )
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
