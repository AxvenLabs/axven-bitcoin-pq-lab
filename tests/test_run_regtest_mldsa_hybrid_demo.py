import unittest

try:
    from scripts.run_regtest_mldsa_hybrid_demo import run_demo
except ImportError as exc:
    if exc.name == "cryptography.hazmat.primitives.asymmetric.mldsa":
        run_demo = None
    else:
        raise


TXID = "11" * 32
MSG = "22" * 32
CANDIDATES = ("ML-DSA-44", "ML-DSA-65", "ML-DSA-87")
EXPECTED_SIGNATURE_BYTES = {
    "ML-DSA-44": 2420,
    "ML-DSA-65": 3309,
    "ML-DSA-87": 4627,
}


@unittest.skipUnless(run_demo is not None, "requires pinned ML-DSA benchmark backend")
class RegtestMldsaHybridDemoTests(unittest.TestCase):
    def test_all_named_candidates_run_without_selection(self):
        public_key_hashes = set()
        for candidate in CANDIDATES:
            with self.subTest(candidate=candidate):
                first = run_demo(
                    txid=TXID,
                    vout=3,
                    message_digest=MSG,
                    candidate=candidate,
                    classical_valid=True,
                )
                second = run_demo(
                    txid=TXID,
                    vout=3,
                    message_digest=MSG,
                    candidate=candidate,
                    classical_valid=True,
                )
                self.assertEqual(first, second)
                self.assertIs(first["research_only"], True)
                self.assertIs(first["off_consensus"], True)
                self.assertIs(first["parameter_set_selected"], False)
                self.assertIs(first["bitcoin_core_modified"], False)
                self.assertIs(first["script_semantics_defined"], False)
                self.assertIs(first["consensus_changed"], False)
                self.assertEqual(first["signature_bytes"], EXPECTED_SIGNATURE_BYTES[candidate])
                self.assertIs(first["pq_valid_signature_accepted"], True)
                self.assertIs(first["pq_altered_transcript_rejected"], True)
                self.assertIs(first["evidence"]["verification"]["authorized"], True)
                public_key_hashes.add(first["public_key_sha256"])
        self.assertEqual(len(public_key_hashes), 3)

    def test_classical_false_keeps_and_gate_fail_closed(self):
        for candidate in CANDIDATES:
            with self.subTest(candidate=candidate):
                report = run_demo(
                    txid=TXID,
                    vout=0,
                    message_digest=MSG,
                    candidate=candidate,
                    classical_valid=False,
                )
                self.assertIs(report["evidence"]["verification"]["pq_valid"], True)
                self.assertIs(report["evidence"]["verification"]["classical_valid"], False)
                self.assertIs(report["evidence"]["verification"]["authorized"], False)

    def test_invalid_candidate_and_non_boolean_classical_result_fail_closed(self):
        with self.assertRaises(ValueError):
            run_demo(
                txid=TXID,
                vout=0,
                message_digest=MSG,
                candidate="ML-DSA-99",
                classical_valid=True,
            )
        with self.assertRaises(TypeError):
            run_demo(
                txid=TXID,
                vout=0,
                message_digest=MSG,
                candidate="ML-DSA-44",
                classical_valid=1,
            )


if __name__ == "__main__":
    unittest.main()
