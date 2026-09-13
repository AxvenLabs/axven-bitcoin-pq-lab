#!/usr/bin/env python3
"""Compare vanilla and experiment-off regtest observations.

Transaction ids are intentionally excluded because each isolated wallet run
creates fresh keys. All behavioral invariants must otherwise match exactly.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

FIELDS = (
    "blocks",
    "chain",
    "confirmations",
    "research_only",
    "transaction_created_and_mined",
    "upstream_version",
)


def load(path: str) -> dict:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("vanilla")
    parser.add_argument("experiment_off")
    args = parser.parse_args()

    vanilla = load(args.vanilla)
    experiment_off = load(args.experiment_off)

    left = {key: vanilla.get(key) for key in FIELDS}
    right = {key: experiment_off.get(key) for key in FIELDS}
    if left != right:
        raise SystemExit(
            "experiment-off regtest behavior diverged from vanilla baseline:\n"
            + json.dumps({"vanilla": left, "experiment_off": right}, indent=2, sort_keys=True)
        )

    print(json.dumps({"equivalent": True, "fields": list(FIELDS)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
