import unittest

from scripts.benchmark_neutral_runtime import (
    build_report,
    deterministic_payload,
    neutral_work,
    parse_sizes,
    run_case,
)


class NeutralRuntimeBenchmarkTests(unittest.TestCase):
    def test_payload_is_deterministic_and_exact_size(self):
        self.assertEqual(deterministic_payload(64), deterministic_payload(64))
        self.assertEqual(len(deterministic_payload(257)), 257)

    def test_invalid_sizes_fail_closed(self):
        for value in (0, -1, True):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    deterministic_payload(value)

    def test_neutral_work_is_deterministic(self):
        payload = deterministic_payload(128)
        self.assertEqual(neutral_work(payload, 5), neutral_work(payload, 5))

    def test_case_reports_runtime_and_memory_without_crypto_claim(self):
        case = run_case(64, 2, 2)
        self.assertEqual(case["payload_bytes"], 64)
        self.assertEqual(case["iterations"], 2)
        self.assertEqual(case["rounds"], 2)
        self.assertGreaterEqual(case["median_duration_ns"], 0)
        self.assertGreaterEqual(case["max_peak_python_bytes"], 0)
        self.assertEqual(len(case["result_sha256_hex"]), 64)

    def test_report_keeps_decision_gates_open(self):
        report = build_report([64, 256], 2, 1)
        self.assertTrue(report["research_only"])
        self.assertFalse(report["endorsed_by_bitcoin_core"])
        self.assertFalse(report["mainnet_intended"])
        self.assertFalse(report["scheme_selected"])
        self.assertFalse(report["hybrid_semantics_selected"])
        self.assertEqual(report["network_scope"], "none-local-microbenchmark")
        self.assertIn("not cryptographic verification", report["warning"])

    def test_duplicate_sizes_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "unique"):
            build_report([64, 64], 1, 1)

    def test_parse_sizes(self):
        self.assertEqual(parse_sizes("64, 256,4096"), [64, 256, 4096])


if __name__ == "__main__":
    unittest.main()
