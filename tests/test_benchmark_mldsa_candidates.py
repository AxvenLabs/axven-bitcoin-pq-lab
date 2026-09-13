import json
import tempfile
import unittest
from pathlib import Path

from scripts.benchmark_mldsa_candidates import CANDIDATES, SOURCE_COMMIT, load_vector


class MldsaCandidateBenchmarkTests(unittest.TestCase):
    def _write_vector(self, candidate: str, *, pk_len: int | None = None, sig_len: int | None = None):
        spec = CANDIDATES[candidate]
        data = {
            "algorithm": candidate,
            "testGroups": [
                {
                    "publicKey": (b"p" * (pk_len if pk_len is not None else spec["public_key_bytes"])).hex(),
                    "tests": [
                        {
                            "result": "valid",
                            "sig": (b"s" * (sig_len if sig_len is not None else spec["signature_bytes"])).hex(),
                            "msg": b"message".hex(),
                            "ctx": b"axven-lab".hex(),
                        }
                    ],
                }
            ],
        }
        td = tempfile.TemporaryDirectory()
        path = Path(td.name) / "vector.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return td, path

    def test_all_three_named_candidates_remain_measurements_not_selection(self):
        self.assertEqual(tuple(CANDIDATES), ("ML-DSA-44", "ML-DSA-65", "ML-DSA-87"))
        self.assertEqual(CANDIDATES["ML-DSA-44"]["public_key_bytes"], 1312)
        self.assertEqual(CANDIDATES["ML-DSA-44"]["signature_bytes"], 2420)
        self.assertEqual(CANDIDATES["ML-DSA-65"]["public_key_bytes"], 1952)
        self.assertEqual(CANDIDATES["ML-DSA-65"]["signature_bytes"], 3309)
        self.assertEqual(CANDIDATES["ML-DSA-87"]["public_key_bytes"], 2592)
        self.assertEqual(CANDIDATES["ML-DSA-87"]["signature_bytes"], 4627)
        self.assertEqual(SOURCE_COMMIT, "b84df503a3cf57ede27f33a81185a63305579a95")

    def test_vector_loader_accepts_expected_lengths(self):
        td, path = self._write_vector("ML-DSA-44")
        try:
            pk, sig, msg, ctx = load_vector(path, "ML-DSA-44")
            self.assertEqual(len(pk), 1312)
            self.assertEqual(len(sig), 2420)
            self.assertEqual(msg, b"message")
            self.assertEqual(ctx, b"axven-lab")
        finally:
            td.cleanup()

    def test_vector_loader_rejects_algorithm_mismatch(self):
        td, path = self._write_vector("ML-DSA-44")
        try:
            with self.assertRaisesRegex(ValueError, "vector algorithm"):
                load_vector(path, "ML-DSA-65")
        finally:
            td.cleanup()

    def test_vector_loader_rejects_wrong_key_or_signature_length(self):
        for field, kwargs, message in (
            ("pk", {"pk_len": 1}, "public-key length mismatch"),
            ("sig", {"sig_len": 1}, "signature length mismatch"),
        ):
            with self.subTest(field=field):
                td, path = self._write_vector("ML-DSA-44", **kwargs)
                try:
                    with self.assertRaisesRegex(ValueError, message):
                        load_vector(path, "ML-DSA-44")
                finally:
                    td.cleanup()

    def test_vector_loader_rejects_missing_valid_vector(self):
        td, path = self._write_vector("ML-DSA-44")
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            data["testGroups"][0]["tests"][0]["result"] = "invalid"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "no valid verification vector"):
                load_vector(path, "ML-DSA-44")
        finally:
            td.cleanup()


if __name__ == "__main__":
    unittest.main()
