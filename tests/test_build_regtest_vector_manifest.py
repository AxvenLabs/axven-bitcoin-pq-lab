import copy
import hashlib
import json
import unittest

try:
    from scripts.build_regtest_vector_manifest import build_manifest
except ImportError as exc:
    if exc.name and exc.name.startswith("cryptography"):
        build_manifest = None
    else:
        raise


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


@unittest.skipUnless(build_manifest is not None, "requires pinned ML-DSA benchmark backend")
class RegtestVectorManifestTests(unittest.TestCase):
    def test_manifest_is_deterministic_candidate_neutral(self):
        first = build_manifest()
        second = build_manifest()
        self.assertEqual(first, second)
        self.assertTrue(first["research_only"])
        self.assertEqual(first["network"], "regtest")
        self.assertFalse(first["mainnet_intended"])
        self.assertFalse(first["parameter_set_selected"])
        self.assertFalse(first["bitcoin_core_modified"])
        self.assertFalse(first["script_semantics_defined"])
        self.assertFalse(first["consensus_changed"])
        self.assertFalse(first["timing_data_included"])
        self.assertEqual(first["vector_count"], 6)
        self.assertEqual(first["candidates"], ["ML-DSA-44", "ML-DSA-65", "ML-DSA-87"])

    def test_manifest_digest_binds_public_metadata(self):
        manifest = build_manifest()
        supplied = manifest.pop("manifest_sha256")
        self.assertEqual(supplied, digest(manifest))
        self.assertEqual(len(manifest["source_bundle_sha256"]), 64)

    def test_manifest_exposes_no_selection_or_secret_fields(self):
        manifest = copy.deepcopy(build_manifest())
        forbidden = {"winner", "rank", "score", "preferred", "selected", "private_key", "seed", "signature"}
        self.assertTrue(forbidden.isdisjoint({key.lower() for key in manifest}))


if __name__ == "__main__":
    unittest.main()
