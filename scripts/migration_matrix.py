from __future__ import annotations

import argparse
import json

from lab.migration import Event, run_scenario
from lab.model import Mode, UtxoAuthState


SCENARIOS = {
    "happy_path": [Event.ADVANCE, Event.ADVANCE],
    "rollback_after_hybrid": [Event.ADVANCE, Event.ROLLBACK],
    "stale_replay_after_hybrid": [Event.ADVANCE, Event.REPLAY_OLD],
    "skip_from_legacy": [Event.SKIP],
    "advance_past_pq": [Event.ADVANCE, Event.ADVANCE, Event.ADVANCE],
}


def export() -> dict:
    output = {"schema": "axven-bitcoin-pq-lab/migration-matrix/v1", "scenarios": {}}
    for name, events in SCENARIOS.items():
        steps = run_scenario(UtxoAuthState(Mode.LEGACY), events)
        output["scenarios"][name] = [
            {
                "before": {"mode": step.before.mode.value, "epoch": step.before.epoch},
                "event": step.event.value,
                "accepted": step.accepted,
                "after": {"mode": step.after.mode.value, "epoch": step.after.epoch},
                "reason": step.reason,
            }
            for step in steps
        ]
    return output


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()
    encoded = json.dumps(export(), sort_keys=True, indent=2) + "\n"
    if args.output:
        with open(args.output, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(encoded)
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
