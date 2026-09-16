#!/usr/bin/env python3
"""Canonical provenance evidence for the public regtest research checkpoint.

Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.
This records execution provenance only. Bitcoin Core/Script/consensus remain
unmodified; Bitcoin Core does not validate ML-DSA; no deployment parameter set
or Script/output/witness semantics are selected.
"""
from __future__ import annotations

import argparse
import hashlib
import json

EXPECTED_TAG = "v31.1"
EXPECTED_COMMIT = "9be056a8a72b624dae9623b2f7bded92c2a21c91"


def _sha(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def build_provenance(*, repo_commit: str, bitcoin_version: str, python_version: str,
                     cryptography_version: str, os_name: str, machine: str) -> dict:
    if len(repo_commit) != 40 or any(c not in "0123456789abcdef" for c in repo_commit):
        raise ValueError("repo_commit must be 40 lowercase hex characters")
    if EXPECTED_TAG not in bitcoin_version:
        raise ValueError("Bitcoin Core binary is not the pinned v31.1 baseline")
    for name, value in (("python_version", python_version), ("cryptography_version", cryptography_version),
                        ("os_name", os_name), ("machine", machine)):
        if not isinstance(value, str) or not value.strip():
            raise ValueError(f"missing {name}")
    payload = {
        "schema_version": 1,
        "research_only": True,
        "endorsed_by_bitcoin_core": False,
        "mainnet_intended": False,
        "off_consensus": True,
        "bitcoin_core_modified": False,
        "script_semantics_defined": False,
        "consensus_changed": False,
        "parameter_set_selected": False,
        "bitcoin_core_validates_mldsa": False,
        "repo_commit": repo_commit,
        "bitcoin_core": {"tag": EXPECTED_TAG, "commit_sha": EXPECTED_COMMIT, "binary_version": bitcoin_version.strip()},
        "python_version": python_version.strip(),
        "cryptography_version": cryptography_version.strip(),
        "runtime": {"os": os_name.strip(), "machine": machine.strip()},
        "native_windows_resource_portability_demonstrated": False,
    }
    return {**payload, "provenance_sha256": _sha(payload)}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--repo-commit", required=True)
    p.add_argument("--bitcoin-version", required=True)
    p.add_argument("--python-version", required=True)
    p.add_argument("--cryptography-version", required=True)
    p.add_argument("--os-name", required=True)
    p.add_argument("--machine", required=True)
    a = p.parse_args()
    print(json.dumps(build_provenance(repo_commit=a.repo_commit, bitcoin_version=a.bitcoin_version,
                                     python_version=a.python_version, cryptography_version=a.cryptography_version,
                                     os_name=a.os_name, machine=a.machine), sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
