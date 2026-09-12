#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import argparse

from lab.vectors import canonical_vector_json


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export deterministic authorization-state research vectors."
    )
    parser.add_argument(
        "--output",
        default="artifacts/test-vectors-v1.json",
        help="Output path (default: artifacts/test-vectors-v1.json)",
    )
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(canonical_vector_json(), encoding="utf-8")
    print(output)


if __name__ == "__main__":
    main()
