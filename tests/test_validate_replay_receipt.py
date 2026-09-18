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
    from scripts.validate_replay_receipt import load_replay_receipt, validate_replay_receipt
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
        for value in (0, 2, -1, True, "1", 1.0):
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
