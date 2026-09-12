from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from lab.model import Mode, UtxoAuthState


class CrashPoint(str, Enum):
    BEFORE_PREPARE = "before_prepare"
    AFTER_PREPARE = "after_prepare"
    BEFORE_COMMIT = "before_commit"
    AFTER_COMMIT = "after_commit"


@dataclass(frozen=True)
class MigrationRecord:
    before: UtxoAuthState
    target: Mode
    prepared: UtxoAuthState | None = None
    committed: bool = False

    def prepare(self) -> "MigrationRecord":
        if self.prepared is not None or self.committed:
            raise ValueError("migration record already advanced")
        candidate = self.before.migrate(self.target)
        return MigrationRecord(
            before=self.before,
            target=self.target,
            prepared=candidate,
            committed=False,
        )

    def commit(self) -> "MigrationRecord":
        if self.prepared is None:
            raise ValueError("cannot commit before prepare")
        if self.committed:
            raise ValueError("migration record already committed")
        return MigrationRecord(
            before=self.before,
            target=self.target,
            prepared=self.prepared,
            committed=True,
        )

    def visible_state(self) -> UtxoAuthState:
        # This is a research harness, not a persistence design. Prepared state is
        # intentionally invisible until commit so crash tests can assert an
        # atomic old-or-new observation contract without choosing Bitcoin
        # storage, consensus, activation, or recovery semantics.
        if self.committed:
            assert self.prepared is not None
            return self.prepared
        return self.before


def simulate_crash(before: UtxoAuthState, target: Mode, crash_point: CrashPoint) -> UtxoAuthState:
    record = MigrationRecord(before=before, target=target)

    if crash_point is CrashPoint.BEFORE_PREPARE:
        return record.visible_state()

    record = record.prepare()
    if crash_point in (CrashPoint.AFTER_PREPARE, CrashPoint.BEFORE_COMMIT):
        return record.visible_state()

    record = record.commit()
    if crash_point is CrashPoint.AFTER_COMMIT:
        return record.visible_state()

    raise AssertionError(f"unhandled crash point: {crash_point}")
