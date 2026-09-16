import unittest
from scripts.regtest_provenance_evidence import build_provenance,EXPECTED_COMMIT,EXPECTED_TAG,EXPECTED_TAG_OBJECT
class TestRegtestProvenanceEvidence(unittest.TestCase):
    def kwargs(self): return {"repo_commit":"a"*40,"bitcoin_version":"Bitcoin Core daemon version v31.1 bitcoind","source_commit":EXPECTED_COMMIT,"tag":EXPECTED_TAG,"tag_object":EXPECTED_TAG_OBJECT,"bitcoind_sha256":"b"*64,"bitcoin_cli_sha256":"c"*64,"python_version":"3.12.3","cryptography_version":"48.0.0","openssl_version":"OpenSSL test","os_name":"Linux-WSL2","machine":"x86_64"}
    def test_deterministic_and_safe(self):
        a=build_provenance(**self.kwargs()); self.assertEqual(a,build_provenance(**self.kwargs())); self.assertFalse(a["parameter_set_selected"]); self.assertEqual(a["bitcoin_core"]["tag_object"],EXPECTED_TAG_OBJECT)
    def test_rejects_source_drift(self):
        k=self.kwargs(); k["source_commit"]="0"*40
        with self.assertRaises(ValueError): build_provenance(**k)
    def test_rejects_missing_openssl(self):
        k=self.kwargs(); k["openssl_version"]=""
        with self.assertRaises(ValueError): build_provenance(**k)
if __name__=="__main__": unittest.main()
