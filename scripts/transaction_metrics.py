#!/usr/bin/env python3
"""Extract structural metrics from Bitcoin Core getrawtransaction verbose JSON.

Research-only helper. This module does not define PQ, consensus, activation,
recovery, key-custody, or mainnet behavior.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

HEX_RE = re.compile(r"[0-9a-fA-F]*\Z")
TXID_RE = re.compile(r"[0-9a-f]{64}\Z")


def _require_positive_int(tx: dict, key: str) -> int:
    value = tx.get(key)
    if not isinstance(value, int) or isinstance(value, bool) or value <= 0:
        raise ValueError(f"{key} must be a positive integer")
    return value


def extract_metrics(tx: dict) -> dict:
    if not isinstance(tx, dict):
        raise ValueError("transaction must be a JSON object")

    txid = tx.get("txid")
    if not isinstance(txid, str) or not TXID_RE.fullmatch(txid):
        raise ValueError("txid must be 64 lowercase hexadecimal characters")

    size = _require_positive_int(tx, "size")
    vsize = _require_positive_int(tx, "vsize")
    weight = _require_positive_int(tx, "weight")

    if weight > size * 4:
        raise ValueError("weight cannot exceed four times serialized size")
    if not ((weight + 3) // 4 == vsize):
        raise ValueError("vsize must equal ceil(weight / 4)")

    vin = tx.get("vin")
    vout = tx.get("vout")
    if not isinstance(vin, list) or not vin:
        raise ValueError("vin must be a non-empty list")
    if not isinstance(vout, list) or not vout:
        raise ValueError("vout must be a non-empty list")

    witness_item_bytes: list[int] = []
    witness_input_count = 0
    for txin in vin:
        if not isinstance(txin, dict):
            raise ValueError("each vin entry must be an object")
        witness = txin.get("txinwitness", [])
        if not isinstance(witness, list):
            raise ValueError("txinwitness must be a list when present")
        if witness:
            witness_input_count += 1
        for item in witness:
            if not isinstance(item, str) or len(item) % 2 or not HEX_RE.fullmatch(item):
                raise ValueError("witness items must be even-length hexadecimal strings")
            witness_item_bytes.append(len(item) // 2)

    return {
        "input_count": len(vin),
        "output_count": len(vout),
        "research_only": True,
        "serialized_size_bytes": size,
        "total_witness_item_bytes": sum(witness_item_bytes),
        "txid": txid,
        "virtual_size_vbytes": vsize,
        "weight_units": weight,
        "witness_input_count": witness_input_count,
        "witness_item_bytes": witness_item_bytes,
        "witness_item_count": len(witness_item_bytes),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", nargs="?", help="getrawtransaction verbose JSON; stdin if omitted")
    args = parser.parse_args()

    if args.input:
        raw = pathlib.Path(args.input).read_text(encoding="utf-8")
    else:
        raw = sys.stdin.read()
    metrics = extract_metrics(json.loads(raw))
    print(json.dumps(metrics, sort_keys=True))


if __name__ == "__main__":
    main()
