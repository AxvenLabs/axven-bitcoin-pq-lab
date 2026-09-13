import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_regtest_lab.py"
COMPARATOR = ROOT / "scripts" / "compare_regtest_baselines.py"


class RegtestIsolationTests(unittest.TestCase):
    def test_experiment_on_fails_closed_before_touching_bitcoin(self):
        result = subprocess.run(
            [sys.executable, str(RUNNER), "--mode", "on", "--bin-dir", "/definitely/missing"],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("experimental mode is intentionally unavailable", result.stderr)
        self.assertIn("no PQ scheme", result.stderr)

    def test_equivalence_comparator_accepts_behavioral_match_with_different_txid(self):
        base = {
            "blocks": 102,
            "chain": "regtest",
            "confirmations": 1,
            "research_only": True,
            "transaction_created_and_mined": True,
            "upstream_version": 310100,
        }
        with tempfile.TemporaryDirectory() as tmp:
            left = Path(tmp) / "left.json"
            right = Path(tmp) / "right.json"
            left.write_text(json.dumps({**base, "txid": "a" * 64}), encoding="utf-8")
            right.write_text(json.dumps({**base, "txid": "b" * 64}), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(COMPARATOR), str(left), str(right)],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["equivalent"])

    def test_equivalence_comparator_rejects_behavioral_divergence(self):
        with tempfile.TemporaryDirectory() as tmp:
            left = Path(tmp) / "left.json"
            right = Path(tmp) / "right.json"
            left.write_text(json.dumps({"chain": "regtest", "blocks": 102}), encoding="utf-8")
            right.write_text(json.dumps({"chain": "regtest", "blocks": 103}), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(COMPARATOR), str(left), str(right)],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("diverged", result.stderr)


if __name__ == "__main__":
    unittest.main()
