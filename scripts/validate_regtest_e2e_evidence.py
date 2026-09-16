#!/usr/bin/env python3
"""Independent fail-closed validator for evidence-complete regtest envelope."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from scripts.validate_regtest_provenance_evidence import validate_provenance
EXPECTED=["ML-DSA-44","ML-DSA-65","ML-DSA-87"]
def _digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def _check_digest(obj,key):
    claimed=obj.get(key); p=dict(obj); p.pop(key,None)
    if claimed!=_digest(p): raise ValueError(f"{key} mismatch")
def validate_e2e_evidence(e):
    req={"schema_version":2,"research_only":True,"network":"regtest","endorsed_by_bitcoin_core":False,"mainnet_intended":False,"off_consensus":True,"bitcoin_core_modified":False,"script_semantics_defined":False,"consensus_changed":False,"parameter_set_selected":False,"bitcoin_core_validates_mldsa":False,"native_windows_resource_portability_demonstrated":False,"hybrid_research_semantics":"classical-and-pq","candidate_order":EXPECTED}
    for k,v in req.items():
        if e.get(k)!=v: raise ValueError(f"unexpected {k}")
    chain=e.get("chain_evidence",{}); comp=e.get("composition_evidence",{}); bench=e.get("benchmark_evidence",{}); prov=e.get("provenance_evidence",{})
    _check_digest(chain,"chain_evidence_sha256"); _check_digest(comp,"composition_sha256"); _check_digest(bench,"benchmark_evidence_sha256"); validate_provenance(prov)
    if e.get("chain_evidence_sha256")!=chain.get("chain_evidence_sha256") or e.get("composition_sha256")!=comp.get("composition_sha256") or e.get("benchmark_evidence_sha256")!=bench.get("benchmark_evidence_sha256") or e.get("provenance_sha256")!=prov.get("provenance_sha256"): raise ValueError("nested digest binding mismatch")
    if e.get("outpoint")!=chain.get("outpoint") or e.get("confirmation")!=chain.get("confirmation") or e.get("transaction")!=chain.get("transaction"): raise ValueError("chain projection mismatch")
    if comp.get("outpoint",{}).get("txid")!=chain.get("outpoint",{}).get("txid") or comp.get("outpoint",{}).get("vout")!=chain.get("outpoint",{}).get("vout"): raise ValueError("composition outpoint mismatch")
    rows=bench.get("benchmark_report",{}).get("candidates",[])
    if [r.get("candidate") for r in rows]!=EXPECTED: raise ValueError("candidate evidence mismatch")
    for r in rows:
        if r.get("correctness_oracle",{}).get("valid_signature_accepted") is not True or r.get("correctness_oracle",{}).get("altered_message_rejected") is not True: raise ValueError("candidate correctness failure")
        for k in ("sign_wall","sign_cpu","verify_wall","verify_cpu"):
            if not r.get(k,{}).get("samples_ns"): raise ValueError("missing raw candidate samples")
    cross=bench.get("benchmark_report",{}).get("cross_candidate_negative",{})
    if cross.get("all_rejected") is not True or not all(x.get("rejected") is True for x in cross.get("cases",[])): raise ValueError("cross-candidate failure")
    claimed=e.get("e2e_evidence_sha256"); p=dict(e); p.pop("e2e_evidence_sha256",None); actual=_digest(p)
    if claimed!=actual: raise ValueError("E2E evidence digest mismatch")
    return actual
def main():
    p=argparse.ArgumentParser(); p.add_argument("report",type=Path); a=p.parse_args(); print(validate_e2e_evidence(json.loads(a.report.read_text()))); return 0
if __name__=="__main__": raise SystemExit(main())
