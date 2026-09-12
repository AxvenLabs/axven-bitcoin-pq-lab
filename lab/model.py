from __future__ import annotations

from dataclasses import dataclass, replace
from enum import Enum
import hashlib
import json


class Mode(str, Enum):
    LEGACY = "legacy"
    HYBRID = "hybrid"
    PQ = "pq"


@dataclass(frozen=True)
class Context:
    chain_id: str
    txid: str
    vout: int
    epoch: int
    destination_commitment: str
    mode: Mode

    def canonical_bytes(self) -> bytes:
        payload = {
            "chain_id": self.chain_id,
            "destination_commitment": self.destination_commitment,
            "epoch": self.epoch,
            "mode": self.mode.value,
            "txid": self.txid,
            "vout": self.vout,
        }
        encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
        return b"axven-bitcoin-pq-lab/v1|" + encoded

    def transcript_hash(self) -> str:
        return hashlib.sha256(self.canonical_bytes()).hexdigest()


@dataclass(frozen=True)
class Authorization:
    transcript_hash: str
    legacy_ok: bool = False
    pq_ok: bool = False


@dataclass(frozen=True)
class UtxoAuthState:
    mode: Mode
    epoch: int = 0

    def authorize(self, context: Context, auth: Authorization) -> bool:
        if context.mode is not self.mode:
            return False
        if context.epoch != self.epoch:
            return False
        if auth.transcript_hash != context.transcript_hash():
            return False
        if self.mode is Mode.LEGACY:
            return auth.legacy_ok
        if self.mode is Mode.HYBRID:
            return auth.legacy_ok and auth.pq_ok
        if self.mode is Mode.PQ:
            return auth.pq_ok
        return False

    def migrate(self, target: Mode) -> "UtxoAuthState":
        allowed = {
            Mode.LEGACY: Mode.HYBRID,
            Mode.HYBRID: Mode.PQ,
        }
        if allowed.get(self.mode) is not target:
            raise ValueError(f"forbidden migration: {self.mode.value}->{target.value}")
        return replace(self, mode=target, epoch=self.epoch + 1)
