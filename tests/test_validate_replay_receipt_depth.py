import tempfile
import unittest
from pathlib import Path

from scripts.validate_replay_receipt import MAX_RECEIPT_BYTES, load_replay_receipt


class T(unittest.TestCase):
    def test_excessive_json_nesting_fails_closed(self):
        # Stay well below the byte limit while exceeding CPython's normal JSON
        # recursion depth. The loader must convert parser recursion failure into
        # the same explicit fail-closed ValueError contract used elsewhere.
        depth = 2_000
        encoded = ("[" * depth + "0" + "]" * depth).encode("ascii")
        self.assertLess(len(encoded), MAX_RECEIPT_BYTES)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "receipt.json"
            path.write_bytes(encoded)
            with self.assertRaisesRegex(ValueError, "JSON nesting is too deep"):
                load_replay_receipt(path)


if __name__ == "__main__":
    unittest.main()
