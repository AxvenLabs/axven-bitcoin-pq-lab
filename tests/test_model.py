import unittest

from lab.model import Authorization, Context, Mode, UtxoAuthState


class MigrationModelTests(unittest.TestCase):
    def ctx(self, state: UtxoAuthState, **overrides) -> Context:
        values = {
            "chain_id": "bitcoin-regtest-lab",
            "txid": "11" * 32,
            "vout": 0,
            "epoch": state.epoch,
            "destination_commitment": "dest-A",
            "mode": state.mode,
        }
        values.update(overrides)
        return Context(**values)

    def auth(self, ctx: Context, legacy=False, pq=False) -> Authorization:
        return Authorization(ctx.transcript_hash(), legacy_ok=legacy, pq_ok=pq)

    def test_legacy_accepts_legacy_authorization(self):
        state = UtxoAuthState(Mode.LEGACY)
        ctx = self.ctx(state)
        self.assertTrue(state.authorize(ctx, self.auth(ctx, legacy=True)))
        self.assertFalse(state.authorize(ctx, self.auth(ctx, pq=True)))

    def test_hybrid_requires_both(self):
        state = UtxoAuthState(Mode.HYBRID, epoch=1)
        ctx = self.ctx(state)
        self.assertFalse(state.authorize(ctx, self.auth(ctx, legacy=True)))
        self.assertFalse(state.authorize(ctx, self.auth(ctx, pq=True)))
        self.assertTrue(state.authorize(ctx, self.auth(ctx, legacy=True, pq=True)))

    def test_pq_accepts_pq_only(self):
        state = UtxoAuthState(Mode.PQ, epoch=2)
        ctx = self.ctx(state)
        self.assertTrue(state.authorize(ctx, self.auth(ctx, pq=True)))
        self.assertFalse(state.authorize(ctx, self.auth(ctx, legacy=True)))

    def test_replay_rejected_across_chain_id(self):
        state = UtxoAuthState(Mode.HYBRID, epoch=1)
        original = self.ctx(state)
        auth = self.auth(original, legacy=True, pq=True)
        replay = self.ctx(state, chain_id="other-regtest")
        self.assertFalse(state.authorize(replay, auth))

    def test_replay_rejected_across_outpoint(self):
        state = UtxoAuthState(Mode.HYBRID, epoch=1)
        original = self.ctx(state)
        auth = self.auth(original, legacy=True, pq=True)
        replay = self.ctx(state, vout=1)
        self.assertFalse(state.authorize(replay, auth))

    def test_replay_rejected_across_epoch(self):
        state = UtxoAuthState(Mode.HYBRID, epoch=1)
        original = self.ctx(state)
        auth = self.auth(original, legacy=True, pq=True)
        replay = self.ctx(state, epoch=2)
        self.assertFalse(state.authorize(replay, auth))

    def test_replay_rejected_across_destination(self):
        state = UtxoAuthState(Mode.HYBRID, epoch=1)
        original = self.ctx(state)
        auth = self.auth(original, legacy=True, pq=True)
        replay = self.ctx(state, destination_commitment="dest-B")
        self.assertFalse(state.authorize(replay, auth))

    def test_monotonic_migration(self):
        state = UtxoAuthState(Mode.LEGACY)
        state = state.migrate(Mode.HYBRID)
        self.assertEqual((state.mode, state.epoch), (Mode.HYBRID, 1))
        state = state.migrate(Mode.PQ)
        self.assertEqual((state.mode, state.epoch), (Mode.PQ, 2))

    def test_downgrade_and_skip_are_rejected_without_mutation(self):
        original = UtxoAuthState(Mode.LEGACY)
        for target in (Mode.PQ, Mode.LEGACY):
            with self.assertRaises(ValueError):
                original.migrate(target)
        self.assertEqual(original, UtxoAuthState(Mode.LEGACY))

        pq = UtxoAuthState(Mode.PQ, epoch=2)
        with self.assertRaises(ValueError):
            pq.migrate(Mode.HYBRID)
        self.assertEqual(pq, UtxoAuthState(Mode.PQ, epoch=2))


if __name__ == "__main__":
    unittest.main()
