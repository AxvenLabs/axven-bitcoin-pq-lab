#!/usr/bin/env python3
"""Compose complete independently generated regtest research evidence."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from scripts.validate_regtest_provenance_evidence import validate_provenance
def _digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def build_e2e_evidence(chain,composition,benchmark,provenance):
    for n,e in (("chain",chain),("composition",composition),("benchmark",benchmark),("provenance",provenance)):
        if e.get("research_only") is not True or e.get("endorsed_by_bitcoin_core") is not False or e.get("mainnet_intended") is not False: raise ValueError(f"{n} boundary drift")
        if e.get("bitcoin_core_modified") is not False or e.get("parameter_set_selected") is not False: raise ValueError(f"{n} Bitcoin/parameter boundary drift")
    validate_provenance(provenance)
    if chain.get("outpoint",{}).get("txid")!=composition.get("outpoint",{}).get("txid") or chain.get("outpoint",{}).get("vout")!=composition.get("outpoint",{}).get("vout"): raise ValueError("chain/composition outpoint mismatch")
    if composition.get("hybrid_research_semantics")!="classical-and-pq": raise ValueError("unexpected hybrid semantics")
    if benchmark.get("correctness_oracle_separate") is not True or benchmark.get("native_windows_resource_portability_demonstrated") is not False: raise ValueError("benchmark boundary drift")
    payload={"schema_version":2,"research_only":True,"network":"regtest","endorsed_by_bitcoin_core":False,"mainnet_intended":False,"off_consensus":True,
             "bitcoin_core_modified":False,"script_semantics_defined":False,"consensus_changed":False,"parameter_set_selected":False,"bitcoin_core_validates_mldsa":False,
             "native_windows_resource_portability_demonstrated":False,"hybrid_research_semantics":"classical-and-pq","candidate_order":benchmark["candidate_order"],
             "chain_evidence":chain,"composition_evidence":composition,"benchmark_evidence":benchmark,"provenance_evidence":provenance,
             "chain_evidence_sha256":chain["chain_evidence_sha256"],"composition_sha256":composition["composition_sha256"],
             "benchmark_evidence_sha256":benchmark["benchmark_evidence_sha256"],"provenance_sha256":provenance["provenance_sha256"],
             "outpoint":chain["outpoint"],"confirmation":chain["confirmation"],"transaction":chain["transaction"]}
    return {**payload,"e2e_evidence_sha256":_digest(payload)}
def main():
    p=argparse.ArgumentParser()
    for n in ("chain","composition","benchmark","provenance"): p.add_argument("--"+n,type=Path,required=True)
    a=p.parse_args(); load=lambda p:json.loads(p.read_text()); print(json.dumps(build_e2e_evidence(load(a.chain),load(a.composition),load(a.benchmark),load(a.provenance)),sort_keys=True,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
