import unittest

from scripts.regtest_demo_preflight import build_report


class RegtestDemoPreflightTests(unittest.TestCase):
    def test_report_keeps_all_high_impact_decisions_open(self):
        report = build_report("ab" * 32, 1, 2, "1.00000000")
        self.assertTrue(report["research_only"])
        self.assertFalse(report["endorsed_by_bitcoin_core"])
        self.assertFalse(report["mainnet_intended"])
        self.assertEqual(report["network"], "regtest")
        self.assertFalse(report["bitcoin_core_modified"])
        self.assertFalse(report["creates_coin_token_or_network"])
        for key in (
            "scheme_selected",
            "hybrid_semantics_selected",
            "consensus_change_selected",
            "activation_selected",
            "legacy_utxo_treatment_selected",
            "lost_coin_treatment_selected",
            "recovery_authority_selected",
            "trust_root_selected",
            "key_custody_selected",
        ):
            with self.subTest(key=key):
                self.assertFalse(report[key])
        self.assertEqual(
            report["experiment_on_status"],
            "blocked_pending_explicit_security_decisions",
        )
        self.assertEqual(
            report["required_decisions"],
            ["post_quantum_scheme", "hybrid_authorization_semantics"],
        )

    def test_observed_utxo_is_reported(self):
        report = build_report("01" * 32, 3, 7, "0.50000000")
        self.assertEqual(
            report["observed_utxo"],
            {
                "txid": "01" * 32,
                "vout": 3,
                "confirmations": 7,
                "amount_btc": "0.50000000",
            },
        )

    def test_invalid_txid_fails_closed(self):
        for txid in ("", "AA" * 32, "00" * 31, "g0" * 32):
            with self.subTest(txid=txid):
                with self.assertRaises(ValueError):
                    build_report(txid, 0, 1, "1.0")

    def test_invalid_numeric_fields_fail_closed(self):
        for vout in (-1, True):
            with self.subTest(vout=vout):
                with self.assertRaises(ValueError):
                    build_report("00" * 32, vout, 1, "1.0")
        for confirmations in (0, -1, True):
            with self.subTest(confirmations=confirmations):
                with self.assertRaises(ValueError):
                    build_report("00" * 32, 0, confirmations, "1.0")

    def test_empty_amount_fails_closed(self):
        with self.assertRaises(ValueError):
            build_report("00" * 32, 0, 1, "")


if __name__ == "__main__":
    unittest.main()
