import unittest

from scripts.benchmark_verifier_harness import (
    VerificationSample,
    benchmark_verifier,
    calibration_verifier,
)


class VerifierHarnessTests(unittest.TestCase):
    def setUp(self):
        self.sample = VerificationSample(b"m" * 32, b"s" * 64, b"k" * 32)

    def test_report_is_explicitly_research_only_and_scheme_neutral(self):
        report = benchmark_verifier(calibration_verifier, self.sample, iterations=3)
        self.assertTrue(report["research_only"])
        self.assertFalse(report["endorsed_by_bitcoin_core"])
        self.assertFalse(report["mainnet_intended"])
        self.assertFalse(report["scheme_selected"])
        self.assertFalse(report["hybrid_semantics_selected"])
        self.assertEqual(report["measurement_scope"], "generic-verifier-call-harness")
        self.assertIn("not PQ signature verification costs", report["warning"])

    def test_lengths_are_reported_without_interpreting_scheme(self):
        report = benchmark_verifier(calibration_verifier, self.sample, iterations=2)
        self.assertEqual(report["message_bytes"], 32)
        self.assertEqual(report["signature_bytes"], 64)
        self.assertEqual(report["public_key_bytes"], 32)

    def test_invalid_iterations_fail_closed(self):
        for value in (0, -1, True):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    benchmark_verifier(calibration_verifier, self.sample, value)

    def test_non_callable_verifier_fails_closed(self):
        with self.assertRaises(ValueError):
            benchmark_verifier(None, self.sample, 1)  # type: ignore[arg-type]

    def test_false_verifier_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "literal True"):
            benchmark_verifier(lambda _m, _s, _k: False, self.sample, 1)

    def test_calibration_verifier_is_non_cryptographic_and_deterministic(self):
        self.assertTrue(calibration_verifier(b"m", b"s", b"k"))
        self.assertFalse(calibration_verifier(b"", b"s", b"k"))


if __name__ == "__main__":
    unittest.main()
