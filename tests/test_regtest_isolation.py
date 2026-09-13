import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run_regtest_lab.py"
COMPARATOR = ROOT / "scripts" / "compare_regtest_baselines.py"


def baseline(**overrides):
    value = {
        "blocks": 102,
        "chain": "regtest",
        "confirmations": 1,
        "research_only": True,
        "transaction_created_and_mined": True,
        "txid": "a" * 64,
        "upstream_version": 310100,
    }
    value.update(overrides)
    return value


def compare(left_value, right_value):
    with tempfile.TemporaryDirectory() as tmp:
        left = Path(tmp) / "left.json"
        right = Path(tmp) / "right.json"
        left.write_text(json.dumps(left_value), encoding="utf-8")
        right.write_text(json.dumps(right_value), encoding="utf-8")
        return subprocess.run(
            [sys.executable, str(COMPARATOR), str(left), str(right)],
            text=True,
            capture_output=True,
            check=False,
        )


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
        result = compare(baseline(), baseline(txid="b" * 64))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["equivalent"])

    def test_equivalence_comparator_rejects_behavioral_divergence(self):
        result = compare(baseline(), baseline(blocks=103))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("diverged", result.stderr)

    def test_equivalence_comparator_rejects_missing_field_on_both_sides(self):
        left = baseline()
        right = baseline(txid="b" * 64)
        del left["upstream_version"]
        del right["upstream_version"]
        result = compare(left, right)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("missing required fields: upstream_version", result.stderr)

    def test_equivalence_comparator_rejects_wrong_network_even_when_equal(self):
        result = compare(baseline(chain="main"), baseline(chain="main", txid="b" * 64))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("chain must be regtest", result.stderr)

    def test_equivalence_comparator_rejects_invalid_txid_shape(self):
        result = compare(baseline(txid="not-a-txid"), baseline(txid="also-invalid"))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("txid must be a 64-character hexadecimal string", result.stderr)

    def test_equivalence_comparator_rejects_false_research_marker(self):
        result = compare(
            baseline(research_only=False),
            baseline(research_only=False, txid="b" * 64),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("research_only must be true", result.stderr)


if __name__ == "__main__":
    unittest.main()
