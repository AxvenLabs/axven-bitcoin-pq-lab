import copy
import unittest

try:
    from scripts.run_regtest_mldsa_hybrid_demo import run_demo
    from scripts.validate_regtest_mldsa_hybrid_demo import validate_demo_report
except ImportError as exc:
    if exc.name and exc.name.startswith("cryptography"):
        run_demo = validate_demo_report = None
    else:
        raise

TXID = "11" * 32
MSG = "22" * 32
CANDIDATES = ("ML-DSA-44", "ML-DSA-65", "ML-DSA-87")


@unittest.skipUnless(run_demo is not None, "requires pinned ML-DSA benchmark backend")
class RegtestMldsaHybridDemoValidatorTests(unittest.TestCase):
    def _report(self, candidate="ML-DSA-44", classical=True):
        return run_demo(txid=TXID, vout=2, message_digest=MSG, candidate=candidate, classical_valid=classical)

    def test_all_candidates_validate_deterministically(self):
        digests = []
        for candidate in CANDIDATES:
            with self.subTest(candidate=candidate):
                report = self._report(candidate)
                first = validate_demo_report(report)
                second = validate_demo_report(report)
                self.assertEqual(first, second)
                self.assertEqual(first, report["demo_sha256"])
                digests.append(first)
        self.assertEqual(len(set(digests)), 3)

    def test_classical_false_is_valid_evidence_but_not_authorized(self):
        report = self._report(classical=False)
        self.assertIs(report["evidence"]["verification"]["authorized"], False)
        self.assertEqual(validate_demo_report(report), report["demo_sha256"])

    def test_tampering_and_selection_fields_fail_closed(self):
        mutations = []
        base = self._report()
        for path, value in [
            (("signature_bytes",), 1),
            (("parameter_set_selected",), True),
            (("script_semantics_defined",), True),
            (("consensus_changed",), True),
            (("pq_altered_transcript_rejected",), False),
            (("demo_sha256",), "00" * 32),
        ]:
            item = copy.deepcopy(base)
            item[path[0]] = value
            mutations.append(item)
        nested = copy.deepcopy(base)
        nested["evidence"]["winner"] = "ML-DSA-44"
        mutations.append(nested)
        mismatch = copy.deepcopy(base)
        mismatch["candidate"] = "ML-DSA-65"
        mutations.append(mismatch)
        for item in mutations:
            with self.assertRaises(ValueError):
                validate_demo_report(item)


if __name__ == "__main__":
    unittest.main()
