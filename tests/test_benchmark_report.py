import unittest

from scripts.benchmark_report import summarize_samples, validate_report


def sample_report(**overrides):
    report = {
        "schema_version": 1,
        "research_only": True,
        "benchmark_name": "example structural measurement",
        "category": "structural",
        "source_identity": "bitcoin-core-v31.1-example",
        "timestamp_utc": "2026-09-13T08:00:00Z",
        "unit": "microseconds",
        "environment": {
            "os": "linux",
            "architecture": "x86_64",
            "cpu_model": "example-cpu",
            "logical_cpus": 8,
            "ram_bytes": 16 * 1024**3,
            "runtime": "python-example",
        },
        "warmups": 1,
        "repetitions": 5,
        "samples": [10, 20, 30, 40, 50],
        "median": 30.0,
        "p95": 50.0,
    }
    report.update(overrides)
    return report


class BenchmarkReportTests(unittest.TestCase):
    def test_summary_is_recomputable(self):
        self.assertEqual(summarize_samples([5, 1, 3, 2, 4]), {"median": 3.0, "p95": 5.0})

    def test_valid_report_passes(self):
        report = sample_report()
        self.assertIs(validate_report(report), report)

    def test_rejects_missing_research_label(self):
        with self.assertRaisesRegex(ValueError, "research_only"):
            validate_report(sample_report(research_only=False))

    def test_rejects_short_sample_set(self):
        with self.assertRaisesRegex(ValueError, "repetitions"):
            validate_report(sample_report(repetitions=2, samples=[1, 2], median=1.5, p95=2.0))

    def test_rejects_boolean_sample(self):
        with self.assertRaisesRegex(ValueError, "numeric"):
            validate_report(sample_report(samples=[10, 20, True, 40, 50]))

    def test_rejects_non_finite_sample(self):
        with self.assertRaisesRegex(ValueError, "finite"):
            validate_report(sample_report(samples=[10, 20, float("inf"), 40, 50]))

    def test_rejects_sample_count_mismatch(self):
        with self.assertRaisesRegex(ValueError, "sample count"):
            validate_report(sample_report(repetitions=4))

    def test_rejects_incorrect_derived_summary(self):
        with self.assertRaisesRegex(ValueError, "median"):
            validate_report(sample_report(median=31.0))

    def test_rejects_invalid_environment_numbers(self):
        env = dict(sample_report()["environment"])
        env["logical_cpus"] = True
        with self.assertRaisesRegex(ValueError, "positive integer"):
            validate_report(sample_report(environment=env))


if __name__ == "__main__":
    unittest.main()
