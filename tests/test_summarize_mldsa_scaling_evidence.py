import copy
import unittest

from scripts.summarize_mldsa_scaling_evidence import _assert_candidate_neutral, summarize


def _report():
    sizes = {
        "ML-DSA-44": (1312, 2420),
        "ML-DSA-65": (1952, 3309),
        "ML-DSA-87": (2592, 4627),
    }
    candidates = []
    for name in ("ML-DSA-44", "ML-DSA-65", "ML-DSA-87"):
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
        public_key_bytes, signature_bytes = sizes[name]
        candidates.append(
            {
                "candidate": name,
                "public_key_bytes": public_key_bytes,
                "signature_bytes": signature_bytes,
                "process_max_rss_bytes": 123456,
                "process_max_rss_delta_bytes": 4096,
                "batches": batches,
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
    }


class CandidateNeutralSummaryTests(unittest.TestCase):
    def test_summary_is_deterministic_and_preserves_candidate_order(self):
        first = summarize(_report())
        second = summarize(copy.deepcopy(_report()))
        self.assertEqual(first, second)
        self.assertEqual(
            [row["candidate"] for row in first["candidates"]],
            ["ML-DSA-44", "ML-DSA-65", "ML-DSA-87"],
        )
        self.assertFalse(first["ranking_performed"])
        self.assertFalse(first["parameter_set_selected"])
        self.assertFalse(first["deployment_winner_selected"])

    def test_normalized_per_verification_values_are_derived_only(self):
        summary = summarize(_report())
        first_batch = summary["candidates"][0]["batches"][1]
        self.assertEqual(first_batch["batch_size"], 10)
        self.assertEqual(first_batch["wall_median_ns_per_verification"], 110)
        self.assertEqual(first_batch["cpu_median_ns_per_verification"], 100)

    def test_forbidden_selection_fields_fail_closed(self):
        for field in ("winner", "recommended", "rank", "score", "preferred"):
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    _assert_candidate_neutral({field: "ML-DSA-44"})

    def test_invalid_source_evidence_is_rejected_before_summary(self):
        report = _report()
        report["deployment_winner_selected"] = True
        with self.assertRaises(ValueError):
            summarize(report)


if __name__ == "__main__":
    unittest.main()
