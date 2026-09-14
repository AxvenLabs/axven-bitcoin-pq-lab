import copy
import unittest

from scripts.validate_mldsa_benchmark_evidence import (
    canonical_evidence_sha256,
    validate_report,
)


def _candidate(name: str, public_key_bytes: int, signature_bytes: int) -> dict:
    wall = [100, 120, 140]
    cpu = [80, 90, 110]
    return {
        "candidate": name,
        "iterations": 3,
        "public_key_bytes": public_key_bytes,
        "signature_bytes": signature_bytes,
        "verify_wall_samples_ns": wall,
        "verify_wall_median_ns": 120,
        "verify_wall_p95_ns": 140,
        "verify_wall_min_ns": 100,
        "verify_wall_max_ns": 140,
        "verify_cpu_samples_ns": cpu,
        "verify_cpu_median_ns": 90,
        "verify_cpu_p95_ns": 110,
        "verify_cpu_min_ns": 80,
        "verify_cpu_max_ns": 110,
        "python_peak_alloc_bytes": 1024,
        "process_max_rss_bytes": 64 * 1024 * 1024,
        "process_max_rss_delta_bytes": 4096,
        "correctness_oracle": {
            "valid_signature_accepted": True,
            "altered_message_rejected": True,
        },
    }


def _synthetic_report() -> dict:
    return {
        "schema_version": 3,
        "research_only": True,
        "endorsed_by_bitcoin_core": False,
        "mainnet_intended": False,
        "candidate_family": "ML-DSA",
        "hybrid_research_semantics": "classical-and-pq",
        "parameter_set_selected": False,
        "deployment_winner_selected": False,
        "bitcoin_core_modified": False,
        "bitcoin_script_semantics_selected": False,
        "consensus_change_selected": False,
        "raw_sample_evidence": True,
        "percentile_method": "nearest-rank",
        "cryptography_version": "synthetic-fixture",
        "openssl_version": "synthetic-fixture",
        "python_version": "synthetic-fixture",
        "platform": "synthetic-fixture",
        "message_bytes": 32,
        "candidates": [
            _candidate("ML-DSA-44", 1312, 2420),
            _candidate("ML-DSA-65", 1952, 3309),
            _candidate("ML-DSA-87", 2592, 4627),
        ],
    }


class MldsaBenchmarkEvidenceValidatorTests(unittest.TestCase):
    def setUp(self):
        self.report = _synthetic_report()

    def test_independent_synthetic_report_validates_without_crypto_backend(self):
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
