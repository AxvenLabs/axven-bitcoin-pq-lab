import copy
import unittest

from scripts.regtest_hybrid_transcript import build_transcript
from scripts.validate_regtest_hybrid_evidence import build_evidence, validate_evidence, validate_transcript


TXID = "11" * 32
MSG = "22" * 32


class RegtestHybridEvidenceValidatorTests(unittest.TestCase):
    def _transcript(self, candidate="ML-DSA-44"):
        return build_transcript(txid=TXID, vout=3, message_digest=MSG, candidate=candidate)

    def test_evidence_is_deterministic_and_candidate_neutral(self):
        for candidate in ("ML-DSA-44", "ML-DSA-65", "ML-DSA-87"):
            with self.subTest(candidate=candidate):
                transcript = self._transcript(candidate)
                first = build_evidence(transcript=transcript, classical_valid=True, pq_valid=True)
                second = build_evidence(transcript=copy.deepcopy(transcript), classical_valid=True, pq_valid=True)
                self.assertEqual(first, second)
                self.assertEqual(validate_evidence(first), first)
                self.assertIs(first["research_only"], True)
                self.assertIs(first["off_consensus"], True)
                self.assertIs(first["parameter_set_selected"], False)
                self.assertIs(first["script_semantics_defined"], False)
                self.assertIs(first["consensus_changed"], False)

    def test_complete_classical_and_pq_truth_table_is_bound_to_evidence(self):
        cases = (
            (False, False, False),
            (False, True, False),
            (True, False, False),
            (True, True, True),
        )
        transcript = self._transcript()
        for classical_valid, pq_valid, expected in cases:
            with self.subTest(classical_valid=classical_valid, pq_valid=pq_valid):
                evidence = build_evidence(
                    transcript=transcript,
                    classical_valid=classical_valid,
                    pq_valid=pq_valid,
                )
                self.assertIs(evidence["verification"]["authorized"], expected)
                self.assertEqual(validate_evidence(evidence), evidence)

    def test_transcript_tampering_fails_closed(self):
        transcript = self._transcript()
        mutations = []

        changed_digest = copy.deepcopy(transcript)
        changed_digest["message_digest"] = "33" * 32
        mutations.append(changed_digest)

        changed_flag = copy.deepcopy(transcript)
        changed_flag["script_semantics_defined"] = True
        mutations.append(changed_flag)

        selected = copy.deepcopy(transcript)
        selected["parameter_set_selected"] = True
        mutations.append(selected)

        extra_field = copy.deepcopy(transcript)
        extra_field["winner"] = "ML-DSA-44"
        mutations.append(extra_field)

        for mutated in mutations:
            with self.subTest(mutated=mutated):
                with self.assertRaises(ValueError):
                    validate_transcript(mutated)

    def test_evidence_tampering_fails_closed(self):
        evidence = build_evidence(transcript=self._transcript(), classical_valid=True, pq_valid=True)
        mutations = []

        wrong_authorized = copy.deepcopy(evidence)
        wrong_authorized["verification"]["authorized"] = False
        mutations.append(wrong_authorized)

        changed_digest = copy.deepcopy(evidence)
        changed_digest["evidence_sha256"] = "00" * 32
        mutations.append(changed_digest)

        mainnet = copy.deepcopy(evidence)
        mainnet["mainnet_intended"] = True
        mutations.append(mainnet)

        ranked = copy.deepcopy(evidence)
        ranked["rank"] = 1
        mutations.append(ranked)

        for mutated in mutations:
            with self.subTest(mutated=mutated):
                with self.assertRaises((ValueError, TypeError)):
                    validate_evidence(mutated)

    def test_non_boolean_verifier_results_fail_closed(self):
        transcript = self._transcript()
        with self.assertRaises(TypeError):
            build_evidence(transcript=transcript, classical_valid=1, pq_valid=True)
        with self.assertRaises(TypeError):
            build_evidence(transcript=transcript, classical_valid=True, pq_valid="yes")


if __name__ == "__main__":
    unittest.main()
