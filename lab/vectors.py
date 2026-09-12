from __future__ import annotations

from dataclasses import asdict
import json
from typing import Iterable

from lab.model import Authorization, Context, Mode, UtxoAuthState


VECTOR_VERSION = 1


def _context(*, mode: Mode, epoch: int = 0) -> Context:
    return Context(
        chain_id="bitcoin-regtest-research",
        txid="11" * 32,
        vout=1,
        epoch=epoch,
        destination_commitment="22" * 32,
        mode=mode,
    )


def deterministic_vectors() -> list[dict[str, object]]:
    """Return implementation-independent positive and negative model vectors.

    These vectors exercise transcript binding and migration semantics only. They
    intentionally do not instantiate, benchmark, or imply a post-quantum
    signature scheme.
    """

    vectors: list[dict[str, object]] = []

    for mode, legacy_ok, pq_ok, expected in (
        (Mode.LEGACY, True, False, True),
        (Mode.LEGACY, False, True, False),
        (Mode.HYBRID, True, True, True),
        (Mode.HYBRID, True, False, False),
        (Mode.HYBRID, False, True, False),
        (Mode.PQ, False, True, True),
        (Mode.PQ, True, False, False),
    ):
        epoch = 0 if mode is Mode.LEGACY else (1 if mode is Mode.HYBRID else 2)
        context = _context(mode=mode, epoch=epoch)
        state = UtxoAuthState(mode=mode, epoch=epoch)
        auth = Authorization(
            transcript_hash=context.transcript_hash(),
            legacy_ok=legacy_ok,
            pq_ok=pq_ok,
        )
        vectors.append(
            {
                "name": f"{mode.value}-auth-l{int(legacy_ok)}-p{int(pq_ok)}",
                "state": {"mode": state.mode.value, "epoch": state.epoch},
                "context": {
                    **asdict(context),
                    "mode": context.mode.value,
                },
                "authorization": asdict(auth),
                "expected": expected,
            }
        )

    baseline = _context(mode=Mode.HYBRID, epoch=1)
    good_auth = Authorization(
        transcript_hash=baseline.transcript_hash(), legacy_ok=True, pq_ok=True
    )

    tampered_contexts: Iterable[tuple[str, Context]] = (
        (
            "wrong-chain",
            Context(
                chain_id="other-regtest",
                txid=baseline.txid,
                vout=baseline.vout,
                epoch=baseline.epoch,
                destination_commitment=baseline.destination_commitment,
                mode=baseline.mode,
            ),
        ),
        (
            "wrong-outpoint",
            Context(
                chain_id=baseline.chain_id,
                txid="33" * 32,
                vout=baseline.vout,
                epoch=baseline.epoch,
                destination_commitment=baseline.destination_commitment,
                mode=baseline.mode,
            ),
        ),
        (
            "wrong-destination",
            Context(
                chain_id=baseline.chain_id,
                txid=baseline.txid,
                vout=baseline.vout,
                epoch=baseline.epoch,
                destination_commitment="44" * 32,
                mode=baseline.mode,
            ),
        ),
    )

    state = UtxoAuthState(mode=Mode.HYBRID, epoch=1)
    for name, context in tampered_contexts:
        vectors.append(
            {
                "name": name,
                "state": {"mode": state.mode.value, "epoch": state.epoch},
                "context": {**asdict(context), "mode": context.mode.value},
                "authorization": asdict(good_auth),
                "expected": False,
            }
        )

    return vectors


def vector_document() -> dict[str, object]:
    return {
        "format": "axven-bitcoin-pq-lab-test-vectors",
        "version": VECTOR_VERSION,
        "scope": "authorization-state-model-only",
        "cryptographic_scheme": None,
        "vectors": deterministic_vectors(),
    }


def canonical_vector_json() -> str:
    return json.dumps(vector_document(), sort_keys=True, separators=(",", ":")) + "\n"
