import json
import unittest

from lab.model import Authorization, Context, Mode, UtxoAuthState
from lab.vectors import canonical_vector_json, deterministic_vectors, vector_document


class TestVectors(unittest.TestCase):
    def test_document_is_deterministic(self) -> None:
        first = canonical_vector_json()
        second = canonical_vector_json()
        self.assertEqual(first, second)
        self.assertEqual(json.loads(first), vector_document())

    def test_no_scheme_is_selected(self) -> None:
        self.assertIsNone(vector_document()["cryptographic_scheme"])

    def test_vectors_execute_as_declared(self) -> None:
        for vector in deterministic_vectors():
            with self.subTest(vector=vector["name"]):
                state_data = vector["state"]
                context_data = vector["context"]
                auth_data = vector["authorization"]

                state = UtxoAuthState(
                    mode=Mode(state_data["mode"]), epoch=state_data["epoch"]
                )
                context = Context(
                    chain_id=context_data["chain_id"],
                    txid=context_data["txid"],
                    vout=context_data["vout"],
                    epoch=context_data["epoch"],
                    destination_commitment=context_data["destination_commitment"],
                    mode=Mode(context_data["mode"]),
                )
                auth = Authorization(**auth_data)
                self.assertEqual(state.authorize(context, auth), vector["expected"])

    def test_vector_names_are_unique(self) -> None:
        names = [vector["name"] for vector in deterministic_vectors()]
        self.assertEqual(len(names), len(set(names)))


if __name__ == "__main__":
    unittest.main()
