import copy
import unittest

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
    from scripts.validate_replay_receipt import _canonical_digest, validate_replay_receipt
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
        cls.evidence = build_e2e_evidence(chain, composition, benchmark, provenance)
        cls.receipt = replay_e2e_evidence(cls.evidence)

    def test_intact_receipt_validates_deterministically(self):
        first = validate_replay_receipt(self.receipt)
        second = validate_replay_receipt(copy.deepcopy(self.receipt))
        self.assertEqual(first, second)
        self.assertEqual(first, self.receipt["replay_receipt_sha256"])

    def test_intact_receipt_binds_to_supplied_evidence(self):
        self.assertEqual(
            validate_replay_receipt(self.receipt, evidence=self.evidence),
            self.receipt["replay_receipt_sha256"],
        )

    def test_rehashed_forged_input_digest_fails_against_supplied_evidence(self):
        tampered = copy.deepcopy(self.receipt)
        tampered["input_e2e_sha256"] = "0" * 64
        unsigned = dict(tampered)
        del unsigned["replay_receipt_sha256"]
        tampered["replay_receipt_sha256"] = _canonical_digest(unsigned)
        with self.assertRaisesRegex(ValueError, "not bound to supplied evidence"):
            validate_replay_receipt(tampered, evidence=self.evidence)

    def test_digest_tamper_fails_closed(self):
        tampered = copy.deepcopy(self.receipt)
        tampered["input_e2e_sha256"] = "0" * 64
        with self.assertRaises(ValueError):
            validate_replay_receipt(tampered)

    def test_safety_overclaim_fails_closed(self):
        tampered = copy.deepcopy(self.receipt)
        tampered["mainnet_intended"] = True
        with self.assertRaises(ValueError):
            validate_replay_receipt(tampered)

    def test_unknown_field_fails_closed(self):
        tampered = copy.deepcopy(self.receipt)
        tampered["production_authorized"] = True
        with self.assertRaises(ValueError):
            validate_replay_receipt(tampered)

    def test_receipt_hash_tamper_fails_closed(self):
        tampered = copy.deepcopy(self.receipt)
        tampered["replay_receipt_sha256"] = "f" * 64
        with self.assertRaises(ValueError):
            validate_replay_receipt(tampered)


if __name__ == "__main__":
    unittest.main()
