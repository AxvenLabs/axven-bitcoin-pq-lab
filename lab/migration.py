from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from .model import Mode, UtxoAuthState


class Event(str, Enum):
    ADVANCE = "advance"
    ROLLBACK = "rollback"
    REPLAY_OLD = "replay_old"
    SKIP = "skip"
    NOOP = "noop"


@dataclass(frozen=True)
class StepResult:
    before: UtxoAuthState
    event: Event
    after: UtxoAuthState
    accepted: bool
    reason: str


def apply_event(state: UtxoAuthState, event: Event) -> StepResult:
    """Apply a scheme-neutral migration event.

    This is deliberately a research state-machine simulator only. It does not
    model Bitcoin consensus, activation, Script, key recovery, or any concrete
    cryptographic primitive.
    """
    if event is Event.NOOP:
        return StepResult(state, event, state, True, "no state change")

    if event is Event.ROLLBACK:
        return StepResult(state, event, state, False, "rollback is fail-closed")

    if event is Event.REPLAY_OLD:
        return StepResult(state, event, state, False, "stale epoch replay is fail-closed")

    if event is Event.SKIP:
        return StepResult(state, event, state, False, "mode skipping is fail-closed")

    if event is Event.ADVANCE:
        target = {
            Mode.LEGACY: Mode.HYBRID,
            Mode.HYBRID: Mode.PQ,
        }.get(state.mode)
        if target is None:
            return StepResult(state, event, state, False, "pq is terminal in this abstract model")
        after = state.migrate(target)
        return StepResult(state, event, after, True, "monotonic one-step migration")

    raise ValueError(f"unsupported event: {event}")


def run_scenario(initial: UtxoAuthState, events: Iterable[Event]) -> list[StepResult]:
    state = initial
    results: list[StepResult] = []
    for event in events:
        result = apply_event(state, event)
        results.append(result)
        state = result.after
    return results


def invariant_monotonic(results: Iterable[StepResult]) -> bool:
    rank = {Mode.LEGACY: 0, Mode.HYBRID: 1, Mode.PQ: 2}
    for result in results:
        if rank[result.after.mode] < rank[result.before.mode]:
            return False
        if result.after.epoch < result.before.epoch:
            return False
        if result.accepted and result.event is Event.ADVANCE:
            if result.after.epoch != result.before.epoch + 1:
                return False
        elif result.after.epoch != result.before.epoch:
            return False
    return True
