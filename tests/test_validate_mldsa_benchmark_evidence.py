import copy
import unittest

from scripts.benchmark_mldsa_candidates import build_report
from scripts.validate_mldsa_benchmark_evidence import (
    canonical_evidence_sha256,
    validate_report,
)


class MldsaBenchmarkEvidenceValidatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = build_report(iterations=3)

    def test_current_report_validates(self):
        validate_report(self.report)

    def test_canonical_digest_is_stable_for_key_order(self):
        digest = canonical_evidence_sha256(self.report)
        reordered = dict(reversed(list(self.report.items())))
        self.assertEqual(digest, canonical_evidence_sha256(reordered))
        self.assertEqual(len(digest), 64)

    def test_timing_aggregate_tamper_fails_closed(self):
        mutated = copy.deepcopy(self.report)
        mutated["candidates"][0]["verify_wall_p95_ns"] += 1
        with self.assertRaisesRegex(ValueError, "p95 mismatch"):
            validate_report(mutated)

    def test_timing_sample_tamper_fails_closed(self):
        mutated = copy.deepcopy(self.report)
        mutated["candidates"][1]["verify_cpu_samples_ns"][0] = 0
        with self.assertRaisesRegex(ValueError, "positive integers"):
            validate_report(mutated)

    def test_parameter_selection_fails_closed(self):
        mutated = copy.deepcopy(self.report)
        mutated["parameter_set_selected"] = True
        with self.assertRaisesRegex(ValueError, "parameter_set_selected"):
            validate_report(mutated)

    def test_candidate_removal_fails_closed(self):
        mutated = copy.deepcopy(self.report)
        mutated["candidates"] = mutated["candidates"][:-1]
        with self.assertRaisesRegex(ValueError, "candidate set"):
            validate_report(mutated)

    def test_correctness_oracle_tamper_fails_closed(self):
        mutated = copy.deepcopy(self.report)
        mutated["candidates"][2]["correctness_oracle"]["altered_message_rejected"] = False
        with self.assertRaisesRegex(ValueError, "altered-message oracle failed"):
            validate_report(mutated)


if __name__ == "__main__":
    unittest.main()
