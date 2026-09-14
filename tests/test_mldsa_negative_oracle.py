import copy
import unittest

try:
    from scripts.mldsa_negative_oracle import build_oracle_report, validate_oracle_report
except ModuleNotFoundError as exc:
    if exc.name == "cryptography":
        raise unittest.SkipTest("cryptography correctness dependency is exercised in dedicated CI job")
    raise


class MldsaNegativeOracleTests(unittest.TestCase):
    def test_all_named_candidates_reject_negative_cases(self):
        report = build_oracle_report()
        validate_oracle_report(report)
        self.assertEqual(
            [row["candidate"] for row in report["candidates"]],
            ["ML-DSA-44", "ML-DSA-65", "ML-DSA-87"],
        )
        for row in report["candidates"]:
            self.assertTrue(row["valid_signature_accepted"])
            self.assertTrue(row["altered_message_rejected"])
            self.assertTrue(row["corrupted_signature_rejected"])
            self.assertTrue(row["wrong_public_key_rejected"])
            self.assertTrue(row["truncated_signature_rejected"])
            self.assertTrue(row["oversized_signature_rejected"])

    def test_rejects_silent_parameter_selection(self):
        report = build_oracle_report()
        report["parameter_set_selected"] = True
        with self.assertRaisesRegex(ValueError, "parameter_set_selected"):
            validate_oracle_report(report)

    def test_rejects_or_semantics(self):
        report = build_oracle_report()
        report["hybrid_research_semantics"] = "classical-or-pq"
        with self.assertRaisesRegex(ValueError, "hybrid_research_semantics"):
            validate_oracle_report(report)

    def test_rejects_candidate_drift(self):
        report = build_oracle_report()
        report["candidates"] = list(reversed(report["candidates"]))
        with self.assertRaisesRegex(ValueError, "candidate set/order"):
            validate_oracle_report(report)

    def test_rejects_tampered_negative_result(self):
        report = build_oracle_report()
        report["candidates"][0]["corrupted_signature_rejected"] = False
        with self.assertRaisesRegex(ValueError, "correctness oracle check failed"):
            validate_oracle_report(report)

    def test_validation_does_not_mutate_report(self):
        report = build_oracle_report()
        original = copy.deepcopy(report)
        validate_oracle_report(report)
        self.assertEqual(report, original)


if __name__ == "__main__":
    unittest.main()
