import copy
import unittest

try:
    from scripts.build_regtest_mldsa_vector_bundle import build_bundle
    from scripts.validate_regtest_mldsa_vector_bundle import validate_bundle
except ImportError as exc:
    if exc.name and exc.name.startswith("cryptography"):
        build_bundle = validate_bundle = None
    else:
        raise


@unittest.skipUnless(build_bundle is not None, "requires pinned ML-DSA benchmark backend")
class RegtestMldsaVectorBundleValidatorTests(unittest.TestCase):
    def test_valid_bundle_revalidates_deterministically(self):
        bundle = build_bundle()
        self.assertEqual(validate_bundle(bundle), bundle["bundle_sha256"])
        self.assertEqual(validate_bundle(copy.deepcopy(bundle)), bundle["bundle_sha256"])

    def test_tampering_and_safety_drift_fail_closed(self):
        base = build_bundle()
        mutations = []
        for key, value in (
            ("parameter_set_selected", True),
            ("mainnet_intended", True),
            ("bitcoin_core_modified", True),
            ("script_semantics_defined", True),
            ("consensus_changed", True),
            ("bundle_sha256", "00" * 32),
        ):
            item = copy.deepcopy(base)
            item[key] = value
            mutations.append(item)
        changed = copy.deepcopy(base)
        changed["vectors"][0]["authorized"] = True
        mutations.append(changed)
        changed = copy.deepcopy(base)
        changed["vectors"][0]["signature_bytes"] = 1
        mutations.append(changed)
        changed = copy.deepcopy(base)
        changed["vectors"][0]["pq_altered_transcript_rejected"] = False
        mutations.append(changed)
        changed = copy.deepcopy(base)
        changed["vectors"].reverse()
        mutations.append(changed)
        for item in mutations:
            with self.assertRaises(ValueError):
                validate_bundle(item)

    def test_secret_and_selection_fields_fail_closed(self):
        for key, value in (
            ("winner", "ML-DSA-44"),
            ("rank", 1),
            ("seed", "public-lab-seed"),
            ("signature", "00"),
            ("private_key", "00"),
        ):
            bundle = build_bundle()
            bundle["vectors"][0][key] = value
            with self.assertRaises(ValueError):
                validate_bundle(bundle)


if __name__ == "__main__":
    unittest.main()
