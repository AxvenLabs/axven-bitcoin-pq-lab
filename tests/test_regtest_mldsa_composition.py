import unittest

from scripts.regtest_mldsa_composition import build_composition


class RegtestMldsaCompositionTests(unittest.TestCase):
    def test_all_candidates_and_truth_table_are_recorded_without_selection(self):
        report = build_composition(txid="ab" * 32, vout=2, message_digest="cd" * 32)
        self.assertEqual(set(report["candidates"]), {"ML-DSA-44", "ML-DSA-65", "ML-DSA-87"})
        self.assertFalse(report["parameter_set_selected"])
        self.assertFalse(report["bitcoin_core_modified"])
        self.assertFalse(report["consensus_changed"])
        self.assertFalse(report["script_semantics_defined"])
        for result in report["candidates"].values():
            self.assertTrue(result["valid_signature_accepted"])
            self.assertTrue(result["altered_transcript_rejected"])
            self.assertTrue(result["classical_and_pq_positive_authorized"])
            self.assertFalse(result["classical_false_pq_true_authorized"])

    def test_composition_is_deterministic(self):
        args = dict(txid="12" * 32, vout=0, message_digest="34" * 32)
        self.assertEqual(build_composition(**args), build_composition(**args))


if __name__ == "__main__":
    unittest.main()
