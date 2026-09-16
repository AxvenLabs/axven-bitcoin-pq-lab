#!/usr/bin/env python3
"""Independent fail-closed validator for regtest provenance evidence.

Research only. Not endorsed by Bitcoin Core. Not intended for mainnet.
Bitcoin Core/Script/consensus remain unmodified and Bitcoin Core does not
validate ML-DSA. This validates evidence shape/boundaries only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from scripts.regtest_provenance_evidence import EXPECTED_COMMIT, EXPECTED_TAG


def _sha(payload: dict) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def validate_provenance(report: dict) -> str:
    if not isinstance(report, dict):
        raise ValueError("provenance report must be an object")
    required_false = (
        "endorsed_by_bitcoin_core", "mainnet_intended", "bitcoin_core_modified",
        "script_semantics_defined", "consensus_changed", "parameter_set_selected",
        "bitcoin_core_validates_mldsa", "native_windows_resource_portability_demonstrated",
    )
    if report.get("schema_version") != 1 or report.get("research_only") is not True or report.get("off_consensus") is not True:
        raise ValueError("research boundary mismatch")
    if any(report.get(name) is not False for name in required_false):
        raise ValueError("provenance overclaim or boundary mismatch")
    repo_commit = report.get("repo_commit")
    if not isinstance(repo_commit, str) or len(repo_commit) != 40 or any(c not in "0123456789abcdef" for c in repo_commit):
        raise ValueError("invalid repository commit")
    bitcoin = report.get("bitcoin_core")
    if not isinstance(bitcoin, dict) or bitcoin.get("tag") != EXPECTED_TAG or bitcoin.get("commit_sha") != EXPECTED_COMMIT:
        raise ValueError("Bitcoin Core pin mismatch")
    if EXPECTED_TAG not in str(bitcoin.get("binary_version", "")):
        raise ValueError("Bitcoin Core binary version mismatch")
    runtime = report.get("runtime")
    if not isinstance(runtime, dict) or not runtime.get("os") or not runtime.get("machine"):
        raise ValueError("missing runtime identity")
    for name in ("python_version", "cryptography_version"):
        if not isinstance(report.get(name), str) or not report[name].strip():
            raise ValueError(f"missing {name}")
    claimed = report.get("provenance_sha256")
    if not isinstance(claimed, str) or len(claimed) != 64:
        raise ValueError("invalid provenance digest")
    payload = dict(report)
    payload.pop("provenance_sha256", None)
    actual = _sha(payload)
    if claimed != actual:
        raise ValueError("provenance digest mismatch")
    return actual


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("report")
    a = p.parse_args()
    report = json.loads(Path(a.report).read_text(encoding="utf-8"))
    print(validate_provenance(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
