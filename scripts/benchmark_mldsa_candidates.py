#!/usr/bin/env python3
"""Evidence-complete, candidate-neutral ML-DSA benchmark.

Research only. Not endorsed by Bitcoin Core. Not intended for mainnet. No
Bitcoin Core/Script/consensus changes and no deployment parameter selection.
Private key material is never emitted; only its serialized byte length is kept.
"""
from __future__ import annotations
import argparse, json, math, platform, resource, statistics, time, tracemalloc
import cryptography
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends.openssl.backend import backend
from cryptography.hazmat.primitives.asymmetric import mldsa

CANDIDATES={"ML-DSA-44":mldsa.MLDSA44PrivateKey,"ML-DSA-65":mldsa.MLDSA65PrivateKey,"ML-DSA-87":mldsa.MLDSA87PrivateKey}
EXPECTED_SIZES={"ML-DSA-44":(1312,2420),"ML-DSA-65":(1952,3309),"ML-DSA-87":(2592,4627)}

def _rss_bytes():
    v=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if platform.system()=="Darwin": return int(v)
    if platform.system()=="Linux": return int(v)*1024
    raise RuntimeError("unsupported platform for ru_maxrss normalization")
def _median(v): return int(statistics.median(v))
def _p95(v):
    if len(v)<3: raise ValueError("at least three samples are required")
    o=sorted(v); return o[max(1,math.ceil(.95*len(o)))-1]
def _stats(v): return {"samples_ns":v,"min_ns":min(v),"median_ns":_median(v),"p95_ns":_p95(v),"max_ns":max(v)}
def _key(name):
    seed=(name.encode()+b"|axven-bitcoin-pq-lab|bench-008").ljust(32,b"\0")[:32]
    return CANDIDATES[name].from_seed_bytes(seed)

def benchmark_candidate(name,iterations,message):
    if name not in CANDIDATES or isinstance(iterations,bool) or not isinstance(iterations,int) or iterations<3: raise ValueError("invalid candidate/iterations")
    if not isinstance(message,bytes) or not message: raise ValueError("message must be non-empty bytes")
    sk=_key(name); pk=sk.public_key(); pub=pk.public_bytes_raw(); secret_size=len(sk.private_bytes_raw())
    sign_wall=[]; sign_cpu=[]; signatures=[]
    for _ in range(iterations):
        c=time.process_time_ns(); w=time.perf_counter_ns(); sig=sk.sign(message); sign_wall.append(time.perf_counter_ns()-w); sign_cpu.append(time.process_time_ns()-c); signatures.append(sig)
    sig=signatures[-1]; exp_pub,exp_sig=EXPECTED_SIZES[name]
    if len(pub)!=exp_pub or len(sig)!=exp_sig: raise RuntimeError("unexpected ML-DSA size")
    pk.verify(sig,message); altered=message[:-1]+bytes([message[-1]^1])
    try: pk.verify(sig,altered)
    except InvalidSignature: altered_rejected=True
    else: raise RuntimeError("altered message accepted")
    wall=[]; cpu=[]; rss_before=_rss_bytes(); tracemalloc.start()
    try:
        for _ in range(iterations):
            c=time.process_time_ns(); w=time.perf_counter_ns(); pk.verify(sig,message); wall.append(time.perf_counter_ns()-w); cpu.append(time.process_time_ns()-c)
        _,peak=tracemalloc.get_traced_memory()
    finally: tracemalloc.stop()
    rss_after=_rss_bytes()
    return {"candidate":name,"public_key_bytes":len(pub),"secret_key_bytes":secret_size,"signature_bytes":len(sig),"iterations":iterations,
            "sign_wall":_stats(sign_wall),"sign_cpu":_stats(sign_cpu),"verify_wall":_stats(wall),"verify_cpu":_stats(cpu),
            "python_peak_alloc_bytes":peak,"process_max_rss_bytes":rss_after,"process_max_rss_delta_bytes":max(0,rss_after-rss_before),
            "correctness_oracle":{"valid_signature_accepted":True,"altered_message_rejected":altered_rejected}}

def _cross_candidate(message):
    keys={n:_key(n) for n in CANDIDATES}; sigs={n:k.sign(message) for n,k in keys.items()}; rows=[]
    for signer,sig in sigs.items():
        for verifier,key in keys.items():
            if signer==verifier: continue
            try: key.public_key().verify(sig,message)
            except (InvalidSignature,ValueError): rejected=True
            else: rejected=False
            rows.append({"signature_candidate":signer,"verifier_candidate":verifier,"rejected":rejected})
    if not all(r["rejected"] for r in rows): raise RuntimeError("cross-candidate mismatch accepted")
    return rows

def build_report(iterations=25,message=b"axven-bitcoin-pq-lab-bench-008"):
    rows=[benchmark_candidate(n,iterations,message) for n in CANDIDATES]
    return {"schema_version":4,"research_only":True,"endorsed_by_bitcoin_core":False,"mainnet_intended":False,"network_scope":"none-local-cryptographic-benchmark",
            "candidate_family":"ML-DSA","hybrid_research_semantics":"classical-and-pq","parameter_set_selected":False,"deployment_winner_selected":False,
            "bitcoin_core_modified":False,"bitcoin_script_semantics_selected":False,"consensus_change_selected":False,"raw_sample_evidence":True,
            "percentile_method":"nearest-rank","cryptography_version":cryptography.__version__,"openssl_version":backend.openssl_version_text(),
            "python_version":platform.python_version(),"platform":platform.platform(),"message_bytes":len(message),"candidates":rows,
            "cross_candidate_negative":{"scope":"wrong ML-DSA candidate key/signature pairings only","cases":_cross_candidate(message),"all_rejected":True},
            "warning":"Research evidence only; no Bitcoin deployment parameter set is selected."}
def main():
    p=argparse.ArgumentParser(); p.add_argument("--iterations",type=int,default=25); a=p.parse_args(); print(json.dumps(build_report(a.iterations),sort_keys=True,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
