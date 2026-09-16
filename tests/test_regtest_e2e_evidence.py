import copy
import unittest

from scripts.regtest_e2e_evidence import build_e2e_evidence


class TestRegtestE2EEvidence(unittest.TestCase):
    def setUp(self):
        common = {
            "research_only": True,
            "endorsed_by_bitcoin_core": False,
            "mainnet_intended": False,
            "bitcoin_core_modified": False,
            "parameter_set_selected": False,
        }
        self.chain = {**common, "chain_evidence_sha256": "1" * 64,
                      "outpoint": {"txid": "a" * 64, "vout": 0},
                      "confirmation": {"block_hash": "b" * 64, "block_height": 102},
                      "transaction": {"raw_tx_sha256": "c" * 64, "serialized_bytes": 100,
                                      "weight": 400, "vbytes": 100}}
        self.composition = {**common, "composition_sha256": "2" * 64,
                            "outpoint": {"txid": "a" * 64, "vout": 0},
                            "hybrid_research_semantics": "classical-and-pq"}
        self.benchmark = {**common, "benchmark_evidence_sha256": "3" * 64,
                          "correctness_oracle_separate": True,
                          "native_windows_resource_portability_demonstrated": False,
                          "candidate_order": ["ML-DSA-44", "ML-DSA-65", "ML-DSA-87"]}

    def test_deterministic_envelope(self):
        a = build_e2e_evidence(self.chain, self.composition, self.benchmark)
        b = build_e2e_evidence(self.chain, self.composition, self.benchmark)
        self.assertEqual(a, b)
        self.assertFalse(a["parameter_set_selected"])
        self.assertFalse(a["bitcoin_core_validates_mldsa"])

    def test_rejects_outpoint_mismatch(self):
        altered = copy.deepcopy(self.composition)
        altered["outpoint"]["vout"] = 1
        with self.assertRaises(ValueError):
            build_e2e_evidence(self.chain, altered, self.benchmark)

    def test_rejects_boundary_drift(self):
        altered = copy.deepcopy(self.benchmark)
        altered["parameter_set_selected"] = True
        with self.assertRaises(ValueError):
            build_e2e_evidence(self.chain, self.composition, altered)

    def test_rejects_windows_portability_overclaim(self):
        altered = copy.deepcopy(self.benchmark)
        altered["native_windows_resource_portability_demonstrated"] = True
        with self.assertRaises(ValueError):
            build_e2e_evidence(self.chain, self.composition, altered)


if __name__ == "__main__":
    unittest.main()
