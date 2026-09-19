import copy
import json
import tempfile
import unittest
from pathlib import Path

try:
    from scripts.regtest_chain_evidence import build_chain_evidence
    from scripts.regtest_mldsa_composition import build_composition
    from scripts.regtest_benchmark_evidence import build_benchmark_evidence
    from scripts.regtest_provenance_evidence import (
        build_provenance,
        EXPECTED_COMMIT,
        EXPECTED_TAG,
        EXPECTED_TAG_OBJECT,
    )
    from scripts.regtest_e2e_evidence import build_e2e_evidence
    from scripts.replay_regtest_e2e_evidence import replay_e2e_evidence
    from scripts.validate_replay_receipt import MAX_JSON_NESTING, MAX_RECEIPT_BYTES, load_replay_receipt, validate_replay_receipt
except (ImportError, ModuleNotFoundError):
    raise unittest.SkipTest("requires pinned ML-DSA backend")


class T(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        chain = build_chain_evidence(
            txid="a" * 64,
            vout=0,
            amount_btc="1.0",
            confirmations=1,
            block_hash="b" * 64,
            block_height=102,
            tx_hex="00",
            tx_size=1,
            tx_weight=4,
            tx_vsize=1,
        )
        composition = build_composition(txid="a" * 64, vout=0, message_digest="c" * 64)
        benchmark = build_benchmark_evidence(3)
        provenance = build_provenance(
            repo_commit="d" * 40,
            bitcoin_version="Bitcoin Core daemon version v31.1 bitcoind",
            source_commit=EXPECTED_COMMIT,
            tag=EXPECTED_TAG,
            tag_object=EXPECTED_TAG_OBJECT,
            bitcoind_sha256="e" * 64,
            bitcoin_cli_sha256="f" * 64,
            python_version="3.12.3",
            cryptography_version="48.0.0",
            openssl_version="OpenSSL test",
            os_name="Linux",
            machine="x86_64",
        )
        cls.receipt = replay_e2e_evidence(build_e2e_evidence(chain, composition, benchmark, provenance))

    def assertReceiptRejects(self, **changes):
        tampered = copy.deepcopy(self.receipt)
        tampered.update(changes)
        with self.assertRaises(ValueError):
            validate_replay_receipt(tampered)

    def test_intact_receipt_validates_deterministically(self):
        first = validate_replay_receipt(self.receipt)
        second = validate_replay_receipt(copy.deepcopy(self.receipt))
        self.assertEqual(first, second)
        self.assertEqual(first, self.receipt["replay_receipt_sha256"])

    def test_duplicate_json_field_fails_closed_at_load(self):
        encoded = json.dumps(self.receipt, sort_keys=True, separators=(",", ":"))
        duplicate = encoded[:-1] + ',"schema_version":1}'
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "receipt.json"
            path.write_text(duplicate, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate replay receipt field"):
                load_replay_receipt(path)

    def test_oversized_json_fails_closed_before_parse(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "receipt.json"
            path.write_bytes(b" " * (MAX_RECEIPT_BYTES + 1))
            with self.assertRaisesRegex(ValueError, "replay receipt exceeds size limit"):
                load_replay_receipt(path)

    def test_excessive_json_nesting_fails_closed_at_load(self):
        nested = "[" * (MAX_JSON_NESTING + 1) + "0" + "]" * (MAX_JSON_NESTING + 1)
        self.assertLess(len(nested.encode("utf-8")), MAX_RECEIPT_BYTES)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "receipt.json"
            path.write_text(nested, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "replay receipt JSON nesting is too deep"):
                load_replay_receipt(path)

    def test_brackets_inside_json_string_do_not_count_as_nesting(self):
        value = "[" * (MAX_JSON_NESTING + 1) + "]" * (MAX_JSON_NESTING + 1)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "receipt.json"
            path.write_text(json.dumps(value), encoding="utf-8")
            self.assertEqual(load_replay_receipt(path), value)

    def test_invalid_utf8_fails_closed_at_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "receipt.json"
            path.write_bytes(b'{"schema_version":1,"x":"\xff"}')
            with self.assertRaisesRegex(ValueError, "replay receipt is not valid UTF-8"):
                load_replay_receipt(path)

    def test_utf8_bom_fails_closed_at_load(self):
        encoded = json.dumps(self.receipt, sort_keys=True, separators=(",", ":")).encode("utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "receipt.json"
            path.write_bytes(b"\xef\xbb\xbf" + encoded)
            with self.assertRaisesRegex(ValueError, "replay receipt must not contain a UTF-8 BOM"):
                load_replay_receipt(path)

    def test_nonstandard_json_constants_fail_closed_at_load(self):
        encoded = json.dumps(self.receipt, sort_keys=True, separators=(",", ":"))
        for constant in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(constant=constant), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "receipt.json"
                tampered = encoded.replace('"schema_version":1', f'"schema_version":{constant}', 1)
                path.write_text(tampered, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, "non-standard JSON constant"):
                    load_replay_receipt(path)

    def test_non_object_json_roots_fail_closed(self):
        cases = ([], [self.receipt], None, True, 1, "receipt")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "receipt.json"
            for value in cases:
                with self.subTest(value=value):
                    path.write_text(json.dumps(value), encoding="utf-8")
                    loaded = load_replay_receipt(path)
                    with self.assertRaisesRegex(ValueError, "unexpected replay receipt fields"):
                        validate_replay_receipt(loaded)

    def test_digest_tamper_fails_closed(self):
        self.assertReceiptRejects(input_e2e_sha256="0" * 64)

    def test_digest_encoding_matrix_fails_closed(self):
        digest = self.receipt["input_e2e_sha256"]
        cases = (digest.upper(), "g" * 64, digest[:-1], digest + "0")
        for value in cases:
            with self.subTest(value=value):
                self.assertReceiptRejects(input_e2e_sha256=value)

    def test_safety_boundary_tamper_matrix_fails_closed(self):
        cases = {
            "research_only": False,
            "off_consensus": False,
            "bitcoin_core_modified": True,
            "mainnet_intended": True,
            "parameter_set_selected": True,
        }
        for key, value in cases.items():
            with self.subTest(key=key):
                self.assertReceiptRejects(**{key: value})

    def test_validator_result_tamper_fails_closed(self):
        self.assertReceiptRejects(validator_result="rejected")

    def test_schema_version_tamper_matrix_fails_closed(self):
        for value in (0, 2, -1, True, "1", 1.0):
            with self.subTest(value=value):
                self.assertReceiptRejects(schema_version=value)

    def test_validator_schema_version_tamper_matrix_fails_closed(self):
        expected = self.receipt["validator_schema_version"]
        for value in (0, 1, 3, -1, True, str(expected), float(expected)):
            with self.subTest(value=value):
                self.assertReceiptRejects(validator_schema_version=value)

    def test_unknown_field_fails_closed(self):
        tampered = copy.deepcopy(self.receipt)
        tampered["production_authorized"] = True
        with self.assertRaises(ValueError):
            validate_replay_receipt(tampered)

    def test_missing_field_fails_closed(self):
        tampered = copy.deepcopy(self.receipt)
        del tampered["off_consensus"]
        with self.assertRaises(ValueError):
            validate_replay_receipt(tampered)

    def test_receipt_hash_tamper_fails_closed(self):
        self.assertReceiptRejects(replay_receipt_sha256="f" * 64)

    def test_receipt_hash_encoding_matrix_fails_closed(self):
        digest = self.receipt["replay_receipt_sha256"]
        cases = (digest.upper(), "g" * 64, digest[:-1], digest + "0")
        for value in cases:
            with self.subTest(value=value):
                self.assertReceiptRejects(replay_receipt_sha256=value)


if __name__ == "__main__":
    unittest.main()
