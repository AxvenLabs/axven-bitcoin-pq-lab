#!/usr/bin/env python3
"""Scheme-neutral structural size model for opaque authorization material.

Research only. Not endorsed by Bitcoin Core and not intended for mainnet use.
This model does not select a post-quantum scheme, define hybrid authorization
semantics, alter Bitcoin consensus, or prescribe migration/activation policy.
It only measures hypothetical serialized witness-item overhead for opaque byte
payloads so candidate designs can later be compared without freezing one here.
"""

from __future__ import annotations

import argparse
import json


def compact_size_len(value: int) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 0:
        raise ValueError("value must be a non-negative integer")
    if value < 253:
        return 1
    if value <= 0xFFFF:
        return 3
    if value <= 0xFFFFFFFF:
        return 5
    if value <= 0xFFFFFFFFFFFFFFFF:
        return 9
    raise ValueError("value exceeds CompactSize range")


def witness_item_serialized_bytes(payload_bytes: int) -> int:
    """Return CompactSize length prefix + opaque payload bytes."""
    return compact_size_len(payload_bytes) + payload_bytes


def structural_case(payload_bytes: int) -> dict[str, int]:
    serialized = witness_item_serialized_bytes(payload_bytes)
    # Witness bytes contribute one weight unit per byte. This is intentionally a
    # marginal structural model, not a complete transaction template.
    return {
        "payload_bytes": payload_bytes,
        "length_prefix_bytes": compact_size_len(payload_bytes),
        "serialized_witness_item_bytes": serialized,
        "marginal_weight_units": serialized,
        "marginal_vbytes_ceiling": (serialized + 3) // 4,
    }


def build_report(payload_sizes: list[int]) -> dict:
    if not isinstance(payload_sizes, list) or not payload_sizes:
        raise ValueError("at least one payload size is required")
    if len(set(payload_sizes)) != len(payload_sizes):
        raise ValueError("payload sizes must be unique")
    cases = [structural_case(size) for size in payload_sizes]
    return {
        "schema_version": 1,
        "research_only": True,
        "network_scope": "none-structural-model",
        "endorsed_by_bitcoin_core": False,
        "mainnet_intended": False,
        "scheme_selected": False,
        "hybrid_semantics_selected": False,
        "measurement": "hypothetical opaque witness-item structural overhead",
        "cases": cases,
    }


def parse_sizes(raw: str) -> list[int]:
    try:
        values = [int(part.strip()) for part in raw.split(",") if part.strip()]
    except ValueError as exc:
        raise argparse.ArgumentTypeError("sizes must be comma-separated integers") from exc
    if not values:
        raise argparse.ArgumentTypeError("at least one size is required")
    if any(value < 0 for value in values):
        raise argparse.ArgumentTypeError("sizes must be non-negative")
    return values


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sizes",
        type=parse_sizes,
        default=[64, 128, 256, 512, 1024, 2048, 4096],
        help="comma-separated opaque payload sizes in bytes",
    )
    args = parser.parse_args()
    print(json.dumps(build_report(args.sizes), sort_keys=True, indent=2))


if __name__ == "__main__":
    main()
