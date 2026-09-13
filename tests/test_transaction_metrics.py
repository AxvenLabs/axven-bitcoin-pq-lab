import unittest

from scripts.transaction_metrics import extract_metrics


TXID = "a" * 64


def sample_tx(**overrides):
    tx = {
        "txid": TXID,
        "size": 222,
        "vsize": 141,
        "weight": 561,
        "vin": [{"txinwitness": ["30" * 72, "02" * 33]}],
        "vout": [{}, {}],
    }
    tx.update(overrides)
    return tx


class TransactionMetricTests(unittest.TestCase):
    def test_extracts_structural_metrics(self):
        metrics = extract_metrics(sample_tx())
        self.assertEqual(metrics["serialized_size_bytes"], 222)
        self.assertEqual(metrics["virtual_size_vbytes"], 141)
        self.assertEqual(metrics["weight_units"], 561)
        self.assertEqual(metrics["input_count"], 1)
        self.assertEqual(metrics["output_count"], 2)
        self.assertEqual(metrics["witness_input_count"], 1)
        self.assertEqual(metrics["witness_item_bytes"], [72, 33])
        self.assertEqual(metrics["total_witness_item_bytes"], 105)
        self.assertTrue(metrics["research_only"])

    def test_rejects_inconsistent_vsize(self):
        with self.assertRaisesRegex(ValueError, "ceil"):
            extract_metrics(sample_tx(vsize=140))

    def test_rejects_impossible_weight(self):
        with self.assertRaisesRegex(ValueError, "four times"):
            extract_metrics(sample_tx(weight=889, vsize=223))

    def test_rejects_malformed_txid(self):
        with self.assertRaisesRegex(ValueError, "txid"):
            extract_metrics(sample_tx(txid="ABC"))

    def test_rejects_bad_witness_encoding(self):
        with self.assertRaisesRegex(ValueError, "witness items"):
            extract_metrics(sample_tx(vin=[{"txinwitness": ["xyz"]}]))

    def test_rejects_boolean_numeric_fields(self):
        with self.assertRaisesRegex(ValueError, "positive integer"):
            extract_metrics(sample_tx(size=True))


if __name__ == "__main__":
    unittest.main()
