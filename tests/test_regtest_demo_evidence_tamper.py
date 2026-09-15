"""Regression tests for fail-closed public evidence binding.

Research only. Not endorsed by Bitcoin Core. Not intended for mainnet deployment.
These tests do not select an ML-DSA parameter set or define Bitcoin Script,
output/witness, consensus, activation, recovery, trust, custody, or production semantics.
"""
from __future__ import annotations

import copy
import unittest

from scripts.run_regtest_mldsa_hybrid_demo import build_demo
from scripts.validate_regtest_mldsa_hybrid_demo import validate_demo_report


class RegtestDemoEvidenceTamperTests(unittest.TestCase):
    def setUp(self) -> None:
        self.report = build_demo(
            candidate="ML-DSA-44",
            txid="b731e7c37947aa0155fddd8889330749db9d6fb0056bc3ba3b5701ea3be6e467",
            vout=0,
            message_digest="22" * 32,
            classical_valid=True,
        )

    def test_untampered_report_validates(self) -> None:
        self.assertEqual(validate_demo_report(self.report), self.report["demo_sha256"])

    def test_outpoint_vout_tamper_fails_closed(self) -> None:
        tampered = copy.deepcopy(self.report)
        tampered["evidence"]["transcript"]["outpoint"]["vout"] = 1
        with self.assertRaisesRegex(ValueError, "canonical research transcript"):
            validate_demo_report(tampered)

    def test_message_digest_tamper_fails_closed(self) -> None:
        tampered = copy.deepcopy(self.report)
        tampered["evidence"]["transcript"]["message_digest"] = "33" * 32
        with self.assertRaisesRegex(ValueError, "canonical research transcript"):
            validate_demo_report(tampered)


if __name__ == "__main__":
    unittest.main()
