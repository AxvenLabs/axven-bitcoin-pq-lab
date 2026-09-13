import unittest

from scripts.benchmark_auth_material_size import (
    build_report,
    compact_size_len,
    parse_sizes,
    structural_case,
    witness_item_serialized_bytes,
)


class OpaqueAuthorizationMaterialSizeTests(unittest.TestCase):
    def test_compact_size_boundaries(self):
        self.assertEqual(compact_size_len(0), 1)
        self.assertEqual(compact_size_len(252), 1)
        self.assertEqual(compact_size_len(253), 3)
        self.assertEqual(compact_size_len(65535), 3)
        self.assertEqual(compact_size_len(65536), 5)
        self.assertEqual(compact_size_len(0xFFFFFFFF), 5)
        self.assertEqual(compact_size_len(0x100000000), 9)

    def test_boolean_and_negative_values_fail_closed(self):
        for value in (True, -1):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    compact_size_len(value)

    def test_witness_item_includes_length_prefix(self):
        self.assertEqual(witness_item_serialized_bytes(64), 65)
        self.assertEqual(witness_item_serialized_bytes(253), 256)

    def test_structural_case_is_marginal_not_full_transaction(self):
        case = structural_case(1024)
        self.assertEqual(case["length_prefix_bytes"], 3)
        self.assertEqual(case["serialized_witness_item_bytes"], 1027)
        self.assertEqual(case["marginal_weight_units"], 1027)
        self.assertEqual(case["marginal_vbytes_ceiling"], 257)

    def test_report_keeps_decision_gates_open(self):
        report = build_report([64, 1024, 4096])
        self.assertTrue(report["research_only"])
        self.assertFalse(report["endorsed_by_bitcoin_core"])
        self.assertFalse(report["mainnet_intended"])
        self.assertFalse(report["scheme_selected"])
        self.assertFalse(report["hybrid_semantics_selected"])
        self.assertEqual(report["network_scope"], "none-structural-model")

    def test_duplicate_sizes_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "unique"):
            build_report([64, 64])

    def test_parse_sizes(self):
        self.assertEqual(parse_sizes("64, 128,4096"), [64, 128, 4096])


if __name__ == "__main__":
    unittest.main()
