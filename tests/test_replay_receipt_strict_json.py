import tempfile
import unittest
from pathlib import Path

try:
    from scripts.validate_replay_receipt import load_replay_receipt
except (ImportError, ModuleNotFoundError):
    raise unittest.SkipTest("requires replay receipt validator")


class T(unittest.TestCase):
    def test_nonfinite_json_constants_fail_closed_at_load(self):
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(token=token), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "receipt.json"
                path.write_text('{"schema_version":' + token + '}', encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "non-finite JSON constant"):
                    load_replay_receipt(path)


if __name__ == "__main__":
    unittest.main()
