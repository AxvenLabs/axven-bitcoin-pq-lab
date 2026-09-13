import copy
import json
import unittest
from pathlib import Path

from scripts.validate_regtest_demo_policy import validate_policy


class RegtestDemoPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.policy = json.loads(
            Path("lab/regtest-demo-002-policy.json").read_text(encoding="utf-8")
        )

    def test_approved_research_choices_are_explicit(self):
        validate_policy(self.policy)
        self.assertEqual(self.policy["pq_candidate_family"], "ML-DSA")
        self.assertEqual(
            self.policy["hybrid_authorization_semantics"], "classical-and-pq"
        )
        self.assertEqual(
            self.policy["selection_scope"], "reversible-research-candidate"
        )

    def test_parameter_set_remains_unselected(self):
        self.assertFalse(self.policy["parameter_set_selected"])

    def test_high_impact_gates_fail_closed_if_silently_selected(self):
        protected = (
            "parameter_set_selected",
            "bitcoin_consensus_change_selected",
            "activation_or_fork_selected",
            "legacy_utxo_treatment_selected",
            "lost_coin_treatment_selected",
            "recovery_authority_selected",
            "trust_root_selected",
            "key_custody_selected",
            "production_security_semantics_selected",
            "security_engine_source_used",
        )
        for field in protected:
            with self.subTest(field=field):
                mutated = copy.deepcopy(self.policy)
                mutated[field] = True
                with self.assertRaisesRegex(ValueError, field):
                    validate_policy(mutated)

    def test_or_semantics_is_rejected_for_this_approved_research_track(self):
        mutated = copy.deepcopy(self.policy)
        mutated["hybrid_authorization_semantics"] = "classical-or-pq"
        with self.assertRaisesRegex(ValueError, "classical AND PQ"):
            validate_policy(mutated)

    def test_other_pq_family_is_rejected_without_new_decision(self):
        mutated = copy.deepcopy(self.policy)
        mutated["pq_candidate_family"] = "SLH-DSA"
        with self.assertRaisesRegex(ValueError, "ML-DSA"):
            validate_policy(mutated)


if __name__ == "__main__":
    unittest.main()
