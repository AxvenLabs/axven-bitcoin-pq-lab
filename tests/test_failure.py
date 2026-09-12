import unittest

from lab.failure import CrashPoint, MigrationRecord, simulate_crash
from lab.model import Mode, UtxoAuthState


class AtomicMigrationFailureTests(unittest.TestCase):
    def test_precommit_crashes_expose_only_old_state(self):
        before = UtxoAuthState(Mode.LEGACY, epoch=0)
        for point in (
            CrashPoint.BEFORE_PREPARE,
            CrashPoint.AFTER_PREPARE,
            CrashPoint.BEFORE_COMMIT,
        ):
            with self.subTest(point=point.value):
                self.assertEqual(simulate_crash(before, Mode.HYBRID, point), before)

    def test_postcommit_crash_exposes_only_new_state(self):
        before = UtxoAuthState(Mode.LEGACY, epoch=0)
        observed = simulate_crash(before, Mode.HYBRID, CrashPoint.AFTER_COMMIT)
        self.assertEqual(observed, UtxoAuthState(Mode.HYBRID, epoch=1))

    def test_failure_harness_never_exposes_prepared_intermediate_state(self):
        before = UtxoAuthState(Mode.HYBRID, epoch=7)
        prepared = before.migrate(Mode.PQ)

        for point in CrashPoint:
            with self.subTest(point=point.value):
                observed = simulate_crash(before, Mode.PQ, point)
                self.assertIn(observed, (before, prepared))

    def test_invalid_transition_fails_without_visible_mutation(self):
        before = UtxoAuthState(Mode.LEGACY, epoch=3)
        for target in (Mode.LEGACY, Mode.PQ):
            with self.subTest(target=target.value):
                record = MigrationRecord(before=before, target=target)
                with self.assertRaises(ValueError):
                    record.prepare()
                self.assertEqual(record.visible_state(), before)

    def test_commit_requires_prepare(self):
        record = MigrationRecord(
            before=UtxoAuthState(Mode.LEGACY, epoch=0),
            target=Mode.HYBRID,
        )
        with self.assertRaises(ValueError):
            record.commit()
        self.assertEqual(record.visible_state(), UtxoAuthState(Mode.LEGACY, epoch=0))

    def test_prepare_and_commit_are_single_advance_operations(self):
        record = MigrationRecord(
            before=UtxoAuthState(Mode.LEGACY, epoch=0),
            target=Mode.HYBRID,
        ).prepare()
        with self.assertRaises(ValueError):
            record.prepare()

        committed = record.commit()
        with self.assertRaises(ValueError):
            committed.commit()
        self.assertEqual(committed.visible_state(), UtxoAuthState(Mode.HYBRID, epoch=1))


if __name__ == "__main__":
    unittest.main()
