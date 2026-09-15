import copy
import unittest

try:
    from scripts.build_regtest_vector_manifest import build_manifest
    from scripts.validate_regtest_vector_manifest import validate_manifest
except ImportError as exc:
    if exc.name and exc.name.startswith("cryptography"):
        build_manifest = validate_manifest = None
    else:
        raise


@unittest.skipUnless(build_manifest is not None, "requires pinned ML-DSA benchmark backend")
class RegtestVectorManifestValidatorTests(unittest.TestCase):
    def test_manifest_validates_and_is_deterministic(self):
        first = build_manifest()
        second = build_manifest()
        self.assertEqual(first, second)
        self.assertEqual(validate_manifest(first), first["manifest_sha256"])

    def test_manifest_rejects_boundary_drift(self):
        cases = [
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
        ]
        for field, value in cases:
            with self.subTest(field=field):
                manifest = build_manifest()
                manifest[field] = value
                with self.assertRaises(ValueError):
                    validate_manifest(manifest)

    def test_manifest_rejects_candidate_reordering(self):
        manifest = build_manifest()
        manifest["candidates"] = list(reversed(manifest["candidates"]))
        with self.assertRaises(ValueError):
            validate_manifest(manifest)

    def test_manifest_rejects_digest_tampering(self):
        manifest = build_manifest()
        manifest["source_bundle_sha256"] = "00" * 32
        with self.assertRaisesRegex(ValueError, "manifest digest mismatch"):
            validate_manifest(manifest)

    def test_manifest_rejects_selection_fields(self):
        for key in ["winner", "recommended", "rank", "score", "selected", "preferred"]:
            with self.subTest(key=key):
                manifest = build_manifest()
                manifest["metadata"] = {key: "ML-DSA-44"}
                with self.assertRaisesRegex(ValueError, "forbidden manifest field"):
                    validate_manifest(manifest)

    def test_manifest_rejects_secret_or_raw_signature_fields(self):
        for key in ["private_key", "secret", "seed", "raw_signature", "signature_hex"]:
            with self.subTest(key=key):
                manifest = build_manifest()
                manifest["metadata"] = {key: "not-allowed"}
                with self.assertRaisesRegex(ValueError, "forbidden manifest field"):
                    validate_manifest(manifest)


if __name__ == "__main__":
    unittest.main()
