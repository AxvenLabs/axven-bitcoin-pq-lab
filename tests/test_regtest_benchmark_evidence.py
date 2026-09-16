import unittest
from unittest.mock import patch

try:
    import scripts.regtest_benchmark_evidence as subject
except (ImportError, ModuleNotFoundError):
    subject = None


@unittest.skipIf(subject is None, "requires pinned ML-DSA benchmark backend and Unix resource module")
class RegtestBenchmarkEvidenceTests(unittest.TestCase):
    def test_records_raw_timing_cpu_rss_without_selection(self):
        evidence = subject.build_benchmark_evidence(iterations=3)
        self.assertTrue(evidence["research_only"])
        self.assertTrue(evidence["off_consensus"])
        self.assertFalse(evidence["parameter_set_selected"])
        self.assertFalse(evidence["bitcoin_core_modified"])
        self.assertFalse(evidence["native_windows_resource_portability_demonstrated"])
        self.assertEqual(evidence["candidate_order"], ["ML-DSA-44", "ML-DSA-65", "ML-DSA-87"])
        for row in evidence["benchmark_report"]["candidates"]:
            self.assertEqual(len(row["verify_wall_samples_ns"]), 3)
            self.assertEqual(len(row["verify_cpu_samples_ns"]), 3)
            self.assertGreater(row["process_max_rss_bytes"], 0)
            self.assertGreaterEqual(row["python_peak_alloc_bytes"], 0)
            self.assertTrue(row["correctness_oracle"]["valid_signature_accepted"])
            self.assertTrue(row["correctness_oracle"]["altered_message_rejected"])

    def test_fail_closed_on_candidate_order_drift(self):
        report = {
            "research_only": True, "endorsed_by_bitcoin_core": False, "mainnet_intended": False,
            "parameter_set_selected": False, "bitcoin_core_modified": False,
            "candidates": [{"candidate": "ML-DSA-87"}],
        }
        with patch.object(subject, "build_report", return_value=report):
            with self.assertRaisesRegex(ValueError, "candidate order"):
                subject.build_benchmark_evidence(3)


if __name__ == "__main__":
    unittest.main()
