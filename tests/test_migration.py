import unittest

from lab.migration import Event, apply_event, invariant_monotonic, run_scenario
from lab.model import Mode, UtxoAuthState


class MigrationFailureTests(unittest.TestCase):
    def test_happy_path_is_monotonic(self):
        results = run_scenario(
            UtxoAuthState(Mode.LEGACY),
            [Event.ADVANCE, Event.ADVANCE],
        )
        self.assertEqual(results[-1].after, UtxoAuthState(Mode.PQ, epoch=2))
        self.assertTrue(invariant_monotonic(results))

    def test_rollback_fails_closed_without_state_change(self):
        state = UtxoAuthState(Mode.HYBRID, epoch=7)
        result = apply_event(state, Event.ROLLBACK)
        self.assertFalse(result.accepted)
        self.assertEqual(result.after, state)

    def test_stale_replay_fails_closed_without_state_change(self):
        state = UtxoAuthState(Mode.HYBRID, epoch=4)
        result = apply_event(state, Event.REPLAY_OLD)
        self.assertFalse(result.accepted)
        self.assertEqual(result.after, state)

    def test_skip_fails_closed_without_state_change(self):
        state = UtxoAuthState(Mode.LEGACY, epoch=0)
        result = apply_event(state, Event.SKIP)
        self.assertFalse(result.accepted)
        self.assertEqual(result.after, state)

    def test_advance_from_terminal_mode_fails_closed(self):
        state = UtxoAuthState(Mode.PQ, epoch=2)
        result = apply_event(state, Event.ADVANCE)
        self.assertFalse(result.accepted)
        self.assertEqual(result.after, state)

    def test_rejected_events_do_not_change_epoch(self):
        results = run_scenario(
            UtxoAuthState(Mode.LEGACY),
            [Event.REPLAY_OLD, Event.SKIP, Event.ROLLBACK, Event.NOOP],
        )
        self.assertTrue(invariant_monotonic(results))
        self.assertTrue(all(step.after.epoch == 0 for step in results))


if __name__ == "__main__":
    unittest.main()
