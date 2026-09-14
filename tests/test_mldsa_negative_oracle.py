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
        self.assertEqual(report["schema_version"], 2)
        self.assertEqual(
            [row["candidate"] for row in report["candidates"]],
            ["ML-DSA-44", "ML-DSA-65", "ML-DSA-87"],
        )
        all_candidates = [row["candidate"] for row in report["candidates"]]
        for row in report["candidates"]:
            self.assertTrue(row["valid_signature_accepted"])
            self.assertTrue(row["altered_message_rejected"])
            self.assertTrue(row["corrupted_signature_rejected"])
            self.assertTrue(row["wrong_public_key_rejected"])
            self.assertTrue(row["truncated_signature_rejected"])
            self.assertTrue(row["oversized_signature_rejected"])
            expected_others = [name for name in all_candidates if name != row["candidate"]]
            self.assertEqual(
                list(row["cross_candidate_signatures_rejected"]), expected_others
            )
            self.assertTrue(all(row["cross_candidate_signatures_rejected"].values()))

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

    def test_rejects_cross_candidate_matrix_drift(self):
        report = build_oracle_report()
        row = report["candidates"][0]
        row["cross_candidate_signatures_rejected"] = dict(
            reversed(list(row["cross_candidate_signatures_rejected"].items()))
        )
        with self.assertRaisesRegex(ValueError, "cross-candidate matrix drift"):
            validate_oracle_report(report)

    def test_rejects_cross_candidate_acceptance(self):
        report = build_oracle_report()
        row = report["candidates"][0]
        other = next(iter(row["cross_candidate_signatures_rejected"]))
        row["cross_candidate_signatures_rejected"][other] = False
        with self.assertRaisesRegex(ValueError, "cross-candidate rejection failed"):
            validate_oracle_report(report)

    def test_rejects_schema_downgrade(self):
        report = build_oracle_report()
        report["schema_version"] = 1
        with self.assertRaisesRegex(ValueError, "schema_version"):
            validate_oracle_report(report)

    def test_validation_does_not_mutate_report(self):
        report = build_oracle_report()
        original = copy.deepcopy(report)
        validate_oracle_report(report)
        self.assertEqual(report, original)


if __name__ == "__main__":
    unittest.main()
