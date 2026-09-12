import json
import pathlib
import tempfile
import unittest

from scripts.verify_upstream_pin import load_pin


ROOT = pathlib.Path(__file__).resolve().parents[1]
PIN = ROOT / "upstream" / "bitcoin-core.json"


class UpstreamPinTests(unittest.TestCase):
    def test_committed_pin_has_expected_identity(self):
        pin = load_pin(PIN)
        self.assertEqual(pin["tag"], "v31.1")
        self.assertEqual(
            pin["tag_object_sha"],
            "bfa6a4b79cd4c1562fd32857e3147763efae37fb",
        )
        self.assertEqual(
            pin["commit_sha"],
            "9be056a8a72b624dae9623b2f7bded92c2a21c91",
        )
        self.assertIn("regtest", pin["purpose"].lower())

    def test_rejects_malformed_object_ids(self):
        bad = {
            "repository": "https://github.com/bitcoin/bitcoin.git",
            "tag": "v31.1",
            "tag_object_sha": "not-a-sha",
            "commit_sha": "0" * 40,
            "purpose": "research-only regtest baseline",
        }
        with tempfile.TemporaryDirectory() as tmp:
            path = pathlib.Path(tmp) / "pin.json"
            path.write_text(json.dumps(bad), encoding="utf-8")
            with self.assertRaises(ValueError):
                load_pin(path)


if __name__ == "__main__":
    unittest.main()
