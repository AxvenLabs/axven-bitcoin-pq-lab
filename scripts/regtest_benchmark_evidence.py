#!/usr/bin/env python3
"""Canonical raw benchmark evidence for the off-consensus regtest research path."""
from __future__ import annotations
import argparse, hashlib, json
from scripts.benchmark_mldsa_candidates import build_report
EXPECTED=("ML-DSA-44","ML-DSA-65","ML-DSA-87")
def _digest(v): return hashlib.sha256(json.dumps(v,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def build_benchmark_evidence(iterations=25):
    report=build_report(iterations=iterations)
    if report.get("research_only") is not True or report.get("endorsed_by_bitcoin_core") is not False: raise ValueError("benchmark safety boundary drift")
    if report.get("mainnet_intended") is not False or report.get("parameter_set_selected") is not False or report.get("bitcoin_core_modified") is not False: raise ValueError("benchmark deployment boundary drift")
    rows=report.get("candidates")
    if not isinstance(rows,list) or [r.get("candidate") for r in rows]!=list(EXPECTED): raise ValueError("candidate order mismatch")
    for row in rows:
        if row.get("iterations")!=iterations or iterations<3: raise ValueError("invalid iterations")
        for k in ("sign_wall","sign_cpu","verify_wall","verify_cpu"):
            if len(row.get(k,{}).get("samples_ns",[]))!=iterations: raise ValueError(f"missing raw {k} samples")
        for k in ("public_key_bytes","secret_key_bytes","signature_bytes","process_max_rss_bytes"):
            if not isinstance(row.get(k),int) or row[k]<=0: raise ValueError(f"invalid {k}")
        if row.get("python_peak_alloc_bytes",-1)<0: raise ValueError("invalid allocation evidence")
        oracle=row.get("correctness_oracle",{})
        if oracle.get("valid_signature_accepted") is not True or oracle.get("altered_message_rejected") is not True: raise ValueError("correctness oracle failed")
    cross=report.get("cross_candidate_negative",{})
    if cross.get("all_rejected") is not True or len(cross.get("cases",[]))!=6 or not all(x.get("rejected") is True for x in cross["cases"]): raise ValueError("cross-candidate negative evidence failed")
    payload={"schema_version":2,"research_only":True,"network":"regtest","endorsed_by_bitcoin_core":False,"mainnet_intended":False,"off_consensus":True,
             "bitcoin_core_modified":False,"script_semantics_defined":False,"consensus_changed":False,"parameter_set_selected":False,"candidate_order":list(EXPECTED),
             "correctness_oracle_separate":True,"native_windows_resource_portability_demonstrated":False,"benchmark_report":report}
    return {**payload,"benchmark_evidence_sha256":_digest(payload)}
def main():
    p=argparse.ArgumentParser(); p.add_argument("--iterations",type=int,default=25); a=p.parse_args(); print(json.dumps(build_benchmark_evidence(a.iterations),sort_keys=True,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
