import json
import subprocess
import sys
import unittest

from scripts.benchmark_environment import collect_environment
from scripts.benchmark_report import validate_report


class BenchmarkEnvironmentTests(unittest.TestCase):
    def test_environment_matches_report_contract(self):
        env = collect_environment()
        report = {
            "schema_version": 1,
            "research_only": True,
            "benchmark_name": "environment-contract-smoke",
            "category": "methodology",
            "source_identity": "test-source-identity",
            "timestamp_utc": "2026-09-13T00:00:00Z",
            "unit": "microseconds",
            "environment": env,
            "warmups": 0,
            "repetitions": 3,
            "samples": [1, 2, 3],
            "median": 2.0,
            "p95": 3.0,
        }
        self.assertIs(validate_report(report), report)

    def test_environment_fields_are_nonempty_and_positive(self):
        env = collect_environment()
        for key in ("os", "architecture", "cpu_model", "runtime"):
            self.assertIsInstance(env[key], str)
            self.assertTrue(env[key].strip())
        for key in ("logical_cpus", "ram_bytes"):
            self.assertIsInstance(env[key], int)
            self.assertGreater(env[key], 0)

    def test_cli_emits_machine_readable_json(self):
        output = subprocess.check_output(
            [sys.executable, "-m", "scripts.benchmark_environment"], text=True
        )
        parsed = json.loads(output)
        self.assertEqual(parsed, collect_environment())


if __name__ == "__main__":
    unittest.main()
