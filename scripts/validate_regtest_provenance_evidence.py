#!/usr/bin/env python3
"""Independent fail-closed validator for complete regtest provenance evidence."""
from __future__ import annotations
import argparse,hashlib,json
from pathlib import Path
from scripts.regtest_provenance_evidence import EXPECTED_COMMIT,EXPECTED_TAG,EXPECTED_TAG_OBJECT
def _sha(p): return hashlib.sha256(json.dumps(p,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def _hex(v,n): return isinstance(v,str) and len(v)==n and all(c in "0123456789abcdef" for c in v)
def validate_provenance(r):
    false=("endorsed_by_bitcoin_core","mainnet_intended","bitcoin_core_modified","script_semantics_defined","consensus_changed","parameter_set_selected","bitcoin_core_validates_mldsa","native_windows_resource_portability_demonstrated")
    if r.get("schema_version")!=2 or r.get("research_only") is not True or r.get("off_consensus") is not True: raise ValueError("research boundary mismatch")
    if any(r.get(x) is not False for x in false): raise ValueError("provenance overclaim or boundary mismatch")
    if not _hex(r.get("repo_commit"),40): raise ValueError("invalid repository commit")
    b=r.get("bitcoin_core",{})
    if b.get("tag")!=EXPECTED_TAG or b.get("tag_object")!=EXPECTED_TAG_OBJECT or b.get("commit_sha")!=EXPECTED_COMMIT or b.get("source_identity_verified_from_git") is not True: raise ValueError("Bitcoin Core pin mismatch")
    if EXPECTED_TAG not in str(b.get("binary_version","")): raise ValueError("Bitcoin Core binary version mismatch")
    if not _hex(b.get("bitcoind_sha256"),64) or not _hex(b.get("bitcoin_cli_sha256"),64): raise ValueError("invalid Bitcoin binary digest")
    for n in ("python_version","cryptography_version","openssl_version"):
        if not isinstance(r.get(n),str) or not r[n].strip(): raise ValueError(f"missing {n}")
    rt=r.get("runtime",{})
    if not rt.get("os") or not rt.get("machine"): raise ValueError("missing runtime identity")
    claimed=r.get("provenance_sha256"); payload=dict(r); payload.pop("provenance_sha256",None); actual=_sha(payload)
    if not _hex(claimed,64) or claimed!=actual: raise ValueError("provenance digest mismatch")
    return actual
def main():
    p=argparse.ArgumentParser(); p.add_argument("report"); a=p.parse_args(); print(validate_provenance(json.loads(Path(a.report).read_text()))); return 0
if __name__=="__main__": raise SystemExit(main())
