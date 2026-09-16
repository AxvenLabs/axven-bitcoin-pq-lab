import copy
import unittest

from scripts.regtest_provenance_evidence import build_provenance
from scripts.validate_regtest_provenance_evidence import validate_provenance


class TestValidateRegtestProvenanceEvidence(unittest.TestCase):
    def report(self):
        return build_provenance(
            repo_commit="a" * 40,
            bitcoin_version="Bitcoin Core version v31.1",
            python_version="3.12.3",
            cryptography_version="48.0.0",
            os_name="Linux-WSL2",
            machine="x86_64",
        )

    def test_accepts_intact_report(self):
        report = self.report()
        self.assertEqual(validate_provenance(report), report["provenance_sha256"])

    def test_rejects_digest_tamper(self):
        report = self.report(); report["python_version"] = "9.9.9"
        with self.assertRaises(ValueError): validate_provenance(report)

    def test_rejects_bitcoin_pin_tamper_even_with_rehashed_digest(self):
        report = self.report(); report["bitcoin_core"]["commit_sha"] = "b" * 40
        report["provenance_sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "pin mismatch"): validate_provenance(report)

    def test_rejects_parameter_selection_overclaim(self):
        report = self.report(); report["parameter_set_selected"] = True
        with self.assertRaisesRegex(ValueError, "overclaim"): validate_provenance(report)

    def test_rejects_native_windows_resource_overclaim(self):
        report = self.report(); report["native_windows_resource_portability_demonstrated"] = True
        with self.assertRaisesRegex(ValueError, "overclaim"): validate_provenance(report)


if __name__ == "__main__":
    unittest.main()
