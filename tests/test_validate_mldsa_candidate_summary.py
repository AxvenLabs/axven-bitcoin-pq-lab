import copy
import unittest

from scripts.validate_mldsa_candidate_summary import canonical_digest, validate_summary


def _summary():
    sizes = {
        "ML-DSA-44": (1312, 2420),
        "ML-DSA-65": (1952, 3309),
        "ML-DSA-87": (2592, 4627),
    }
    candidates = []
    for name in ("ML-DSA-44", "ML-DSA-65", "ML-DSA-87"):
        pk, sig = sizes[name]
        batches = []
        for size in (1, 10, 100):
            batches.append(
                {
                    "batch_size": size,
                    "wall_total_median_ns": 120 * size,
                    "wall_median_ns_per_verification": 120,
                    "cpu_total_median_ns": 100 * size,
                    "cpu_median_ns_per_verification": 100,
                }
            )
        candidates.append(
            {
                "candidate": name,
                "public_key_bytes": pk,
                "signature_bytes": sig,
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
        "candidate_family": "ML-DSA",
        "hybrid_research_semantics": "classical-and-pq",
        "parameter_set_selected": False,
        "deployment_winner_selected": False,
        "ranking_performed": False,
        "candidates": candidates,
    }


class CandidateSummaryValidatorTests(unittest.TestCase):
    def test_valid_summary_and_digest_are_deterministic(self):
        first = _summary()
        second = copy.deepcopy(first)
        validate_summary(first)
        self.assertEqual(canonical_digest(first), canonical_digest(second))

    def test_parameter_selection_and_ranking_fail_closed(self):
        for key, value in (
            ("parameter_set_selected", True),
            ("deployment_winner_selected", True),
            ("ranking_performed", True),
        ):
            with self.subTest(key=key):
                summary = _summary()
                summary[key] = value
                with self.assertRaises(ValueError):
                    validate_summary(summary)

    def test_forbidden_selection_fields_fail_closed_at_any_depth(self):
        summary = _summary()
        summary["candidates"][0]["winner"] = True
        with self.assertRaises(ValueError):
            validate_summary(summary)

    def test_candidate_order_and_fips_sizes_are_bound(self):
        summary = _summary()
        summary["candidates"].reverse()
        with self.assertRaises(ValueError):
            validate_summary(summary)

        summary = _summary()
        summary["candidates"][0]["signature_bytes"] += 1
        with self.assertRaises(ValueError):
            validate_summary(summary)

    def test_derived_timings_must_match_integer_derivation(self):
        summary = _summary()
        summary["candidates"][1]["batches"][1]["wall_median_ns_per_verification"] += 1
        with self.assertRaises(ValueError):
            validate_summary(summary)

    def test_negative_rss_and_schema_downgrade_fail_closed(self):
        summary = _summary()
        summary["candidates"][2]["process_max_rss_delta_bytes"] = -1
        with self.assertRaises(ValueError):
            validate_summary(summary)

        summary = _summary()
        summary["schema_version"] = 0
        with self.assertRaises(ValueError):
            validate_summary(summary)


if __name__ == "__main__":
    unittest.main()
