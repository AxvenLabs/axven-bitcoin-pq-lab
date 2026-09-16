#!/usr/bin/env python3
"""Compose independently produced regtest research evidence into one envelope.

Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.
Bitcoin Core/Script/consensus remain unmodified; Bitcoin Core does not validate
ML-DSA. This module does not select an ML-DSA deployment parameter set.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def _digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def build_e2e_evidence(chain: dict, composition: dict, benchmark: dict) -> dict:
    for name, evidence in (("chain", chain), ("composition", composition), ("benchmark", benchmark)):
        if evidence.get("research_only") is not True:
            raise ValueError(f"{name} research boundary drift")
        if evidence.get("endorsed_by_bitcoin_core") is not False or evidence.get("mainnet_intended") is not False:
            raise ValueError(f"{name} deployment boundary drift")
        if evidence.get("bitcoin_core_modified") is not False or evidence.get("parameter_set_selected") is not False:
            raise ValueError(f"{name} Bitcoin/parameter boundary drift")

    if chain.get("outpoint", {}).get("txid") != composition.get("outpoint", {}).get("txid"):
        raise ValueError("chain/composition txid mismatch")
    if chain.get("outpoint", {}).get("vout") != composition.get("outpoint", {}).get("vout"):
        raise ValueError("chain/composition vout mismatch")
    if composition.get("hybrid_research_semantics") != "classical-and-pq":
        raise ValueError("unexpected hybrid research semantics")
    if benchmark.get("correctness_oracle_separate") is not True:
        raise ValueError("benchmark correctness oracle is not separate")
    if benchmark.get("native_windows_resource_portability_demonstrated") is not False:
        raise ValueError("native Windows portability boundary drift")

    payload = {
        "schema_version": 1,
        "research_only": True,
        "network": "regtest",
        "endorsed_by_bitcoin_core": False,
        "mainnet_intended": False,
        "off_consensus": True,
        "bitcoin_core_modified": False,
        "script_semantics_defined": False,
        "consensus_changed": False,
        "parameter_set_selected": False,
        "bitcoin_core_validates_mldsa": False,
        "native_windows_resource_portability_demonstrated": False,
        "chain_evidence_sha256": chain["chain_evidence_sha256"],
        "composition_sha256": composition["composition_sha256"],
        "benchmark_evidence_sha256": benchmark["benchmark_evidence_sha256"],
        "outpoint": {"txid": chain["outpoint"]["txid"], "vout": chain["outpoint"]["vout"]},
        "confirmation": chain["confirmation"],
        "transaction": chain["transaction"],
        "hybrid_research_semantics": "classical-and-pq",
        "candidate_order": benchmark["candidate_order"],
    }
    return {**payload, "e2e_evidence_sha256": _digest(payload)}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--chain", type=Path, required=True)
    p.add_argument("--composition", type=Path, required=True)
    p.add_argument("--benchmark", type=Path, required=True)
    a = p.parse_args()
    chain = json.loads(a.chain.read_text())
    composition = json.loads(a.composition.read_text())
    benchmark = json.loads(a.benchmark.read_text())
    print(json.dumps(build_e2e_evidence(chain, composition, benchmark), sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
