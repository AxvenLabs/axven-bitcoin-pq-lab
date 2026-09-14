import unittest

try:
    from scripts.benchmark_mldsa_candidates import (
        CANDIDATES,
        EXPECTED_SIZES,
        _p95,
        benchmark_candidate,
        build_report,
    )
    from scripts.benchmark_mldsa_scaling import (
        DEFAULT_BATCH_SIZES,
        benchmark_candidate_scaling,
        build_report as build_scaling_report,
    )
except ModuleNotFoundError as exc:
    if exc.name == "cryptography":
        raise unittest.SkipTest("cryptography benchmark dependency is exercised in dedicated CI job")
    raise


class MldsaCandidateBenchmarkTests(unittest.TestCase):
    def test_report_is_research_only_and_does_not_select_winner(self):
        report = build_report(iterations=3)
        self.assertEqual(report["schema_version"], 3)
        self.assertTrue(report["research_only"])
        self.assertFalse(report["mainnet_intended"])
        self.assertFalse(report["parameter_set_selected"])
        self.assertFalse(report["deployment_winner_selected"])
        self.assertFalse(report["bitcoin_core_modified"])
        self.assertFalse(report["bitcoin_script_semantics_selected"])
        self.assertFalse(report["consensus_change_selected"])
        self.assertTrue(report["raw_sample_evidence"])
        self.assertEqual(report["percentile_method"], "nearest-rank")
        self.assertEqual(report["candidate_family"], "ML-DSA")
        self.assertEqual(report["hybrid_research_semantics"], "classical-and-pq")
        self.assertEqual({row["candidate"] for row in report["candidates"]}, set(CANDIDATES))

    def test_each_candidate_matches_fips204_sizes_and_has_recomputable_measurements(self):
        report = build_report(iterations=3)
        for row in report["candidates"]:
            with self.subTest(candidate=row["candidate"]):
                expected = EXPECTED_SIZES[row["candidate"]]
                self.assertEqual(row["public_key_bytes"], expected["public_key_bytes"])
                self.assertEqual(row["signature_bytes"], expected["signature_bytes"])
                wall = row["verify_wall_samples_ns"]
                cpu = row["verify_cpu_samples_ns"]
                self.assertEqual(len(wall), row["iterations"])
                self.assertEqual(len(cpu), row["iterations"])
                self.assertTrue(all(isinstance(value, int) and value > 0 for value in wall))
                self.assertTrue(all(isinstance(value, int) and value > 0 for value in cpu))
                self.assertEqual(row["verify_wall_min_ns"], min(wall))
                self.assertEqual(row["verify_wall_max_ns"], max(wall))
                self.assertEqual(row["verify_wall_p95_ns"], _p95(wall))
                self.assertEqual(row["verify_cpu_min_ns"], min(cpu))
                self.assertEqual(row["verify_cpu_max_ns"], max(cpu))
                self.assertEqual(row["verify_cpu_p95_ns"], _p95(cpu))
                self.assertGreater(row["verify_wall_median_ns"], 0)
                self.assertGreater(row["verify_cpu_median_ns"], 0)
                self.assertGreaterEqual(row["python_peak_alloc_bytes"], 0)
                self.assertGreater(row["process_max_rss_bytes"], 0)
                self.assertTrue(row["correctness_oracle"]["valid_signature_accepted"])
                self.assertTrue(row["correctness_oracle"]["altered_message_rejected"])

    def test_nearest_rank_p95_contract(self):
        self.assertEqual(_p95([1, 2, 3]), 3)
        self.assertEqual(_p95(list(range(1, 21))), 19)
        with self.assertRaises(ValueError):
            _p95([1, 2])

    def test_expected_size_contract_covers_all_candidates(self):
        self.assertEqual(set(EXPECTED_SIZES), set(CANDIDATES))
        self.assertEqual(EXPECTED_SIZES["ML-DSA-44"], {"public_key_bytes": 1312, "signature_bytes": 2420})
        self.assertEqual(EXPECTED_SIZES["ML-DSA-65"], {"public_key_bytes": 1952, "signature_bytes": 3309})
        self.assertEqual(EXPECTED_SIZES["ML-DSA-87"], {"public_key_bytes": 2592, "signature_bytes": 4627})

    def test_invalid_inputs_fail_closed(self):
        with self.assertRaises(ValueError):
            benchmark_candidate("ML-DSA-44", 2, b"message")
        with self.assertRaises(ValueError):
            benchmark_candidate("not-a-candidate", 3, b"message")
        with self.assertRaises(ValueError):
            benchmark_candidate("ML-DSA-44", 3, b"")

    def test_scaling_report_preserves_decision_gates_and_all_candidates(self):
        report = build_scaling_report(repetitions=3, batch_sizes=(1, 2))
        self.assertTrue(report["research_only"])
        self.assertFalse(report["mainnet_intended"])
        self.assertFalse(report["parameter_set_selected"])
        self.assertFalse(report["deployment_winner_selected"])
        self.assertFalse(report["bitcoin_core_modified"])
        self.assertFalse(report["bitcoin_script_semantics_selected"])
        self.assertFalse(report["output_commitment_semantics_selected"])
        self.assertFalse(report["consensus_change_selected"])
        self.assertTrue(report["correctness_oracle_separate"])
        self.assertEqual([row["candidate"] for row in report["candidates"]], list(CANDIDATES))

    def test_scaling_samples_are_recomputable_and_size_bound(self):
        row = benchmark_candidate_scaling("ML-DSA-44", repetitions=3, batch_sizes=(1, 2))
        self.assertEqual(row["public_key_bytes"], EXPECTED_SIZES["ML-DSA-44"]["public_key_bytes"])
        self.assertEqual(row["signature_bytes"], EXPECTED_SIZES["ML-DSA-44"]["signature_bytes"])
        self.assertGreater(row["process_max_rss_bytes"], 0)
        self.assertGreaterEqual(row["process_max_rss_delta_bytes"], 0)
        self.assertEqual([batch["batch_size"] for batch in row["batches"]], [1, 2])
        for batch in row["batches"]:
            wall = batch["wall_total_samples_ns"]
            cpu = batch["cpu_total_samples_ns"]
            self.assertEqual(len(wall), 3)
            self.assertEqual(len(cpu), 3)
            self.assertTrue(all(type(v) is int and v > 0 for v in wall))
            self.assertTrue(all(type(v) is int and v > 0 for v in cpu))
            self.assertEqual(batch["wall_total_median_ns"], int(__import__("statistics").median(wall)))
            self.assertEqual(batch["cpu_total_median_ns"], int(__import__("statistics").median(cpu)))
            self.assertGreaterEqual(batch["wall_total_p95_ns"], batch["wall_total_median_ns"])
            self.assertGreaterEqual(batch["cpu_total_p95_ns"], batch["cpu_total_median_ns"])

    def test_scaling_inputs_fail_closed(self):
        self.assertEqual(DEFAULT_BATCH_SIZES, (1, 10, 100))
        for bad in ((), (0,), (2, 1), (1, 1), (True,)):
            with self.subTest(batch_sizes=bad):
                with self.assertRaises(ValueError):
                    build_scaling_report(repetitions=3, batch_sizes=bad)
        with self.assertRaises(ValueError):
            benchmark_candidate_scaling("ML-DSA-44", repetitions=2)
        with self.assertRaises(ValueError):
            benchmark_candidate_scaling("not-a-candidate", repetitions=3)


if __name__ == "__main__":
    unittest.main()
