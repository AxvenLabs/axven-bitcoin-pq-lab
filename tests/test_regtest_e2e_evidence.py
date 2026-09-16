import copy,unittest
from scripts.regtest_e2e_evidence import build_e2e_evidence
from scripts.regtest_provenance_evidence import build_provenance,EXPECTED_COMMIT,EXPECTED_TAG,EXPECTED_TAG_OBJECT
class T(unittest.TestCase):
 def setUp(self):
  common={"research_only":True,"endorsed_by_bitcoin_core":False,"mainnet_intended":False,"bitcoin_core_modified":False,"parameter_set_selected":False}
  self.chain={**common,"chain_evidence_sha256":"1"*64,"outpoint":{"txid":"a"*64,"vout":0,"amount_btc":"1.0","confirmations":1},"confirmation":{"block_hash":"b"*64,"block_height":102},"transaction":{"raw_tx_sha256":"c"*64,"serialized_bytes":1,"weight":4,"vbytes":1}}
  self.comp={**common,"composition_sha256":"2"*64,"outpoint":{"txid":"a"*64,"vout":0},"hybrid_research_semantics":"classical-and-pq"}
  self.bench={**common,"benchmark_evidence_sha256":"3"*64,"correctness_oracle_separate":True,"native_windows_resource_portability_demonstrated":False,"candidate_order":["ML-DSA-44","ML-DSA-65","ML-DSA-87"]}
  self.prov=build_provenance(repo_commit="d"*40,bitcoin_version="Bitcoin Core daemon version v31.1 bitcoind",source_commit=EXPECTED_COMMIT,tag=EXPECTED_TAG,tag_object=EXPECTED_TAG_OBJECT,bitcoind_sha256="e"*64,bitcoin_cli_sha256="f"*64,python_version="3.12.3",cryptography_version="48.0.0",openssl_version="OpenSSL test",os_name="Linux",machine="x86_64")
 def test_deterministic(self): self.assertEqual(build_e2e_evidence(self.chain,self.comp,self.bench,self.prov),build_e2e_evidence(self.chain,self.comp,self.bench,self.prov))
 def test_outpoint_mismatch(self):
  c=copy.deepcopy(self.comp); c["outpoint"]["vout"]=1
  with self.assertRaises(ValueError): build_e2e_evidence(self.chain,c,self.bench,self.prov)
 def test_provenance_tamper(self):
  p=copy.deepcopy(self.prov); p["openssl_version"]="tampered"
  with self.assertRaises(ValueError): build_e2e_evidence(self.chain,self.comp,self.bench,p)
if __name__=="__main__": unittest.main()
