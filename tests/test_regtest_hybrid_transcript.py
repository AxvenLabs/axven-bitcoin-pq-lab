import pytest

from scripts.regtest_hybrid_transcript import build_transcript, hybrid_gate


TXID = "11" * 32
MSG = "22" * 32


def test_transcript_is_deterministic_and_candidate_neutral():
    first = build_transcript(txid=TXID, vout=7, message_digest=MSG, candidate="ML-DSA-44")
    second = build_transcript(txid=TXID.upper(), vout=7, message_digest=MSG.upper(), candidate="ML-DSA-44")
    assert first == second
    assert first["research_only"] is True
    assert first["network"] == "regtest"
    assert first["endorsed_by_bitcoin_core"] is False
    assert first["mainnet_intended"] is False
    assert first["parameter_set_selected"] is False
    assert first["script_semantics_defined"] is False
    assert first["consensus_changed"] is False


def test_candidate_changes_transcript_without_selecting_winner():
    digests = {
        build_transcript(txid=TXID, vout=0, message_digest=MSG, candidate=name)["transcript_sha256"]
        for name in ("ML-DSA-44", "ML-DSA-65", "ML-DSA-87")
    }
    assert len(digests) == 3


@pytest.mark.parametrize(
    ("classical_valid", "pq_valid", "expected"),
    [(False, False, False), (False, True, False), (True, False, False), (True, True, True)],
)
def test_classical_and_pq_truth_table(classical_valid, pq_valid, expected):
    assert hybrid_gate(classical_valid=classical_valid, pq_valid=pq_valid) is expected


@pytest.mark.parametrize(
    "kwargs",
    [
        {"txid": "00", "vout": 0, "message_digest": MSG, "candidate": "ML-DSA-44"},
        {"txid": "zz" * 32, "vout": 0, "message_digest": MSG, "candidate": "ML-DSA-44"},
        {"txid": TXID, "vout": -1, "message_digest": MSG, "candidate": "ML-DSA-44"},
        {"txid": TXID, "vout": 2**32, "message_digest": MSG, "candidate": "ML-DSA-44"},
        {"txid": TXID, "vout": 0, "message_digest": "01", "candidate": "ML-DSA-44"},
        {"txid": TXID, "vout": 0, "message_digest": MSG, "candidate": "winner"},
    ],
)
def test_malformed_transcript_inputs_fail_closed(kwargs):
    with pytest.raises(ValueError):
        build_transcript(**kwargs)


def test_gate_rejects_truthy_non_boolean_inputs():
    with pytest.raises(TypeError):
        hybrid_gate(classical_valid=1, pq_valid=True)
    with pytest.raises(TypeError):
        hybrid_gate(classical_valid=True, pq_valid="yes")
