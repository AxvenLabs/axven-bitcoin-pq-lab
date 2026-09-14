import unittest

from scripts.regtest_hybrid_transcript import build_transcript, hybrid_gate


TXID = "11" * 32
MSG = "22" * 32


class RegtestHybridTranscriptTests(unittest.TestCase):
    def test_transcript_is_deterministic_and_candidate_neutral(self):
        first = build_transcript(txid=TXID, vout=7, message_digest=MSG, candidate="ML-DSA-44")
        second = build_transcript(
            txid=TXID.upper(),
            vout=7,
            message_digest=MSG.upper(),
            candidate="ML-DSA-44",
        )
        self.assertEqual(first, second)
        self.assertIs(first["research_only"], True)
        self.assertEqual(first["network"], "regtest")
        self.assertIs(first["endorsed_by_bitcoin_core"], False)
        self.assertIs(first["mainnet_intended"], False)
        self.assertIs(first["parameter_set_selected"], False)
        self.assertIs(first["script_semantics_defined"], False)
        self.assertIs(first["consensus_changed"], False)

    def test_candidate_changes_transcript_without_selecting_winner(self):
        digests = {
            build_transcript(txid=TXID, vout=0, message_digest=MSG, candidate=name)[
                "transcript_sha256"
            ]
            for name in ("ML-DSA-44", "ML-DSA-65", "ML-DSA-87")
        }
        self.assertEqual(len(digests), 3)

    def test_classical_and_pq_truth_table(self):
        cases = (
            (False, False, False),
            (False, True, False),
            (True, False, False),
            (True, True, True),
        )
        for classical_valid, pq_valid, expected in cases:
            with self.subTest(
                classical_valid=classical_valid,
                pq_valid=pq_valid,
                expected=expected,
            ):
                self.assertIs(
                    hybrid_gate(classical_valid=classical_valid, pq_valid=pq_valid),
                    expected,
                )

    def test_malformed_transcript_inputs_fail_closed(self):
        cases = (
            {"txid": "00", "vout": 0, "message_digest": MSG, "candidate": "ML-DSA-44"},
            {"txid": "zz" * 32, "vout": 0, "message_digest": MSG, "candidate": "ML-DSA-44"},
            {"txid": TXID, "vout": -1, "message_digest": MSG, "candidate": "ML-DSA-44"},
            {"txid": TXID, "vout": 2**32, "message_digest": MSG, "candidate": "ML-DSA-44"},
            {"txid": TXID, "vout": 0, "message_digest": "01", "candidate": "ML-DSA-44"},
            {"txid": TXID, "vout": 0, "message_digest": MSG, "candidate": "winner"},
        )
        for kwargs in cases:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    build_transcript(**kwargs)

    def test_gate_rejects_truthy_non_boolean_inputs(self):
        with self.assertRaises(TypeError):
            hybrid_gate(classical_valid=1, pq_valid=True)
        with self.assertRaises(TypeError):
            hybrid_gate(classical_valid=True, pq_valid="yes")


if __name__ == "__main__":
    unittest.main()
