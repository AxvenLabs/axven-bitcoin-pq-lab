import copy

import pytest

from scripts.build_regtest_vector_manifest import build_manifest
from scripts.validate_regtest_vector_manifest import validate_manifest


def test_manifest_validates_and_is_deterministic():
    first = build_manifest()
    second = build_manifest()
    assert first == second
    assert validate_manifest(first) == first["manifest_sha256"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("research_only", False),
        ("network", "mainnet"),
        ("endorsed_by_bitcoin_core", True),
        ("mainnet_intended", True),
        ("off_consensus", False),
        ("parameter_set_selected", True),
        ("bitcoin_core_modified", True),
        ("script_semantics_defined", True),
        ("consensus_changed", True),
        ("vector_count", 5),
        ("correctness_oracle_separate", False),
        ("timing_data_included", True),
    ],
)
def test_manifest_rejects_boundary_drift(field, value):
    manifest = build_manifest()
    manifest[field] = value
    with pytest.raises(ValueError):
        validate_manifest(manifest)


def test_manifest_rejects_candidate_reordering():
    manifest = build_manifest()
    manifest["candidates"] = list(reversed(manifest["candidates"]))
    with pytest.raises(ValueError):
        validate_manifest(manifest)


def test_manifest_rejects_digest_tampering():
    manifest = build_manifest()
    manifest["source_bundle_sha256"] = "00" * 32
    with pytest.raises(ValueError, match="manifest digest mismatch"):
        validate_manifest(manifest)


@pytest.mark.parametrize("key", ["winner", "recommended", "rank", "score", "selected", "preferred"])
def test_manifest_rejects_selection_fields(key):
    manifest = build_manifest()
    manifest["metadata"] = {key: "ML-DSA-44"}
    with pytest.raises(ValueError, match="forbidden manifest field"):
        validate_manifest(manifest)


@pytest.mark.parametrize("key", ["private_key", "secret", "seed", "raw_signature", "signature_hex"])
def test_manifest_rejects_secret_or_raw_signature_fields(key):
    manifest = build_manifest()
    manifest["metadata"] = {key: "not-allowed"}
    with pytest.raises(ValueError, match="forbidden manifest field"):
        validate_manifest(manifest)
