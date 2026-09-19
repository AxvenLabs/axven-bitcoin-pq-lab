import tempfile
import unittest
from pathlib import Path

from scripts.validate_replay_receipt import MAX_JSON_NESTING, load_replay_receipt


class T(unittest.TestCase):
    def test_exact_depth_limit_is_accepted_by_loader(self):
        encoded = "[" * MAX_JSON_NESTING + "0" + "]" * MAX_JSON_NESTING
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "receipt.json"
            path.write_text(encoded, encoding="utf-8")
            loaded = load_replay_receipt(path)

        depth = 0
        value = loaded
        while isinstance(value, list):
            self.assertEqual(len(value), 1)
            depth += 1
            value = value[0]
        self.assertEqual(depth, MAX_JSON_NESTING)
        self.assertEqual(value, 0)

    def test_one_level_over_depth_limit_fails_closed(self):
        depth = MAX_JSON_NESTING + 1
        encoded = "[" * depth + "0" + "]" * depth
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "receipt.json"
            path.write_text(encoded, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "replay receipt JSON nesting is too deep"):
                load_replay_receipt(path)


if __name__ == "__main__":
    unittest.main()
