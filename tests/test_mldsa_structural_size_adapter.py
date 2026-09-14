import copy
import unittest

from scripts.mldsa_structural_size_adapter import build_report, validate_report


class MldsaStructuralSizeAdapterTests(unittest.TestCase):
    def test_report_validates_and_preserves_all_candidates(self):
        report = build_report()
        validate_report(report)
        self.assertEqual(
            [row["candidate"] for row in report["candidates"]],
            ["ML-DSA-44", "ML-DSA-65", "ML-DSA-87"],
        )
        self.assertFalse(report["parameter_set_selected"])
        self.assertFalse(report["deployment_winner_selected"])
        self.assertFalse(report["bitcoin_script_semantics_selected"])
        self.assertFalse(report["output_commitment_semantics_selected"])
        self.assertFalse(report["consensus_change_selected"])

    def test_rejects_candidate_order_drift(self):
        report = build_report()
        report["candidates"] = list(reversed(report["candidates"]))
        with self.assertRaisesRegex(ValueError, "candidate order drift"):
            validate_report(report)

    def test_rejects_silent_parameter_selection(self):
        report = build_report()
        report["parameter_set_selected"] = True
        with self.assertRaisesRegex(ValueError, "protected field drift"):
            validate_report(report)

    def test_rejects_script_or_commitment_selection(self):
        for field in ("bitcoin_script_semantics_selected", "output_commitment_semantics_selected"):
            report = build_report()
            report[field] = True
            with self.assertRaisesRegex(ValueError, "protected field drift"):
                validate_report(report)

    def test_rejects_tampered_size_evidence(self):
        report = build_report()
        report["candidates"][1]["signature"]["payload_bytes"] += 1
        with self.assertRaisesRegex(ValueError, "structural size drift"):
            validate_report(report)

    def test_validation_does_not_mutate_report(self):
        report = build_report()
        original = copy.deepcopy(report)
        validate_report(report)
        self.assertEqual(report, original)


if __name__ == "__main__":
    unittest.main()
