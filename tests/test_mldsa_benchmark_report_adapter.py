import copy
import unittest

from scripts.mldsa_benchmark_report_adapter import adapt_report


ENV = {
    "os": "linux",
    "architecture": "x86_64",
    "cpu_model": "test-cpu",
    "logical_cpus": 4,
    "ram_bytes": 8 * 1024**3,
    "runtime": "python-test",
}


def _raw_report() -> dict:
    rows = []
    for offset, name in enumerate(("ML-DSA-44", "ML-DSA-65", "ML-DSA-87")):
        wall = [100 + offset, 110 + offset, 120 + offset]
        cpu = [90 + offset, 100 + offset, 110 + offset]
        rows.append(
            {
                "candidate": name,
                "iterations": 3,
                "verify_wall_samples_ns": wall,
                "verify_wall_median_ns": wall[1],
                "verify_wall_p95_ns": wall[2],
                "verify_cpu_samples_ns": cpu,
                "verify_cpu_median_ns": cpu[1],
                "verify_cpu_p95_ns": cpu[2],
            }
        )
    return {
        "research_only": True,
        "candidate_family": "ML-DSA",
        "hybrid_research_semantics": "classical-and-pq",
        "parameter_set_selected": False,
        "deployment_winner_selected": False,
        "bitcoin_core_modified": False,
        "bitcoin_script_semantics_selected": False,
        "consensus_change_selected": False,
        "candidates": rows,
    }


def _adapt(raw: dict) -> list[dict]:
    return adapt_report(
        raw,
        source_identity="git:deadbeef",
        timestamp_utc="2026-09-14T00:00:00Z",
        environment=ENV,
    )


class MldsaBenchmarkReportAdapterTests(unittest.TestCase):
    def test_adapts_all_candidates_and_metrics_to_valid_generic_reports(self):
        reports = _adapt(_raw_report())
        self.assertEqual(len(reports), 6)
        self.assertEqual(
            [report["benchmark_name"] for report in reports],
            [
                "ML-DSA-44-verify-wall",
                "ML-DSA-44-verify-cpu",
                "ML-DSA-65-verify-wall",
                "ML-DSA-65-verify-cpu",
                "ML-DSA-87-verify-wall",
                "ML-DSA-87-verify-cpu",
            ],
        )
        self.assertTrue(all(report["research_only"] is True for report in reports))
        self.assertTrue(all(report["warmups"] == 0 for report in reports))

    def test_rejects_silent_parameter_set_selection(self):
        raw = _raw_report()
        raw["parameter_set_selected"] = True
        with self.assertRaisesRegex(ValueError, "parameter_set_selected"):
            _adapt(raw)

    def test_rejects_or_hybrid_semantics(self):
        raw = _raw_report()
        raw["hybrid_research_semantics"] = "classical-or-pq"
        with self.assertRaisesRegex(ValueError, "hybrid semantics"):
            _adapt(raw)

    def test_rejects_candidate_set_or_order_drift(self):
        raw = _raw_report()
        raw["candidates"] = list(reversed(raw["candidates"]))
        with self.assertRaisesRegex(ValueError, "candidate set/order"):
            _adapt(raw)

    def test_rejects_tampered_aggregate_against_raw_samples(self):
        raw = _raw_report()
        raw["candidates"][0]["verify_wall_median_ns"] += 1
        with self.assertRaisesRegex(ValueError, "median does not match raw samples"):
            _adapt(raw)

    def test_rejects_sample_count_mismatch(self):
        raw = _raw_report()
        raw["candidates"][0]["verify_cpu_samples_ns"] = [90, 100]
        with self.assertRaisesRegex(ValueError, "sample count must equal repetitions"):
            _adapt(raw)

    def test_input_is_not_mutated(self):
        raw = _raw_report()
        original = copy.deepcopy(raw)
        _adapt(raw)
        self.assertEqual(raw, original)


if __name__ == "__main__":
    unittest.main()
