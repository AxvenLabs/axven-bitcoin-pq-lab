import copy,unittest
try:
 from scripts.regtest_chain_evidence import build_chain_evidence
 from scripts.regtest_mldsa_composition import build_composition
 from scripts.regtest_benchmark_evidence import build_benchmark_evidence
 from scripts.regtest_provenance_evidence import build_provenance,EXPECTED_COMMIT,EXPECTED_TAG,EXPECTED_TAG_OBJECT
 from scripts.regtest_e2e_evidence import build_e2e_evidence
 from scripts.validate_regtest_e2e_evidence import validate_e2e_evidence
except (ImportError,ModuleNotFoundError):
 raise unittest.SkipTest("requires pinned ML-DSA backend")
class T(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  chain=build_chain_evidence(txid="a"*64,vout=0,amount_btc="1.0",confirmations=1,block_hash="b"*64,block_height=102,tx_hex="00",tx_size=1,tx_weight=4,tx_vsize=1)
  comp=build_composition(txid="a"*64,vout=0,message_digest="c"*64); bench=build_benchmark_evidence(3)
  prov=build_provenance(repo_commit="d"*40,bitcoin_version="Bitcoin Core daemon version v31.1 bitcoind",source_commit=EXPECTED_COMMIT,tag=EXPECTED_TAG,tag_object=EXPECTED_TAG_OBJECT,bitcoind_sha256="e"*64,bitcoin_cli_sha256="f"*64,python_version="3.12.3",cryptography_version="48.0.0",openssl_version="OpenSSL test",os_name="Linux",machine="x86_64")
  cls.e=build_e2e_evidence(chain,comp,bench,prov)
 def test_ok(self): self.assertEqual(validate_e2e_evidence(self.e),self.e["e2e_evidence_sha256"])
 def reject(self,path,value):
  x=copy.deepcopy(self.e); cur=x
  for p in path[:-1]: cur=cur[p]
  cur[path[-1]]=value
  with self.assertRaises(ValueError): validate_e2e_evidence(x)
 def test_vout_tamper(self): self.reject(["outpoint","vout"],1)
 def test_chain_tamper(self): self.reject(["chain_evidence","confirmation","block_height"],103)
 def test_benchmark_tamper(self): self.reject(["benchmark_evidence","benchmark_report","candidates",0,"signature_bytes"],1)
 def test_candidate_tamper(self): self.reject(["benchmark_evidence","benchmark_report","cross_candidate_negative","all_rejected"],False)
 def test_provenance_tamper(self): self.reject(["provenance_evidence","openssl_version"],"tampered")
 def test_overclaim(self): self.reject(["bitcoin_core_modified"],True)
if __name__=="__main__": unittest.main()
