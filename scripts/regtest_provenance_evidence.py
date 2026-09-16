#!/usr/bin/env python3
"""Canonical execution provenance for the public regtest research checkpoint."""
from __future__ import annotations
import argparse, hashlib, json
EXPECTED_TAG="v31.1"
EXPECTED_COMMIT="9be056a8a72b624dae9623b2f7bded92c2a21c91"
EXPECTED_TAG_OBJECT="bfa6a4b79cd4c1562fd32857e3147763efae37fb"
def _sha(p): return hashlib.sha256(json.dumps(p,sort_keys=True,separators=(",",":")).encode()).hexdigest()
def _hex(v,n): return isinstance(v,str) and len(v)==n and all(c in "0123456789abcdef" for c in v)
def build_provenance(*,repo_commit,bitcoin_version,source_commit,tag,tag_object,bitcoind_sha256,bitcoin_cli_sha256,python_version,cryptography_version,openssl_version,os_name,machine):
    if not _hex(repo_commit,40): raise ValueError("invalid repo commit")
    if EXPECTED_TAG not in bitcoin_version or source_commit!=EXPECTED_COMMIT or tag!=EXPECTED_TAG or tag_object!=EXPECTED_TAG_OBJECT: raise ValueError("Bitcoin Core source pin mismatch")
    if not _hex(bitcoind_sha256,64) or not _hex(bitcoin_cli_sha256,64): raise ValueError("invalid binary digest")
    for n,v in (("python",python_version),("cryptography",cryptography_version),("openssl",openssl_version),("os",os_name),("machine",machine)):
        if not isinstance(v,str) or not v.strip(): raise ValueError(f"missing {n}")
    payload={"schema_version":2,"research_only":True,"endorsed_by_bitcoin_core":False,"mainnet_intended":False,"off_consensus":True,"bitcoin_core_modified":False,
             "script_semantics_defined":False,"consensus_changed":False,"parameter_set_selected":False,"bitcoin_core_validates_mldsa":False,
             "repo_commit":repo_commit,"bitcoin_core":{"tag":tag,"tag_object":tag_object,"commit_sha":source_commit,"binary_version":bitcoin_version.strip(),
             "bitcoind_sha256":bitcoind_sha256,"bitcoin_cli_sha256":bitcoin_cli_sha256,"source_identity_verified_from_git":True},
             "python_version":python_version.strip(),"cryptography_version":cryptography_version.strip(),"openssl_version":openssl_version.strip(),
             "runtime":{"os":os_name.strip(),"machine":machine.strip()},"native_windows_resource_portability_demonstrated":False}
    return {**payload,"provenance_sha256":_sha(payload)}
def main():
    p=argparse.ArgumentParser()
    for x in ("repo-commit","bitcoin-version","source-commit","tag","tag-object","bitcoind-sha256","bitcoin-cli-sha256","python-version","cryptography-version","openssl-version","os-name","machine"): p.add_argument("--"+x,required=True)
    a=p.parse_args(); print(json.dumps(build_provenance(repo_commit=a.repo_commit,bitcoin_version=a.bitcoin_version,source_commit=a.source_commit,tag=a.tag,tag_object=a.tag_object,bitcoind_sha256=a.bitcoind_sha256,bitcoin_cli_sha256=a.bitcoin_cli_sha256,python_version=a.python_version,cryptography_version=a.cryptography_version,openssl_version=a.openssl_version,os_name=a.os_name,machine=a.machine),sort_keys=True,indent=2)); return 0
if __name__=="__main__": raise SystemExit(main())
