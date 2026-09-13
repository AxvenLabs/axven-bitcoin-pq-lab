#!/usr/bin/env python3
"""Compare vanilla and experiment-off regtest observations.

Transaction ids are intentionally excluded from equality because each isolated
wallet run creates fresh keys. Both observations must still satisfy the same
strict baseline schema before behavioral fields are compared.
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
REQUIRED_FIELDS = (*FIELDS, "txid")


def load(path: str) -> dict:
    value = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise SystemExit(f"expected JSON object: {path}")
    return value


def validate(label: str, value: dict) -> None:
    missing = [key for key in REQUIRED_FIELDS if key not in value]
    if missing:
        raise SystemExit(f"{label} baseline missing required fields: {', '.join(missing)}")

    checks = (
        (type(value["blocks"]) is int and value["blocks"] >= 102, "blocks must be an integer >= 102"),
        (value["chain"] == "regtest", "chain must be regtest"),
        (
            type(value["confirmations"]) is int and value["confirmations"] >= 1,
            "confirmations must be an integer >= 1",
        ),
        (value["research_only"] is True, "research_only must be true"),
        (
            value["transaction_created_and_mined"] is True,
            "transaction_created_and_mined must be true",
        ),
        (
            type(value["upstream_version"]) is int and value["upstream_version"] > 0,
            "upstream_version must be a positive integer",
        ),
        (
            isinstance(value["txid"], str)
            and len(value["txid"]) == 64
            and all(char in "0123456789abcdefABCDEF" for char in value["txid"]),
            "txid must be a 64-character hexadecimal string",
        ),
    )
    for ok, message in checks:
        if not ok:
            raise SystemExit(f"{label} baseline invalid: {message}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("vanilla")
    parser.add_argument("experiment_off")
    args = parser.parse_args()

    vanilla = load(args.vanilla)
    experiment_off = load(args.experiment_off)
    validate("vanilla", vanilla)
    validate("experiment-off", experiment_off)

    left = {key: vanilla[key] for key in FIELDS}
    right = {key: experiment_off[key] for key in FIELDS}
    if left != right:
        raise SystemExit(
            "experiment-off regtest behavior diverged from vanilla baseline:\n"
            + json.dumps({"vanilla": left, "experiment_off": right}, indent=2, sort_keys=True)
        )

    print(json.dumps({"equivalent": True, "fields": list(FIELDS)}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
