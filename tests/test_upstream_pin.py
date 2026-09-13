import json
import pathlib
import tempfile
import unittest

from scripts.verify_upstream_pin import load_pin


ROOT = pathlib.Path(__file__).resolve().parents[1]
PIN = ROOT / "upstream" / "bitcoin-core.json"


def valid_pin(**overrides):
    value = {
        "repository": "https://github.com/bitcoin/bitcoin.git",
        "tag": "v31.1",
        "tag_object_sha": "bfa6a4b79cd4c1562fd32857e3147763efae37fb",
        "commit_sha": "9be056a8a72b624dae9623b2f7bded92c2a21c91",
        "purpose": "research-only regtest baseline",
    }
    value.update(overrides)
    return value


def write_and_load(value):
    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp) / "pin.json"
        path.write_text(json.dumps(value), encoding="utf-8")
        return load_pin(path)


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
        with self.assertRaises(ValueError):
            write_and_load(valid_pin(tag_object_sha="not-a-sha"))

    def test_rejects_noncanonical_repository(self):
        with self.assertRaisesRegex(ValueError, "canonical Bitcoin Core upstream"):
            write_and_load(valid_pin(repository="https://example.invalid/bitcoin.git"))

    def test_rejects_unsafe_tag(self):
        with self.assertRaisesRegex(ValueError, "unsafe or unsupported"):
            write_and_load(valid_pin(tag="../../heads/main"))

    def test_rejects_non_string_fields(self):
        with self.assertRaisesRegex(ValueError, "tag must be a string"):
            write_and_load(valid_pin(tag=31))

    def test_rejects_unexpected_fields(self):
        with self.assertRaisesRegex(ValueError, "unexpected fields"):
            write_and_load({**valid_pin(), "mirror": "https://example.invalid"})

    def test_requires_explicit_research_regtest_purpose(self):
        with self.assertRaisesRegex(ValueError, "research and regtest"):
            write_and_load(valid_pin(purpose="production deployment"))


if __name__ == "__main__":
    unittest.main()
