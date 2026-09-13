import json
import pathlib
import unittest

from scripts.migration_scenario import validate_scenario


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCENARIO_DIR = ROOT / "scenarios"


class ScenarioCatalogTests(unittest.TestCase):
    def test_all_catalog_manifests_validate(self):
        manifests = sorted(SCENARIO_DIR.glob("*.json"))
        self.assertGreaterEqual(len(manifests), 3)
        ids = set()
        for path in manifests:
            with self.subTest(path=path.name):
                scenario = json.loads(path.read_text(encoding="utf-8"))
                self.assertIs(validate_scenario(scenario), scenario)
                self.assertNotIn(scenario["scenario_id"], ids)
                ids.add(scenario["scenario_id"])

    def test_catalog_is_regtest_research_only(self):
        for path in sorted(SCENARIO_DIR.glob("*.json")):
            with self.subTest(path=path.name):
                scenario = json.loads(path.read_text(encoding="utf-8"))
                self.assertIs(scenario["research_only"], True)
                self.assertEqual(scenario["network"], "regtest")
                self.assertEqual(
                    scenario["upstream_behavior_outside_experiment"],
                    "preserved",
                )

    def test_replay_scenario_is_evidence_only(self):
        path = SCENARIO_DIR / "replay_context_mismatch.json"
        scenario = json.loads(path.read_text(encoding="utf-8"))
        combined = " ".join(
            [scenario["purpose"]]
            + scenario["assumptions"]
            + [step["action"] for step in scenario["steps"]]
        ).lower()
        self.assertIn("evidence", combined)
        self.assertNotIn("mainnet transaction", scenario["purpose"].lower())


if __name__ == "__main__":
    unittest.main()
