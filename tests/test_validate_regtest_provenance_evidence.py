import unittest
from scripts.regtest_provenance_evidence import build_provenance,EXPECTED_COMMIT,EXPECTED_TAG,EXPECTED_TAG_OBJECT
from scripts.validate_regtest_provenance_evidence import validate_provenance
class T(unittest.TestCase):
 def report(self): return build_provenance(repo_commit="a"*40,bitcoin_version="Bitcoin Core daemon version v31.1 bitcoind",source_commit=EXPECTED_COMMIT,tag=EXPECTED_TAG,tag_object=EXPECTED_TAG_OBJECT,bitcoind_sha256="b"*64,bitcoin_cli_sha256="c"*64,python_version="3.12.3",cryptography_version="48.0.0",openssl_version="OpenSSL test",os_name="Linux-WSL2",machine="x86_64")
 def test_ok(self):
  r=self.report(); self.assertEqual(validate_provenance(r),r["provenance_sha256"])
 def test_runtime_tamper(self):
  r=self.report(); r["openssl_version"]="tampered"
  with self.assertRaises(ValueError): validate_provenance(r)
 def test_tag_object_tamper(self):
  r=self.report(); r["bitcoin_core"]["tag_object"]="0"*40
  with self.assertRaisesRegex(ValueError,"pin mismatch"): validate_provenance(r)
 def test_binary_digest_tamper(self):
  r=self.report(); r["bitcoin_core"]["bitcoind_sha256"]="0"*64
  with self.assertRaises(ValueError): validate_provenance(r)
 def test_overclaim(self):
  r=self.report(); r["parameter_set_selected"]=True
  with self.assertRaisesRegex(ValueError,"overclaim"): validate_provenance(r)
if __name__=="__main__": unittest.main()
