import unittest

from scripts.migration_scenario import validate_scenario


def sample_scenario(**overrides):
    scenario = {
        "schema_version": 1,
        "research_only": True,
        "network": "regtest",
        "upstream_behavior_outside_experiment": "preserved",
        "scenario_id": "rollback-smoke-001",
        "title": "Reversible experiment rollback smoke scenario",
        "purpose": "Exercise a bounded lab-only transition and verify rollback evidence.",
        "assumptions": [
            "Bitcoin Core remains unmodified outside the isolated experiment path.",
            "No mainnet or public-network deployment is performed.",
        ],
        "steps": [
            {
                "id": "baseline",
                "phase": "baseline",
                "action": "Record vanilla regtest state before experiment activity.",
                "expectation": "observe",
                "evidence": "baseline state snapshot",
            },
            {
                "id": "exercise",
                "phase": "exercise",
                "action": "Run a reversible experiment placeholder without defining authorization semantics.",
                "expectation": "observe",
                "evidence": "experiment trace",
            },
            {
                "id": "rollback",
                "phase": "rollback",
                "action": "Disable the isolated experiment and restore the pre-experiment lab state.",
                "expectation": "unchanged",
                "evidence": "post-rollback equivalence record",
            },
        ],
        "decision_gates": [
            "Any choice of post-quantum signature scheme requires explicit user review.",
            "Any Bitcoin consensus, activation, legacy UTXO, recovery, trust-root or key-custody semantics require explicit user review.",
        ],
    }
    scenario.update(overrides)
    return scenario


class MigrationScenarioTests(unittest.TestCase):
    def test_valid_scenario_passes(self):
        scenario = sample_scenario()
        self.assertIs(validate_scenario(scenario), scenario)

    def test_rejects_non_regtest_network(self):
        with self.assertRaisesRegex(ValueError, "regtest"):
            validate_scenario(sample_scenario(network="mainnet"))

    def test_rejects_missing_research_only_label(self):
        with self.assertRaisesRegex(ValueError, "research_only"):
            validate_scenario(sample_scenario(research_only=False))

    def test_rejects_upstream_behavior_change(self):
        with self.assertRaisesRegex(ValueError, "preserved"):
            validate_scenario(sample_scenario(upstream_behavior_outside_experiment="modified"))

    def test_rejects_high_impact_decision_fields(self):
        for field in (
            "pq_scheme",
            "hybrid_semantics",
            "mainnet_activation",
            "fork_deployment",
            "legacy_utxo_policy",
            "lost_coin_policy",
            "recovery_authority",
            "trust_root",
            "key_custody",
        ):
            with self.subTest(field=field):
                with self.assertRaisesRegex(ValueError, "high-impact decision"):
                    validate_scenario(sample_scenario(**{field: "placeholder"}))

    def test_rejects_duplicate_step_ids(self):
        scenario = sample_scenario()
        scenario["steps"][1]["id"] = scenario["steps"][0]["id"]
        with self.assertRaisesRegex(ValueError, "duplicate step id"):
            validate_scenario(scenario)

    def test_rejects_unknown_phase(self):
        scenario = sample_scenario()
        scenario["steps"][0]["phase"] = "activate-mainnet"
        with self.assertRaisesRegex(ValueError, "phase is invalid"):
            validate_scenario(scenario)

    def test_requires_decision_gates(self):
        with self.assertRaisesRegex(ValueError, "decision_gates"):
            validate_scenario(sample_scenario(decision_gates=[]))


if __name__ == "__main__":
    unittest.main()
