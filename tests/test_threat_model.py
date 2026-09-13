import json
import unittest
from pathlib import Path

from scripts.validate_threat_model import validate

MODEL_PATH = Path("lab/threat-model-v1.json")


def load_model():
    return json.loads(MODEL_PATH.read_text(encoding="utf-8"))


class ThreatModelContractTests(unittest.TestCase):
    def test_repository_model_passes(self):
        model = load_model()
        self.assertIs(validate(model), model)

    def test_rejects_non_research_model(self):
        model = load_model()
        model["research_only"] = False
        with self.assertRaisesRegex(ValueError, "research_only"):
            validate(model)

    def test_rejects_mainnet_deployment(self):
        model = load_model()
        model["mainnet_deployment"] = True
        with self.assertRaisesRegex(ValueError, "mainnet_deployment"):
            validate(model)

    def test_rejects_missing_upstream_preservation(self):
        model = load_model()
        model["preserve_upstream_outside_experiment"] = False
        with self.assertRaisesRegex(ValueError, "upstream behavior"):
            validate(model)

    def test_rejects_missing_scheme_selection_gate(self):
        model = load_model()
        model["decision_gates"].remove("cryptographic_scheme_selection")
        with self.assertRaisesRegex(ValueError, "missing decision gates"):
            validate(model)

    def test_rejects_missing_production_security_gate(self):
        model = load_model()
        model["decision_gates"].remove("production_security_semantics")
        with self.assertRaisesRegex(ValueError, "missing decision gates"):
            validate(model)

    def test_rejects_duplicate_capabilities(self):
        model = load_model()
        model["adversary_capabilities"].append(model["adversary_capabilities"][0])
        with self.assertRaisesRegex(ValueError, "duplicates"):
            validate(model)


if __name__ == "__main__":
    unittest.main()
