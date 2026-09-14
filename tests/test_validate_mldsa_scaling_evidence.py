import copy
import unittest

from scripts.validate_mldsa_scaling_evidence import canonical_evidence_digest, validate_report


def _report():
    batches = []
    for size in (1, 10, 100):
        wall = [size * 100, size * 110, size * 120]
        cpu = [size * 90, size * 100, size * 110]
        batches.append(
            {
                "batch_size": size,
                "repetitions": 3,
                "wall_total_samples_ns": wall,
                "wall_total_median_ns": wall[1],
                "wall_total_p95_ns": wall[2],
                "cpu_total_samples_ns": cpu,
                "cpu_total_median_ns": cpu[1],
                "cpu_total_p95_ns": cpu[2],
            }
        )

    sizes = {
        "ML-DSA-44": (1312, 2420),
        "ML-DSA-65": (1952, 3309),
        "ML-DSA-87": (2592, 4627),
    }
    candidates = []
    for name in ("ML-DSA-44", "ML-DSA-65", "ML-DSA-87"):
        public_key_bytes, signature_bytes = sizes[name]
        candidates.append(
            {
                "candidate": name,
                "public_key_bytes": public_key_bytes,
                "signature_bytes": signature_bytes,
                "process_max_rss_bytes": 123456,
                "process_max_rss_delta_bytes": 4096,
                "batches": copy.deepcopy(batches),
            }
        )

    return {
        "schema_version": 1,
        "research_only": True,
        "endorsed_by_bitcoin_core": False,
        "mainnet_intended": False,
        "network_scope": "none-local-cryptographic-benchmark",
        "candidate_family": "ML-DSA",
        "hybrid_research_semantics": "classical-and-pq",
        "parameter_set_selected": False,
        "deployment_winner_selected": False,
        "bitcoin_core_modified": False,
        "bitcoin_script_semantics_selected": False,
        "output_commitment_semantics_selected": False,
        "consensus_change_selected": False,
        "correctness_oracle_separate": True,
        "batch_sizes": [1, 10, 100],
        "repetitions": 3,
        "candidates": candidates,
        "warning": "Research evidence only",
    }


class ScalingEvidenceValidatorTests(unittest.TestCase):
    def test_valid_report_and_digest_are_deterministic(self):
        report = _report()
        validate_report(report)
        first = canonical_evidence_digest(report)
        second = canonical_evidence_digest(copy.deepcopy(report))
        self.assertEqual(first, second)
        self.assertEqual(len(first), 64)

    def test_decision_gates_fail_closed(self):
        for field in (
            "parameter_set_selected",
            "deployment_winner_selected",
            "bitcoin_core_modified",
            "bitcoin_script_semantics_selected",
            "output_commitment_semantics_selected",
            "consensus_change_selected",
            "mainnet_intended",
        ):
            with self.subTest(field=field):
                report = _report()
                report[field] = True
                with self.assertRaises(ValueError):
                    validate_report(report)

    def test_candidate_family_and_hybrid_semantics_are_pinned_to_approved_research_hypothesis(self):
        for field, value in (("candidate_family", "other"), ("hybrid_research_semantics", "classical-or-pq")):
            report = _report()
            report[field] = value
            with self.assertRaises(ValueError):
                validate_report(report)

    def test_candidate_order_and_fips_sizes_fail_closed(self):
        report = _report()
        report["candidates"].reverse()
        with self.assertRaises(ValueError):
            validate_report(report)

        report = _report()
        report["candidates"][0]["signature_bytes"] += 1
        with self.assertRaises(ValueError):
            validate_report(report)

    def test_raw_samples_are_required_and_summary_must_recompute(self):
        report = _report()
        report["candidates"][0]["batches"][0]["wall_total_median_ns"] += 1
        with self.assertRaises(ValueError):
            validate_report(report)

        report = _report()
        report["candidates"][0]["batches"][0]["cpu_total_samples_ns"] = [1, 2]
        with self.assertRaises(ValueError):
            validate_report(report)

    def test_batch_shape_fails_closed(self):
        for bad in ([10, 1], [1, 1], [0, 1]):
            report = _report()
            report["batch_sizes"] = bad
            with self.assertRaises(ValueError):
                validate_report(report)

        report = _report()
        report["candidates"][1]["batches"].pop()
        with self.assertRaises(ValueError):
            validate_report(report)


if __name__ == "__main__":
    unittest.main()
