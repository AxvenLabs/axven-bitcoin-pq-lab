import unittest

try:
    from scripts.benchmark_mldsa_candidates import CANDIDATES, benchmark_candidate, build_report
except ModuleNotFoundError as exc:
    if exc.name == "cryptography":
        raise unittest.SkipTest("cryptography benchmark dependency is exercised in dedicated CI job")
    raise


class MldsaCandidateBenchmarkTests(unittest.TestCase):
    def test_report_is_research_only_and_does_not_select_winner(self):
        report = build_report(iterations=3)
        self.assertTrue(report["research_only"])
        self.assertFalse(report["mainnet_intended"])
        self.assertFalse(report["parameter_set_selected"])
        self.assertFalse(report["deployment_winner_selected"])
        self.assertFalse(report["bitcoin_core_modified"])
        self.assertFalse(report["bitcoin_script_semantics_selected"])
        self.assertFalse(report["consensus_change_selected"])
        self.assertEqual(report["candidate_family"], "ML-DSA")
        self.assertEqual(report["hybrid_research_semantics"], "classical-and-pq")
        self.assertEqual({row["candidate"] for row in report["candidates"]}, set(CANDIDATES))

    def test_each_candidate_has_positive_sizes_and_correctness_oracle(self):
        report = build_report(iterations=3)
        for row in report["candidates"]:
            with self.subTest(candidate=row["candidate"]):
                self.assertGreater(row["public_key_bytes"], 0)
                self.assertGreater(row["signature_bytes"], 0)
                self.assertGreater(row["verify_median_ns"], 0)
                self.assertGreater(row["process_max_rss_bytes"], 0)
                self.assertTrue(row["correctness_oracle"]["valid_signature_accepted"])
                self.assertTrue(row["correctness_oracle"]["altered_message_rejected"])

    def test_invalid_inputs_fail_closed(self):
        with self.assertRaises(ValueError):
            benchmark_candidate("ML-DSA-44", 2, b"message")
        with self.assertRaises(ValueError):
            benchmark_candidate("not-a-candidate", 3, b"message")
        with self.assertRaises(ValueError):
            benchmark_candidate("ML-DSA-44", 3, b"")


if __name__ == "__main__":
    unittest.main()
