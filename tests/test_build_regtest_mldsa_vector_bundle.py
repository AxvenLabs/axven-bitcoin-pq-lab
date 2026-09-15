import copy
import unittest

try:
    from scripts.build_regtest_mldsa_vector_bundle import CANDIDATES, build_bundle
except ImportError as exc:
    if exc.name and exc.name.startswith("cryptography"):
        build_bundle = None
        CANDIDATES = ()
    else:
        raise


@unittest.skipUnless(build_bundle is not None, "requires pinned ML-DSA benchmark backend")
class RegtestMldsaVectorBundleTests(unittest.TestCase):
    def test_bundle_is_deterministic_candidate_neutral_and_complete(self):
        first = build_bundle()
        second = build_bundle()
        self.assertEqual(first, second)
        self.assertTrue(first["research_only"])
        self.assertEqual(first["network"], "regtest")
        self.assertFalse(first["mainnet_intended"])
        self.assertTrue(first["off_consensus"])
        self.assertFalse(first["parameter_set_selected"])
        self.assertFalse(first["bitcoin_core_modified"])
        self.assertFalse(first["script_semantics_defined"])
        self.assertFalse(first["consensus_changed"])
        self.assertEqual(first["candidates"], list(CANDIDATES))
        self.assertEqual(len(first["vectors"]), 6)

    def test_classical_and_pq_result_is_exposed_without_selecting_candidate(self):
        bundle = build_bundle()
        seen = set()
        for row in bundle["vectors"]:
            seen.add((row["candidate"], row["classical_valid"]))
            self.assertIs(row["authorized"], row["classical_valid"])
            self.assertTrue(row["pq_altered_transcript_rejected"])
            self.assertEqual(len(row["demo_sha256"]), 64)
            self.assertEqual(len(row["transcript_sha256"]), 64)
            self.assertEqual(len(row["public_key_sha256"]), 64)
        self.assertEqual(seen, {(name, value) for name in CANDIDATES for value in (False, True)})

    def test_vectors_do_not_expose_secret_or_selection_fields(self):
        bundle = build_bundle()
        forbidden = {"private_key", "seed", "signature", "winner", "rank", "score", "preferred", "selected"}

        def walk(value):
            if isinstance(value, dict):
                for key, item in value.items():
                    self.assertNotIn(key.lower(), forbidden)
                    walk(item)
            elif isinstance(value, list):
                for item in value:
                    walk(item)

        walk(copy.deepcopy(bundle))


if __name__ == "__main__":
    unittest.main()
