import copy
import unittest

from scripts.regtest_e2e_evidence import build_e2e_evidence
from scripts.validate_regtest_e2e_evidence import validate_e2e_evidence


class TestValidateRegtestE2EEvidence(unittest.TestCase):
    def setUp(self):
        common = {"research_only": True, "endorsed_by_bitcoin_core": False,
                  "mainnet_intended": False, "bitcoin_core_modified": False,
                  "parameter_set_selected": False}
        chain = {**common, "chain_evidence_sha256": "1" * 64,
                 "outpoint": {"txid": "a" * 64, "vout": 0},
                 "confirmation": {"block_hash": "b" * 64, "block_height": 102},
                 "transaction": {"raw_tx_sha256": "c" * 64, "serialized_bytes": 100,
                                 "weight": 400, "vbytes": 100}}
        composition = {**common, "composition_sha256": "2" * 64,
                       "outpoint": {"txid": "a" * 64, "vout": 0},
                       "hybrid_research_semantics": "classical-and-pq"}
        benchmark = {**common, "benchmark_evidence_sha256": "3" * 64,
                     "correctness_oracle_separate": True,
                     "native_windows_resource_portability_demonstrated": False,
                     "candidate_order": ["ML-DSA-44", "ML-DSA-65", "ML-DSA-87"]}
        self.report = build_e2e_evidence(chain, composition, benchmark)

    def test_accepts_intact_report(self):
        self.assertEqual(validate_e2e_evidence(self.report), self.report["e2e_evidence_sha256"])

    def test_rejects_digest_tamper(self):
        altered = copy.deepcopy(self.report)
        altered["confirmation"]["block_height"] += 1
        with self.assertRaises(ValueError):
            validate_e2e_evidence(altered)

    def test_rejects_parameter_selection_overclaim(self):
        altered = copy.deepcopy(self.report)
        altered["parameter_set_selected"] = True
        with self.assertRaises(ValueError):
            validate_e2e_evidence(altered)

    def test_rejects_candidate_reordering(self):
        altered = copy.deepcopy(self.report)
        altered["candidate_order"] = list(reversed(altered["candidate_order"]))
        with self.assertRaises(ValueError):
            validate_e2e_evidence(altered)

    def test_rejects_windows_portability_overclaim(self):
        altered = copy.deepcopy(self.report)
        altered["native_windows_resource_portability_demonstrated"] = True
        with self.assertRaises(ValueError):
            validate_e2e_evidence(altered)


if __name__ == "__main__":
    unittest.main()
