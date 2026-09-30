"""Regression tests for the bit-level front candidates (design optimization).

Run: OPENBLAS_NUM_THREADS=1 python -m unittest -q tests.fixed_rule.design_optimization.test_front_candidate
"""
import inspect
import random
import unittest
from dataclasses import replace

import numpy as np

from gacsca.fixed_rule.design_optimization import (candidates, codec, compiler,
                                                    machine, maintenance, rule)
from gacsca.fixed_rule.design_optimization.netlist import Net, Compiled

CANDIDATE = 'R1'


def cand():
    return candidates.load(CANDIDATE)


class RuleIdentityTest(unittest.TestCase):
    def test_no_depth_parameter_anywhere(self):
        """No executable entry point accepts a hierarchy depth or level."""
        fns = [rule.build, rule.Params, machine.Candidate.step_numpy,
               machine.Candidate.run_numpy, machine.CKernel.run, machine.CKernel.run_packed,
               codec.encode, codec.decode, compiler.compile_candidate]
        for fn in fns:
            names = set(inspect.signature(fn).parameters)
            self.assertFalse(names & {'depth', 'level', 'levels'}, fn)
        self.assertFalse({'depth', 'level'} & set(f for f, _ in rule.schema(cand().p)))

    def test_same_width_and_rule_at_both_levels(self):
        c = cand()
        rng = np.random.default_rng(1)
        top = codec.random_upper(c, 1, rng)
        lvl1 = codec.encode(c, top)
        lvl0 = codec.encode(c, lvl1)
        self.assertEqual(top.shape[0], lvl1.shape[0])
        self.assertEqual(lvl1.shape[0], lvl0.shape[0])
        self.assertEqual(lvl0.shape[0], rule.width(c.p))
        self.assertTrue(np.array_equal(codec.decode(c, codec.decode(c, lvl0)), top))

    def test_netlist_inputs_within_radius_five(self):
        c = cand()
        for name in c.comp.inputs:
            if name[0] == 'x':
                self.assertLessEqual(abs(name[1]), 5, name)
            else:
                self.assertEqual(name[0], 'I')

    def test_cached_rom_matches_recipe_and_netlist(self):
        c = cand()
        p, layout, prog = candidates.build(CANDIDATE)
        self.assertTrue(np.array_equal(c.rom, prog.rom))
        self.assertTrue(np.array_equal(c.layout, layout))
        self.assertEqual(c.comp.digest, rule.cached(p)[1].digest)


class MaintenanceTest(unittest.TestCase):
    def test_matches_existing_candidate_b_code(self):
        from gacsca.fixed_rule import stream28_holder_core as core
        k, m = 13, 28
        Q, U = 1 << k, 1 << m
        n = Net()
        cells = {j: dict(addr=[n.input(('c', j, 'addr', i)) for i in range(k)],
                         age=[n.input(('c', j, 'age', i)) for i in range(m)],
                         **{f: n.input(('c', j, f, 0)) for f in ('f1', 'f2', 'wf1', 'wf2')})
                 for j in range(-5, 6)}
        out = maintenance.build(n, cells, k, m)
        for nm in ('addr', 'age'):
            for i, b in enumerate(out[nm]):
                n.set_output((nm, i), b)
        n.set_output(('f1', 0), out['f1'])
        n.set_output(('f2', 0), out['f2'])
        comp = Compiled(n)
        rng = random.Random(7)
        for _ in range(600):
            ba, bt = rng.randrange(Q), rng.randrange(U)
            cs = {}
            for j in range(-5, 6):
                a, t = (ba + j) % Q, bt
                if rng.random() < 0.25:
                    a = rng.randrange(Q)
                if rng.random() < 0.25:
                    t = (t + rng.choice([-1, 1, 16, 5])) % U
                cs[j] = dict(addr=a, age=t, f1=int(rng.random() < .3), f2=int(rng.random() < .3),
                             wf1=int(rng.random() < .2), wf2=int(rng.random() < .2))
            vals = {}
            for j in range(-5, 6):
                for i in range(k):
                    vals[('c', j, 'addr', i)] = (cs[j]['addr'] >> i) & 1
                for i in range(m):
                    vals[('c', j, 'age', i)] = (cs[j]['age'] >> i) & 1
                for f in ('f1', 'f2', 'wf1', 'wf2'):
                    vals[('c', j, f, 0)] = cs[j][f]
            r = comp.evaluate_scalar(vals)
            got = dict(address=sum(r[('addr', i)] << i for i in range(k)),
                       age=sum(r[('age', i)] << i for i in range(m)), f1=r[('f1', 0)], f2=r[('f2', 0)])
            ref = core.maintenance(tuple(core.Cell(address=cs[j]['addr'], age=cs[j]['age'],
                                                   f1=cs[j]['f1'], f2=cs[j]['f2'],
                                                   wf1=cs[j]['wf1'], wf2=cs[j]['wf2'])
                                         for j in range(-5, 6)))
            self.assertEqual(got, ref)


class ExactQMaintenanceTest(unittest.TestCase):
    """Non-power-of-two colony size: Addresses mod Q, Age packed as
    (tick mod Q, tick // Q). The netlist must equal the integer reference
    `maintenance_scalar` (itself checked against the independent candidate-B
    code for Q = 2^13) on structured random neighbourhoods, including the
    Address wrap at Q-1 -> 0 and the Age wrap at U-1 -> 0."""

    def test_exact_q_matches_integer_reference(self):
        k, Q, nb = 10, 576, 1000
        m = k + (nb - 1).bit_length()
        U = nb * Q
        code = lambda t: ((t // Q) << k) | (t % Q)
        uncode = lambda v: (v >> k) * Q + (v & ((1 << k) - 1))
        n = Net()
        cells = {j: dict(addr=[n.input(('c', j, 'addr', i)) for i in range(k)],
                         age=[n.input(('c', j, 'age', i)) for i in range(m)],
                         **{f: n.input(('c', j, f, 0)) for f in ('f1', 'f2', 'wf1', 'wf2')})
                 for j in range(-5, 6)}
        out = maintenance.build(n, cells, k, m, Q=Q, nb=nb)
        for nm in ('addr', 'age', 'age_now'):
            for i, b in enumerate(out[nm]):
                n.set_output((nm, i), b)
        n.set_output(('f1', 0), out['f1'])
        n.set_output(('f2', 0), out['f2'])
        comp = Compiled(n)
        rng = random.Random(11)
        for trial in range(1500):
            ba = rng.choice([rng.randrange(Q), Q - 3, Q - 1, 0, 2])
            bt = rng.choice([rng.randrange(U), U - 1, U - 2, Q - 1, 15, 31, Q * 7 - 1])
            cs = {}
            for j in range(-5, 6):
                a, t = (ba + j) % Q, bt
                if rng.random() < 0.25:
                    a = rng.randrange(Q)
                if rng.random() < 0.25:
                    t = (t + rng.choice([-1, 1, 16, 5, Q])) % U
                cs[j] = dict(addr=a, age=t, f1=int(rng.random() < .3), f2=int(rng.random() < .3),
                             wf1=int(rng.random() < .2), wf2=int(rng.random() < .2))
            vals = {}
            for j in range(-5, 6):
                for i in range(k):
                    vals[('c', j, 'addr', i)] = (cs[j]['addr'] >> i) & 1
                for i in range(m):
                    vals[('c', j, 'age', i)] = (code(cs[j]['age']) >> i) & 1
                for f in ('f1', 'f2', 'wf1', 'wf2'):
                    vals[('c', j, f, 0)] = cs[j][f]
            r = comp.evaluate_scalar(vals)
            word = lambda nm, w: sum(r[(nm, i)] << i for i in range(w))
            got = dict(addr=word('addr', k), age_now=uncode(word('age_now', m)),
                       age=uncode(word('age', m)), f1=r[('f1', 0)], f2=r[('f2', 0)])
            ref = maintenance.maintenance_scalar(cs, Q, U)
            self.assertEqual(got, {kk: int(v) for kk, v in ref.items()}, (trial, ba, bt))


class BackendTest(unittest.TestCase):
    def random_state(self, c, colonies, seed):
        rng = np.random.default_rng(seed)
        N = colonies * c.p.Q
        X = rng.random((c.W, N)) < 0.5
        # many front arrivals and match passes
        c.set_field(X, 'age', rng.integers(c.p.E0, c.p.E0 + c.p.NP * c.p.Q, size=N))
        return X

    def test_c_scalar_vector_and_numpy_agree_on_arbitrary_states(self):
        c = cand()
        C = c.c_backend()
        for colonies, seed in ((2, 11), (8, 12)):
            X = self.random_state(c, colonies, seed)
            Y = X
            for _ in range(3):
                Y = c.step_numpy(Y)
            P = C.pack(X)
            self.assertTrue(np.array_equal(C.unpack(C.run_packed_scalar(P.copy(), 3), X.shape[1]), Y))
            self.assertTrue(np.array_equal(C.unpack(C.run_packed(P.copy(), 3, threads=4), X.shape[1]), Y))

    def test_transition_reads_nothing_beyond_radius_five(self):
        c = cand()
        X = self.random_state(c, 2, 13)
        N = X.shape[1]
        center = 100
        base = c.step_numpy(X)[:, center]
        rng = np.random.default_rng(14)
        for trial in range(20):
            Z = X.copy()
            far = [s for s in range(N) if min((s - center) % N, (center - s) % N) > 5]
            Z[:, far] = rng.random((c.W, len(far))) < 0.5
            self.assertTrue(np.array_equal(c.step_numpy(Z)[:, center], base))

    def test_rom_lookup_defined_for_every_psel_value(self):
        c = cand()
        self.assertEqual(c.rom.shape, (c.p.Q, 1 << c.p.logNP))


class CodecTest(unittest.TestCase):
    def test_encode_decode_bijective_and_every_raw_field_encoded(self):
        c = cand()
        rng = np.random.default_rng(3)
        up = codec.random_upper(c, 4, rng)
        self.assertTrue(np.array_equal(codec.decode(c, codec.encode(c, up)), up))
        base = codec.encode(c, up)
        for b in range(c.W):
            flipped = up.copy()
            flipped[b, 2] ^= True
            self.assertFalse(np.array_equal(codec.encode(c, flipped), base), c.rows[b])
        fields = {f for f, _ in c.rows}
        self.assertTrue({'reg', 'scr', 'ln', 'mr', 'ml', 'hold', 'info', 'addr', 'age',
                         'f1', 'f2', 'wf1', 'wf2'} <= fields)


class ClosureTest(unittest.TestCase):
    def test_successive_decoded_macrosteps_on_random_upper_states(self):
        c = cand()
        C = c.c_backend()
        rng = np.random.default_rng(2026)
        up = codec.random_upper(c, 12, rng)
        P = C.pack(codec.encode(c, up))
        for period in range(3):
            P = C.run_packed(P, c.p.U, threads=4)
            X = C.unpack(P, 12 * c.p.Q)
            ref = c.step_numpy(up)
            self.assertTrue(np.array_equal(codec.decode(c, X), ref), period)
            health = codec.colony_health(c, X)
            self.assertTrue(health['addr'] and health['age'] and health['age0'] == 0)
            self.assertGreater(int((ref != up).sum()), 0)   # dynamics did not stop
            up = ref

    def test_physical_state_changes_every_tick_of_a_period(self):
        c = cand()
        C = c.c_backend()
        rng = np.random.default_rng(5)
        P = C.pack(codec.encode(c, codec.random_upper(c, 12, rng)))
        for _ in range(0, c.p.U, 997):
            Q = C.run_packed(P.copy(), 1, threads=1)
            self.assertFalse(np.array_equal(Q, P))
            P = C.run_packed(P, 997, threads=4)

    def test_mutated_rom_breaks_self_simulation(self):
        """The colony really executes the ROM program: corrupting one used
        instruction changes the decoded result for some upper input."""
        c = cand()
        rng = np.random.default_rng(9)
        used = np.argwhere(c.rom != 0)
        broken = 0
        for trial in range(3):
            a, pg = used[rng.integers(len(used))]
            rom = c.rom.copy()
            rom[a, pg] ^= 1 << int(rng.integers(0, c.p.IW))
            bad = machine.Candidate(c.p, rom, c.layout)
            up = codec.random_upper(c, 12, rng)
            X = bad.c_backend().run(codec.encode(bad, up), c.p.U, threads=4)
            # compare with the *original* rule upstairs
            if not np.array_equal(codec.decode(bad, X), c.step_numpy(up)):
                broken += 1
        self.assertGreater(broken, 0)


if __name__ == '__main__':
    unittest.main()


class GFamilyTest(unittest.TestCase):
    """G1: fivefold storage, three gathers, early Flag program, trickle-down."""

    def test_codec_writes_every_fivefold_info_copy(self):
        c = candidates.load('G1')
        rng = np.random.default_rng(21)
        up = codec.random_upper(c, 2, rng)
        X = codec.encode(c, up)
        info, agree = codec.logical_info(c, X)
        self.assertTrue(agree)
        self.assertTrue(np.array_equal(codec.decode(c, X), up))
        for b in (0, c.W // 2, c.W - 1):
            flipped = up.copy()
            flipped[b, 1] ^= True
            diff = np.argwhere(codec.encode(c, flipped) != X)
            self.assertEqual(len(diff), 5)       # all five stored copies change

    def test_reserved_simbit_cells_not_in_layout(self):
        c = candidates.load('G1')
        self.assertFalse({3, c.p.Q - 3} & set(c.layout.tolist()))

    def test_one_period_closure_with_special_procedure(self):
        c = candidates.load('G1')
        C = c.c_backend()
        rng = np.random.default_rng(31)
        up = codec.random_upper(c, 12, rng)
        ref = c.step_numpy(up)
        P = C.pack(codec.encode(c, up))
        P = C.run_packed(P, c.p.T_sig + 1, threads=4)
        info, _ = codec.logical_info(c, C.unpack(P, 12 * c.p.Q))
        sim = info.reshape(12, c.p.Q)
        self.assertTrue(np.array_equal(sim[:, c.p.Q - 3], ref[c.row[('f1', 0)]]))
        self.assertTrue(np.array_equal(sim[:, 3], ref[c.row[('f2', 0)]]))
        P = C.run_packed(P, c.p.U - c.p.T_sig - 1, threads=4)
        X = C.unpack(P, 12 * c.p.Q)
        self.assertTrue(np.array_equal(codec.decode(c, X), ref))
        h = codec.colony_health(c, X)
        self.assertTrue(h['addr'] and h['age'] and h['info_copies_agree'] and h['flags'] == 0)

    def test_c_matches_numpy_on_arbitrary_g_states(self):
        c = candidates.load('G1')
        C = c.c_backend()
        rng = np.random.default_rng(41)
        N = 4 * c.p.Q
        X = rng.random((c.W, N)) < 0.5
        c.set_field(X, 'age', rng.integers(c.p.E0, c.p.E0 + c.p.NP * c.p.Q, size=N))
        Y = X
        for _ in range(2):
            Y = c.step_numpy(Y)
        P = C.pack(X)
        self.assertTrue(np.array_equal(C.unpack(C.run_packed(P.copy(), 2, threads=4), N), Y))
        self.assertTrue(np.array_equal(C.unpack(C.run_packed_scalar(P.copy(), 2), N), Y))


class TripleEvaluationTest(unittest.TestCase):
    """G3: three evaluation runs into Hold copies A/B/C, majority at commit."""

    def _run_to_commit(self, c, seed):
        C = c.c_backend()
        rng = np.random.default_rng(seed)
        up = codec.random_upper(c, 8, rng)
        P = C.pack(codec.encode(c, up))
        P = C.run_packed(P, c.p.U - 1, threads=4)         # state at Age U-1
        return C, up, P

    def _corrupt_run(self, c, P, run, n1):
        """Flip every stored copy of Hold copy `run` at all layout cells."""
        C = c.c_backend()
        X = C.unpack(P, n1 * c.p.Q)
        for slot in range(5):
            row = c.row[('hold', slot * c.p.NH + run)]
            for b in range(c.W):
                cells = (np.arange(c.layout[b], n1 * c.p.Q, c.p.Q) - (slot - 2)) % (n1 * c.p.Q)
                X[row, cells] ^= True
        return C.pack(X)

    def test_one_period_closure(self):
        c = candidates.load('G3')
        C, up, P = self._run_to_commit(c, 51)
        P = C.run_packed(P, 1, threads=4)
        self.assertTrue(np.array_equal(codec.decode(c, C.unpack(P, 8 * c.p.Q)), c.step_numpy(up)))

    def test_commit_is_majority_of_three_runs(self):
        c = candidates.load('G3')
        C, up, P = self._run_to_commit(c, 52)
        ref = c.step_numpy(up)
        one = C.run_packed(self._corrupt_run(c, P.copy(), 1, 8), 1, threads=4)
        self.assertTrue(np.array_equal(codec.decode(c, C.unpack(one, 8 * c.p.Q)), ref))
        two = self._corrupt_run(c, self._corrupt_run(c, P.copy(), 1, 8), 2, 8)
        two = C.run_packed(two, 1, threads=4)
        self.assertFalse(np.array_equal(codec.decode(c, C.unpack(two, 8 * c.p.Q)), ref))


class ComputedFrontTest(unittest.TestCase):
    """G4: front clock, ROM lookup key and match use computed Age/Address."""

    def test_lookup_key_is_computed_address_in_both_backends(self):
        c = candidates.load('G4')
        self.assertIn(('laddr', 0), c.comp.outputs)
        C = c.c_backend()
        rng = np.random.default_rng(61)
        N = 4 * c.p.Q
        X = rng.random((c.W, N)) < 0.5
        c.set_field(X, 'age', rng.integers(c.p.E0, c.p.E0 + c.p.NP * c.p.Q, size=N))
        # consistent geometry so computed and stored Address mostly agree, then
        # corrupt a few stored Addresses so the two keys differ somewhere
        c.set_field(X, 'addr', np.tile(np.arange(c.p.Q), 4))
        bad = rng.choice(N, size=16, replace=False)
        addr = c.field(X, 'addr')
        addr[bad] ^= 5
        c.set_field(X, 'addr', addr)
        Y = c.step_numpy(X)
        self.assertTrue(np.array_equal(C.unpack(C.run_packed(C.pack(X), 1, threads=4), N), Y))
        self.assertTrue(np.array_equal(C.unpack(C.run_packed_scalar(C.pack(X), 1), N), Y))


class FivefoldFrontTest(unittest.TestCase):
    """G5: register file and pending buffer fivefold, one muxed lookup per cell."""

    def test_front_fields_are_fivefold_and_backends_agree(self):
        c = candidates.load('G5')
        widths = dict(c.schema)
        self.assertEqual(widths['reg'], 5 * c.p.L)
        self.assertEqual(widths['pend'], 5)
        C = c.c_backend()
        rng = np.random.default_rng(81)
        N = 2 * c.p.Q
        X = rng.random((c.W, N)) < 0.5
        c.set_field(X, 'addr', np.tile(np.arange(c.p.Q), 2))
        c.set_field(X, 'age', np.full(N, c.p.E0 + 5 * c.p.Q + 17))
        Y = c.step_numpy(X)
        self.assertTrue(np.array_equal(C.unpack(C.run_packed(C.pack(X), 1, threads=4), N), Y))
        self.assertTrue(np.array_equal(C.unpack(C.run_packed_scalar(C.pack(X), 1), N), Y))

    def test_single_register_copy_fault_is_outvoted_next_tick(self):
        """Flip one stored copy of a register bit of the front's logical cell
        mid-evaluation: after one tick the ring equals the unfaulted one."""
        c = candidates.load('G5')
        C = c.c_backend()
        rng = np.random.default_rng(82)
        up = codec.random_upper(c, 2, rng)
        P = C.pack(codec.encode(c, up))
        t = c.p.E0 + (c.p.MP + 5) * c.p.Q + 40      # inside the final program
        P = C.run_packed(P, t, threads=4)
        clean = C.run_packed(P.copy(), 3, threads=4)
        X = C.unpack(P, 2 * c.p.Q)
        page, pos = divmod(t - 1 - c.p.E0, c.p.Q)
        x = pos if page % 2 == 0 else c.p.Q - 1 - pos        # front's logical cell
        slot = 3                                               # copy held by cell x-1
        row = c.row[('reg', slot * c.p.L + 5)]
        X[row, (x - (slot - 2)) % (2 * c.p.Q)] ^= True
        faulty = C.run_packed(C.pack(X), 3, threads=4)
        self.assertTrue(np.array_equal(faulty, clean))


class CompactFrontTest(unittest.TestCase):
    """G11: the fivefold front stored as one register slot per cell (copies of
    the unique front within two cells). Flipping one or two copies near the
    front mid-evaluation must be fully corrected: three ticks later the ring
    equals the unfaulted one bit for bit."""

    NAMES = ('G11', 'G12')

    def _front_state(self, seed, name='G11'):
        c = candidates.load(name)
        p, C = c.p, c.c_backend()
        rng = np.random.default_rng(seed)
        up = codec.random_upper(c, 2, rng)
        P = C.pack(codec.encode(c, up))
        t = p.E0 + (p.MP + 5) * p.PL + 40                   # inside the final program
        P = C.run_packed(P, t, threads=4)
        X = C.unpack(P, 2 * p.Q)
        rows = [c.row[('reg', i)] for i in range(p.L)]
        cells = np.nonzero(X[rows].any(axis=0))[0]
        return c, C, P, X, rows, cells

    def test_register_field_is_single_slot(self):
        for name in self.NAMES:
            c = candidates.load(name)
            self.assertEqual(dict(c.schema)['reg'], c.p.L)
            self.assertEqual(dict(c.schema)['pend'], 5)

    def test_one_and_two_register_copy_faults_are_outvoted(self):
        for name in self.NAMES:
            c, C, P, X, rows, cells = self._front_state(91, name)
            # the front's register file sits on five consecutive cells per colony
            self.assertGreaterEqual(len(cells), 5)
            clean = C.run_packed(P.copy(), 3, threads=4)
            f = int(cells[2])                                # middle of the first colony's five
            for flips in ([f + 1], [f - 1, f + 2]):
                Y = X.copy()
                for x in flips:
                    for i in (0, 7, c.p.L - 1):
                        Y[rows[i], x] ^= True
                faulty = C.run_packed(C.pack(Y), 3, threads=4)
                self.assertTrue(np.array_equal(faulty, clean), (name, flips))


class MuxFrontEquivalenceTest(unittest.TestCase):
    """mux_front (one front step on the arriving slot's inputs) is the same
    Boolean function as the five gated steps: checked on random inputs and
    on inputs built so that the front arrives at a random slot (including
    match passes)."""

    def test_same_function_as_five_steps(self):
        c = candidates.load('G12')
        p = c.p
        p0 = replace(p, mux_front=False).check()
        _, comp0 = p0.fam().cached(p0)
        comp1 = c.comp
        self.assertLess(len(comp1.gates), len(comp0.gates))
        rng = np.random.default_rng(3)
        N = 2048
        arrivals = 0
        for forced in (False, True, True):
            vals = {nm: rng.random(N) < 0.5 for nm in comp0.inputs}
            if forced:
                pg = rng.integers(0, p.NP, N)
                pg[: N // 4] = p.MP
                d = rng.integers(-2, 3, N)
                a0 = rng.integers(p.lo + 2, p.hi - 2, N)
                tgt = a0 + d
                pos = np.where(pg % 2 == 0, tgt - p.lo, p.hi - 1 - tgt)
                codes = np.array([p.age_code(int(t)) for t in p.E0 + pg * p.PL + pos])
                for j in range(-5, 6):
                    a = (a0 + j) % p.Q
                    for i in range(p.k):
                        vals[('x', j, 'addr', i)] = ((a >> i) & 1).astype(bool)
                    for i in range(p.m):
                        vals[('x', j, 'age', i)] = ((codes >> i) & 1).astype(bool)
                    for f in ('f1', 'f2', 'wf1', 'wf2'):
                        vals[('x', j, f, 0)] = np.zeros(N, bool)
            o0 = comp0.evaluate(vals, dtype=bool)
            o1 = comp1.evaluate(vals, dtype=bool)
            arrivals += int(o0[('arrive', 0)].sum())
            for k in o0:
                self.assertTrue(np.array_equal(o0[k], o1[k]), k)
        self.assertGreater(arrivals, N)


def _gpu_available():
    import os
    import shutil
    from gacsca.fixed_rule.design_optimization import gpu
    if not (os.path.exists(gpu.NVCC) or shutil.which('nvcc')) or not shutil.which('nvidia-smi'):
        return False
    import subprocess
    return subprocess.run(['nvidia-smi', '-L'], capture_output=True).returncode == 0


@unittest.skipUnless(_gpu_available(), 'no CUDA toolkit or GPU')
class GpuBackendTest(unittest.TestCase):
    """The CUDA simulator executes the same fixed rule bit for bit."""

    def _states(self, c, nr, N, rng):
        C = c.c_backend()
        out = []
        for _ in range(nr):
            X = rng.random((c.W, N)) < 0.5
            c.set_field(X, 'age', rng.integers(c.p.E0, c.p.E0 + c.p.NP * c.p.Q, size=N))
            out.append(C.pack(X))
        return out

    def test_block_and_grid_modes_match_c_kernel_with_snapshots(self):
        from gacsca.fixed_rule.design_optimization import gpu
        c = cand()
        C = c.c_backend()
        rng = np.random.default_rng(5)
        for mode in ('block', 'grid'):
            sim = gpu.GpuSim(c, 3, 4, mode=mode)
            states = self._states(c, 3, sim.N, rng)
            sim.set_state(np.stack(states))
            rows = [0, c.row[('reg', 3)], c.W - 1]
            snap = sim.run(9, rows=rows, stride=3)
            for r in range(3):
                ref = states[r]
                for k in range(3):
                    ref = C.run_packed_scalar(ref, 3)
                    self.assertTrue(np.array_equal(snap[k, r], ref[rows]), (mode, r, k))
                self.assertTrue(np.array_equal(sim.state()[r], ref), (mode, r))

    def test_one_period_closure_on_gpu(self):
        from gacsca.fixed_rule.design_optimization import gpu
        c = cand()
        C = c.c_backend()
        up = codec.random_upper(c, 6, np.random.default_rng(8))
        sim = gpu.GpuSim(c, 1, up.shape[1])
        sim.set_state(C.pack(codec.encode(c, up)))
        sim.run(c.p.U)
        dec = codec.decode(c, C.unpack(sim.state()[0], sim.N))
        self.assertTrue(np.array_equal(dec, c.step_numpy(up)))

    def test_level0_error_grid_is_separated_and_boxes_are_exact(self):
        from gacsca.fixed_rule.design_optimization import gpu
        c = cand()
        sim = gpu.GpuSim(c, 2, 12)
        M = sim.error_masks(gpu.noise(seed=4, e0_grid=50, e0_pair=0.5), 1, 777, 400)
        t, x = np.nonzero(M)
        self.assertGreater(len(t), 50)
        groups = []
        for ti, xi in sorted(zip(t.tolist(), x.tolist())):
            if groups and groups[-1][0] == ti and xi == groups[-1][2] + 1:
                groups[-1][2] = xi
            else:
                groups.append([ti, xi, xi])
        N = M.shape[1]
        for i, a in enumerate(groups):
            self.assertLessEqual(a[2] - a[1], 1)
            for b in groups[i + 1:]:
                dx = min(abs(u - v) for u in a[1:] for v in b[1:])
                dx = min(dx, N - max(abs(u - v) for u in a[1:] for v in b[1:]))
                self.assertGreaterEqual(max(abs(a[0] - b[0]), dx), 25, (a, b))
        B = sim.error_masks(gpu.noise(seed=1, boxes=[(100, 200, 10, 30, 1.0)]), 0, 0, 50)
        self.assertTrue(B[10:40, 100:300].all())
        self.assertEqual(int(B.sum()), 200 * 30)

    def test_errors_are_deterministic_and_reference_ring_is_untouched(self):
        from gacsca.fixed_rule.design_optimization import gpu
        c = cand()
        C = c.c_backend()
        up = codec.random_upper(c, 4, np.random.default_rng(2))
        X0 = C.pack(codec.encode(c, up))
        cfg = gpu.noise(seed=9, e0_grid=50, boxes=[(40, 20, 100, 20, 0.5)])
        outs = []
        for _ in range(2):
            sim = gpu.GpuSim(c, 3, 4)
            sim.set_state(X0)
            sim.set_noise([gpu.noise(), cfg, cfg])
            sim.run(700)
            outs.append(sim.state())
        self.assertTrue(np.array_equal(outs[0], outs[1]))
        self.assertTrue(np.array_equal(outs[0][1], outs[0][2]))
        self.assertTrue(np.array_equal(outs[0][0], C.run_packed(X0.copy(), 700, threads=2)))
        self.assertFalse(np.array_equal(outs[0][1], outs[0][0]))


class ColonyMarginTest(unittest.TestCase):
    """G7/G8: Gray p. 33 margin. Represented SimBits and all workspace lie in
    the working range; margin cells carry instructions only at the two
    special cells, during the early Flag program."""

    NAMES = ('G7', 'G8', 'G9', 'G10', 'G11', 'G12')

    def test_layout_and_instruction_slots_avoid_margins(self):
        for name in self.NAMES:
            c = candidates.load(name)
            p = c.p
            lo, hi = p.fam().work_range(p)
            # margins of >= 100 cells: a 200-wide burst reaches at most one
            # colony's working area (G7/G8 also meet Gray's Q >= 2K; G9 uses
            # the smaller Q >= K + 200 that the margin argument needs)
            self.assertGreaterEqual(lo, 100)
            self.assertGreaterEqual(p.Q - hi, 100)
            self.assertGreaterEqual(hi - lo, c.W)
            self.assertTrue(((c.layout >= lo) & (c.layout < hi)).all())
            rows = set(np.nonzero(c.rom.any(axis=1))[0].tolist())
            margin_rows = {r for r in rows if not lo <= r < hi}
            self.assertLessEqual(margin_rows, set(p.fam().reserved_cells(p)))
            for r in margin_rows:
                self.assertLess(int(np.nonzero(c.rom[r])[0].max()), p.NPe)
                for col in np.nonzero(c.rom[r])[0]:
                    _, kind, _, _, _ = rule.decode_instruction(p, int(c.rom[r, col]))
                    self.assertIn(kind, (rule.K_REG, rule.K_HOLD))   # no scratch in margins

    def test_margin_is_compiler_only(self):
        """Unless the front is confined, the margin does not change the rule:
        the netlist equals the one built with margin 0. (A confined front's
        sweep range, Age radix and couriers depend on the margin, so there it
        is part of the rule.)"""
        for name in self.NAMES:
            c = candidates.load(name)
            p = c.p
            if getattr(p, 'confined', False):
                continue
            self.assertEqual(p.fam().cached(replace(p, margin=0))[1].digest, c.comp.digest)

    def test_g8_clears_scratch_at_the_period_boundary(self):
        """G8 (Gray p. 34): scratch, including never-written slots, is 0 after
        the commit tick; G7 keeps it."""
        for name, cleared in (('G7', False), ('G8', True), ('G9', True), ('G10', True), ('G11', True),
                              ('G12', True)):
            c = candidates.load(name)
            p = c.p
            rng = np.random.default_rng(4)
            X = rng.random((c.W, 2 * p.Q)) < 0.5
            c.set_field(X, 'age', np.full(2 * p.Q, p.age_code(p.U - 1)))
            for f in ('f1', 'f2', 'wf1', 'wf2'):
                c.set_field(X, f, np.zeros(2 * p.Q, dtype=int))
            c.set_field(X, 'addr', np.tile(np.arange(p.Q), 2))
            Y = c.step_numpy(X)
            scr = Y[[c.row[('scr', i)] for i in range(dict(c.schema)['scr'])]]
            self.assertEqual(not scr.any(), cleared, name)


@unittest.skipUnless(_gpu_available() and __import__('os').environ.get('GACSCA_SLOW') == '1',
                     'slow G8 GPU test: set GACSCA_SLOW=1 (needs a CUDA GPU, about 3 minutes)')
class G8SlowTest(unittest.TestCase):
    """G8 (the final G candidate): one full work period on the GPU for random
    and for coherent upper states decodes to the rule applied upstairs, with
    all Info copies agreeing and healthy colony geometry."""

    def test_one_period_closure_random_and_coherent(self):
        from gacsca.fixed_rule.design_optimization import gpu
        c = candidates.load('G8')
        p, C = c.p, c.c_backend()
        rng = np.random.default_rng(12)
        rand = codec.random_upper(c, 3, rng)
        coh = codec.random_upper(c, 3, rng)
        c.set_field(coh, 'addr', np.arange(3))
        c.set_field(coh, 'age', np.full(3, 17))
        for f in ('f1', 'f2', 'wf1', 'wf2'):
            c.set_field(coh, f, np.zeros(3, dtype=int))
        sim = gpu.GpuSim(c, 2, 3)
        sim.set_state(np.stack([C.pack(codec.encode(c, rand)), C.pack(codec.encode(c, coh))]))
        sim.run(p.U)
        S = sim.state()
        for r, up in enumerate((rand, coh)):
            X = C.unpack(S[r], sim.N)
            self.assertTrue(np.array_equal(codec.decode(c, X), c.step_numpy(up)), r)
            h = codec.colony_health(c, X)
            self.assertTrue(h['addr'] and h['age'] and h['info_copies_agree'], (r, h))
