import itertools
import unittest

from lab.migration import Event, apply_event, run_scenario
from lab.model import Mode, UtxoAuthState


class ModelInvariantAuditTests(unittest.TestCase):
    def test_rejected_events_preserve_state_for_small_epoch_space(self):
        for mode in Mode:
            for epoch in range(4):
                state = UtxoAuthState(mode=mode, epoch=epoch)
                for event in Event:
                    result = apply_event(state, event)
                    if not result.accepted:
                        with self.subTest(mode=mode.value, epoch=epoch, event=event.value):
                            self.assertEqual(result.after, state)

    def test_accepted_transition_never_decreases_epoch(self):
        for mode in Mode:
            for epoch in range(4):
                state = UtxoAuthState(mode=mode, epoch=epoch)
                for event in Event:
                    result = apply_event(state, event)
                    if result.accepted:
                        with self.subTest(mode=mode.value, epoch=epoch, event=event.value):
                            self.assertGreaterEqual(result.after.epoch, state.epoch)

    def test_all_short_event_sequences_are_deterministic(self):
        initial_states = [
            UtxoAuthState(Mode.LEGACY, epoch=0),
            UtxoAuthState(Mode.HYBRID, epoch=3),
            UtxoAuthState(Mode.PQ, epoch=9),
        ]
        events = list(Event)
        for length in range(5):
            for sequence in itertools.product(events, repeat=length):
                for initial in initial_states:
                    with self.subTest(
                        initial=(initial.mode.value, initial.epoch),
                        sequence=[event.value for event in sequence],
                    ):
                        first = run_scenario(initial, list(sequence))
                        second = run_scenario(initial, list(sequence))
                        self.assertEqual(first, second)

    def test_rejected_event_is_idempotent(self):
        for mode in Mode:
            state = UtxoAuthState(mode=mode, epoch=2)
            for event in Event:
                first = apply_event(state, event)
                if first.accepted:
                    continue
                second = apply_event(first.after, event)
                with self.subTest(mode=mode.value, event=event.value):
                    self.assertFalse(second.accepted)
                    self.assertEqual(second.after, state)

    def test_only_mode_advance_can_change_visible_state(self):
        for mode in Mode:
            for epoch in range(3):
                state = UtxoAuthState(mode=mode, epoch=epoch)
                for event in Event:
                    result = apply_event(state, event)
                    if result.after != state:
                        with self.subTest(mode=mode.value, epoch=epoch, event=event.value):
                            self.assertEqual(event, Event.ADVANCE)
                            self.assertTrue(result.accepted)
                            self.assertEqual(result.after.epoch, epoch + 1)


if __name__ == "__main__":
    unittest.main()
