import copy
import unittest

from scripts.regtest_provenance_evidence import build_provenance


class TestRegtestProvenanceEvidence(unittest.TestCase):
    def kwargs(self):
        return {
            "repo_commit": "a" * 40,
            "bitcoin_version": "Bitcoin Core version v31.1",
            "python_version": "3.12.3",
            "cryptography_version": "48.0.0",
            "os_name": "Linux-6.6-WSL2",
            "machine": "x86_64",
        }

    def test_deterministic_and_boundary_safe(self):
        a = build_provenance(**self.kwargs())
        b = build_provenance(**self.kwargs())
        self.assertEqual(a, b)
        self.assertFalse(a["parameter_set_selected"])
        self.assertFalse(a["bitcoin_core_validates_mldsa"])
        self.assertFalse(a["native_windows_resource_portability_demonstrated"])

    def test_rejects_wrong_bitcoin_version(self):
        k = self.kwargs(); k["bitcoin_version"] = "Bitcoin Core version v31.0"
        with self.assertRaises(ValueError):
            build_provenance(**k)

    def test_rejects_invalid_repo_commit(self):
        k = self.kwargs(); k["repo_commit"] = "not-a-sha"
        with self.assertRaises(ValueError):
            build_provenance(**k)

    def test_rejects_missing_runtime_identity(self):
        k = self.kwargs(); k["machine"] = ""
        with self.assertRaises(ValueError):
            build_provenance(**k)


if __name__ == "__main__":
    unittest.main()
