"""Tests for canonical real-regtest chain evidence. Research-only/off-consensus."""
from __future__ import annotations

import unittest

from scripts.regtest_chain_evidence import build_chain_evidence


class RegtestChainEvidenceTests(unittest.TestCase):
    def kwargs(self) -> dict:
        return dict(
            txid="ab" * 32,
            vout=0,
            amount_btc="1.00000000",
            confirmations=1,
            block_hash="cd" * 32,
            block_height=102,
            tx_hex="00" * 100,
            tx_size=100,
            tx_weight=400,
            tx_vsize=100,
        )

    def test_deterministic_and_explicitly_off_consensus(self) -> None:
        a = build_chain_evidence(**self.kwargs())
        b = build_chain_evidence(**self.kwargs())
        self.assertEqual(a, b)
        self.assertEqual(len(a["chain_evidence_sha256"]), 64)
        self.assertTrue(a["research_only"])
        self.assertTrue(a["off_consensus"])
        self.assertFalse(a["bitcoin_core_modified"])
        self.assertFalse(a["consensus_changed"])
        self.assertFalse(a["script_semantics_defined"])
        self.assertFalse(a["parameter_set_selected"])

    def test_records_block_and_transaction_metrics(self) -> None:
        report = build_chain_evidence(**self.kwargs())
        self.assertEqual(report["confirmation"], {"block_hash": "cd" * 32, "block_height": 102})
        self.assertEqual(report["transaction"]["serialized_bytes"], 100)
        self.assertEqual(report["transaction"]["weight"], 400)
        self.assertEqual(report["transaction"]["vbytes"], 100)
        self.assertNotIn("raw_tx", report["transaction"])

    def test_rejects_inconsistent_serialized_size(self) -> None:
        kw = self.kwargs(); kw["tx_size"] = 99
        with self.assertRaisesRegex(ValueError, "transaction metrics"):
            build_chain_evidence(**kw)

    def test_rejects_inconsistent_vsize(self) -> None:
        kw = self.kwargs(); kw["tx_weight"] = 401
        with self.assertRaisesRegex(ValueError, "vsize"):
            build_chain_evidence(**kw)

    def test_rejects_unconfirmed_observation(self) -> None:
        kw = self.kwargs(); kw["confirmations"] = 0
        with self.assertRaisesRegex(ValueError, "confirmed outpoint"):
            build_chain_evidence(**kw)


if __name__ == "__main__":
    unittest.main()
