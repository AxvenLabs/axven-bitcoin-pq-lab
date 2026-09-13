import copy
import json
import unittest
from pathlib import Path

from scripts.validate_research_vectors import REQUIRED_GATES, validate


VECTOR_PATH = Path("vectors/research-scenario-vectors-v1.json")


def load_vectors():
    with VECTOR_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)


class ResearchVectorTests(unittest.TestCase):
    def test_checked_in_vectors_validate(self):
        document = load_vectors()
        self.assertIs(validate(document), document)

    def test_vectors_cover_required_neutral_scenarios(self):
        categories = {vector["category"] for vector in load_vectors()["vectors"]}
        self.assertEqual(categories, {"rollback", "failure-recovery", "replay", "migration"})

    def test_migration_vector_contains_every_high_impact_gate(self):
        migration = next(v for v in load_vectors()["vectors"] if v["category"] == "migration")
        self.assertEqual(set(migration["decision_gates"]), REQUIRED_GATES)

    def test_rejects_missing_research_only_label(self):
        document = load_vectors()
        document["research_only"] = False
        with self.assertRaisesRegex(ValueError, "research_only"):
            validate(document)

    def test_rejects_mainnet_scope(self):
        document = load_vectors()
        document["deployment_scope"] = "mainnet"
        with self.assertRaisesRegex(ValueError, "deployment_scope"):
            validate(document)

    def test_rejects_silent_scheme_selection(self):
        document = load_vectors()
        document["vectors"][0]["pq_scheme"] = "example"
        with self.assertRaisesRegex(ValueError, "forbidden high-impact decision fields"):
            validate(document)

    def test_rejects_silent_hybrid_semantics(self):
        document = load_vectors()
        document["vectors"][0]["hybrid_semantics"] = "example"
        with self.assertRaisesRegex(ValueError, "forbidden high-impact decision fields"):
            validate(document)

    def test_rejects_missing_migration_gate(self):
        document = load_vectors()
        migration = next(v for v in document["vectors"] if v["category"] == "migration")
        migration["decision_gates"] = migration["decision_gates"][:-1]
        with self.assertRaisesRegex(ValueError, "migration decision gates mismatch"):
            validate(document)

    def test_rejects_duplicate_vector_id(self):
        document = load_vectors()
        duplicate = copy.deepcopy(document["vectors"][0])
        document["vectors"].append(duplicate)
        with self.assertRaisesRegex(ValueError, "unique"):
            validate(document)


if __name__ == "__main__":
    unittest.main()
