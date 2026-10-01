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


def netlist_outputs(c, X):
    """All netlist outputs on state X before the ROM lookup (I = 0)."""
    values = {}
    zeros = np.zeros(X.shape[1], dtype=bool)
    for name in c.comp.inputs:
        if name[0] == 'x':
            _, j, f, i = name
            values[name] = np.roll(X[c.row[(f, i)]], -j)
        else:
            values[name] = zeros
    return c.comp.evaluate(values, bool)


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

    NAMES = ('G11', 'G12', 'G13')

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


class SelFrontEquivalenceTest(unittest.TestCase):
    """sel_front (select the arriving front's five register and lane copies,
    then one majority) computes the same state transition as mux_front (a
    majority for every candidate source, then select), on random inputs and
    on inputs where a front of the G14 comb arrives at a random slot,
    including match passes. Outside arrivals only the don't-care lookup
    outputs (psel, laddr) may differ."""

    def test_same_transition_as_mux_front(self):
        for mode in (1, 2):
            self._check(mode)

    def _check(self, mode):
        c = candidates.load('G14')
        p0 = c.p
        p1 = replace(p0, sel_front=mode).check()
        comp0 = c.comp
        _, comp1 = p1.fam().cached(p1)
        self.assertLess(len(comp1.gates), len(comp0.gates))
        rng = np.random.default_rng(5)
        N = 2048
        arrivals = 0
        seen = []
        for forced in (False, True, True, True):
            vals = {nm: rng.random(N) < 0.5 for nm in comp0.inputs}
            if forced:
                pg = rng.integers(0, p0.NP, N)
                pg[: N // 4] = p0.MP
                d = rng.integers(-2, 3, N)
                j = rng.integers(0, p0.fronts, N)
                t = rng.integers(0, p0.PL, N)
                front = np.where(pg % 2 == 0, p0.lo - p0.H + t + j * p0.delta,
                                 p0.hi - 1 - t + j * p0.delta)
                a0 = front - d
                codes = np.array([p0.age_code(int(x)) for x in p0.E0 + pg * p0.PL + t])
                for jj in range(-5, 6):
                    a = (a0 + jj) % p0.Q
                    for i in range(p0.k):
                        vals[('x', jj, 'addr', i)] = ((a >> i) & 1).astype(bool)
                    for i in range(p0.m):
                        vals[('x', jj, 'age', i)] = ((codes >> i) & 1).astype(bool)
                    for f in ('f1', 'f2', 'wf1', 'wf2'):
                        vals[('x', jj, f, 0)] = np.zeros(N, bool)
            o0 = comp0.evaluate(vals, dtype=bool)
            o1 = comp1.evaluate(vals, dtype=bool)
            self.assertTrue(self._same(o0, o1))
            arrivals += int(o0[('arrive', 0)].sum())
            seen.append((vals, o0))
        self.assertGreater(arrivals, 2 * N)
        # negative control: the same comparison, on the same inputs, catches single-gate mutants
        # of comp1 (one AND/OR/XOR replaced by another): every mutant of a gate that drives a
        # register output, and most mutants of randomly chosen gates
        import copy
        n_in = 2 + len(comp1.inputs)

        def caught(g):
            m = copy.copy(comp1)
            m.gates = list(comp1.gates)
            op, a, b = m.gates[g]
            m.gates[g] = ((op + 1) % 3, a, b)
            return any(not self._same(o, m.evaluate(v, dtype=bool)) for v, o in seen)
        reg = sorted({node - n_in for k, node in comp1.outputs.items()
                      if k[0] == 'y' and k[1] == 'reg' and node >= n_in})[:8]
        self.assertEqual(len(reg), 8)
        self.assertTrue(all(caught(g) for g in reg))
        rand = np.random.default_rng(mode).choice(len(comp1.gates), 20, replace=False)
        self.assertGreaterEqual(sum(caught(int(g)) for g in rand), 12)

    @staticmethod
    def _same(o0, o1):
        arr = o0[('arrive', 0)]
        if not np.array_equal(arr, o1[('arrive', 0)]):
            return False
        for k in o0:
            a, b = (o0[k][arr], o1[k][arr]) if k[0] in ('psel', 'laddr') else (o0[k], o1[k])
            if not np.array_equal(a, b):
                return False
        return True


class CacheIntegrityTest(unittest.TestCase):
    """The trusted manifest (fresh builds of every recipe) pins each cached
    candidate: a cache whose ROM differs by one bit is rejected, although
    its netlist digest is unchanged (audit finding 4)."""

    def test_every_cached_candidate_matches_the_manifest(self):
        man = candidates.manifest()
        self.assertEqual(set(man), set(candidates.RECIPES))
        for name in ('R1', 'G8', 'G14'):
            self.assertTrue(candidates.verify(name, candidates.load(name)))

    def test_tampered_rom_is_rejected(self):
        import os
        import tempfile
        src = candidates.CACHE
        with tempfile.TemporaryDirectory() as tmp:
            with np.load(os.path.join(src, 'R1.npz'), allow_pickle=False) as z:
                a = {k: z[k] for k in z.files}
            nz = np.argwhere(a['rom'] != 0)[0]
            a['rom'] = a['rom'].copy()
            a['rom'][tuple(nz)] ^= np.uint32(1)
            np.savez(os.path.join(tmp, 'R1.npz'), **a)
            candidates.CACHE = tmp
            try:
                with self.assertRaises(RuntimeError):
                    candidates.load('R1')
                c = candidates.load('R1', check_manifest=False)      # what the audit loaded
                self.assertEqual(c.comp.digest, candidates.manifest()['R1']['netlist_sha256'])
            finally:
                candidates.CACHE = src


    def test_a_changed_recipe_rejects_the_cache(self):
        """The cache is also checked against the current recipe (second audit, finding 5): a
        changed rule parameter, or a changed compile setting that leaves the parameters alone
        (caught by the recipe digest pinned in the manifest), makes load() refuse the cache."""
        import copy
        saved = candidates.RECIPES['G15']
        self.assertEqual(candidates.manifest()['G15'].get('recipe_sha256'), candidates.recipe_digest('G15'))
        try:
            r = copy.deepcopy(saved)
            r['params']['stage_wipe'] = False
            candidates.RECIPES['G15'] = r
            with self.assertRaises(RuntimeError):
                candidates.load('G15')
            r = copy.deepcopy(saved)
            r['compile']['multifront']['order_seed'] = 6
            candidates.RECIPES['G15'] = r
            with self.assertRaises(RuntimeError):
                candidates.load('G15')
        finally:
            candidates.RECIPES['G15'] = saved
        candidates.load('G15')


class GrayErrorClassTest(unittest.TestCase):
    """gray_errors implements Gray's section 5.1 classes for finite sets."""

    def test_dense_boxes(self):
        from gacsca.fixed_rule.design_optimization import gray_errors as ge
        r = ge.classify(ge.dense_box(0, 0, 100, 100), Q=512, U=110880)
        self.assertTrue(r['level1'])
        self.assertEqual(r['level0'], 0)
        r = ge.classify(ge.dense_box(0, 0, 200, 200), Q=512, U=110880)
        self.assertFalse(r['level1'])
        a, b = r['witness']
        self.assertFalse(ge.linked(a, b, 104, 104))          # two separated candidates inside
        self.assertTrue(ge.linked(a[:1], a[1:], 24, 24))

    def test_small_sets(self):
        from gacsca.fixed_rule.design_optimization import gray_errors as ge
        self.assertEqual(ge.classify([(5, 5)])['level0'], 1)                 # isolated site
        self.assertEqual(ge.classify([(5, 5), (6, 5)])['level0'], 2)         # adjacent pair
        r = ge.classify([(0, 0), (1, 0), (10, 10)], Q=512, U=1 << 16)        # linked candidates
        self.assertTrue(r['level1'])
        r = ge.classify([(0, 0), (10, 10), (300, 0), (310, 10)], Q=512, U=1 << 16)
        self.assertFalse(r['level1'])                                       # two separated pairs
        r = ge.classify([(0, 0), (10, 10), (0, 30)], Q=512, U=1 << 16)
        self.assertTrue(r['candidate_level1'])
        # isolation (iv): a second cluster closer than (24Q, 24U) disqualifies
        r = ge.classify([(0, 0), (10, 10)], E=[(0, 0), (10, 10), (5000, 0), (5010, 10)],
                        Q=512, U=1 << 16)
        self.assertFalse(r['level1'])

    def test_level0_errors_inside_S_and_isolated_pairs(self):
        """S must avoid E0 (Gray takes S inside E minus E0); an isolated adjacent pair is a
        level-0 error also in a large set; a dense box with E0-grid hits just outside it fails
        isolation (iv) alone, and together with the linked hits is one level-1 error."""
        from gacsca.fixed_rule.design_optimization import gray_errors as ge
        S = set(ge.dense_box(0, 0, 3, 3)) | {(1000, 0)}
        r = ge.classify(S, Q=512, U=112608)
        self.assertFalse(r['level1'])
        self.assertEqual(r['level0'], 1)
        self.assertTrue(r['core']['level1'])
        box = set(ge.dense_box(0, 0, 36, 36))
        pair = {(1000, 0), (1001, 0)}
        self.assertEqual(ge.level0_points(box | pair), pair)
        self.assertTrue(ge.classify(box, box | pair, Q=512, U=112608)['level1'])
        big = set(ge.dense_box(0, 0, 100, 100))
        hits = {(-10, 40), (120, 70), (50, -15)}
        far = {(3000, 3000), (3500, 2000), (3501, 2000)}
        E = big | hits | far
        self.assertEqual(ge.level0_points(E), far)
        self.assertFalse(ge.classify(big, E, Q=512, U=112608)['level1'])           # (iv)
        r = ge.classify(big | hits, E, Q=512, U=112608)
        self.assertTrue(r['level1'], r)
        self.assertEqual(r['method'], 'hub window')
        # an adjacent pair of hits 10 sites left of the box is itself a minimal candidate, 104 or
        # more away from the box's right edge: (iii) fails, exactly decided
        E2 = big | {(-10, 40), (-11, 40)}
        r = ge.classify(E2, Q=512, U=112608)
        self.assertFalse(r['level1'])
        self.assertEqual(r['method'], 'witness')
        a, b = r['witness']
        self.assertFalse(ge.linked(a, b, 104, 104))
        # two sites 2 left of the box: every pair at the far side is within 103, (iii) holds
        r = ge.classify(big | {(-2, 40), (-3, 40)}, Q=512, U=112608)
        self.assertTrue(r['level1'], r)
        # two linked stragglers on opposite sides, linked to each other's neighbourhood only
        # through the box, do not break (iii); two separated linked pairs do
        r = ge.classify([(0, 0), (10, 10), (300, 0), (310, 10)], Q=512, U=1 << 16)
        self.assertFalse(r['level1'])

    def test_generated_clusters_are_checked(self):
        from gacsca.fixed_rule.design_optimization import gray_errors as ge
        rng = np.random.default_rng(4)
        for _ in range(10):
            pts, boxes = ge.random_level1_cluster(rng, 100, 200, pairs=5)
            self.assertEqual(sum(w * h for _, w, _, h in boxes), len(pts))
            r = ge.classify(pts, Q=512, U=110880)
            self.assertEqual(r['level0'], 0)
            self.assertTrue(r['candidate_level1'])


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

    def test_per_tick_tracking_matches_a_tick_by_tick_comparison(self):
        """GpuSim.track records, per colony, the first and last tick at which a ring differs from
        ring 0 in the given rows and in any row, excluding the sites the ring's own noise hit in
        that update; compared with states downloaded after every single tick."""
        from gacsca.fixed_rule.design_optimization import gpu
        c = cand()
        C = c.c_backend()
        Q, ncol, T = c.p.Q, 6, 120
        P = C.pack(codec.encode(c, codec.random_upper(c, ncol, np.random.default_rng(3))))
        cfgs = [gpu.noise(), gpu.noise(7, boxes=[(Q + 40, 30, 5, 20, 1.0)]),
                gpu.noise(8, e0_grid=50, boxes=[(3 * Q + 10, 30, 40, 10, 1.0)])]
        rows = [c.row[(f, i)] for f, w in c.schema if f == 'info' for i in range(w)]
        sim = gpu.GpuSim(c, 3, ncol, mode='grid')
        sim.set_state(P)
        sim.set_noise(cfgs)
        sim.track(rows)
        ref = gpu.GpuSim(c, 3, ncol, mode='grid')
        ref.set_state(P)
        ref.set_noise(cfgs)
        want = {k: np.full((3, ncol), -1) for k in ('first_rows', 'last_rows', 'first_any', 'last_any')}
        for t in range(T):
            ref.run(1)
            S = ref.state()
            X = [C.unpack(S[r], ref.N) for r in range(3)]
            for r in (1, 2):
                fresh = ref.error_masks(cfgs[r], r, t, 1)[0]
                for key, d in (('rows', (X[r][rows] != X[0][rows]).any(axis=0)), ('any', (X[r] != X[0]).any(axis=0))):
                    for col in set((np.nonzero(d & ~fresh)[0] // Q).tolist()):
                        if want['first_' + key][r, col] < 0:
                            want['first_' + key][r, col] = t + 1
                        want['last_' + key][r, col] = t + 1
        sim.run(T)
        got = sim.tracking()
        for k in want:
            self.assertTrue(np.array_equal(got[k], want[k]), (k, got[k], want[k]))
        self.assertTrue((want['last_any'][1:] > 0).any(axis=1).all())

    def test_value_modes_replace_exactly_the_masked_sites(self):
        """Each error value mode (zero, one, invert, freeze, copy) changes the
        state at the masked sites of one tick, as specified, and nowhere
        else; compared with an error-free GPU ring and the C kernel."""
        from gacsca.fixed_rule.design_optimization import gpu
        c = cand()
        C = c.c_backend()
        rng = np.random.default_rng(13)
        sim0 = gpu.GpuSim(c, 1, 4, mode='block')
        X = rng.random((c.W, sim0.N)) < 0.5
        P = C.pack(X)
        t = 37
        ref_prev = C.run_packed_scalar(P.copy(), t)          # (the C runs overwrite their input)
        Xp = C.unpack(ref_prev, sim0.N)
        Xn = C.unpack(C.run_packed_scalar(ref_prev.copy(), 1), sim0.N)
        box = (100, 50, t, 1, 1.0)
        for mode in gpu.VALUE_MODES[1:]:
            sim = gpu.GpuSim(c, 1, 4, mode='block')
            sim.set_state(P.copy())
            sim.set_noise([gpu.noise(5, boxes=[box], mode=mode, shift_sites=c.p.Q)])
            sim.run(t + 1)
            Y = C.unpack(sim.state()[0], sim.N)
            m = sim.error_masks(gpu.noise(5, boxes=[box], mode=mode), 0, t, 1)[0]
            self.assertEqual(int(m.sum()), 50)
            want = Xn.copy()
            if mode == 'zero':
                want[:, m] = False
            elif mode == 'one':
                want[:, m] = True
            elif mode == 'invert':
                want[:, m] = ~Xn[:, m]
            elif mode == 'freeze':
                want[:, m] = Xp[:, m]
            else:
                want[:, m] = np.roll(Xp, -c.p.Q, axis=1)[:, m]
            self.assertTrue(np.array_equal(Y, want), mode)

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

    NAMES = ('G7', 'G8', 'G9', 'G10', 'G11', 'G12', 'G13', 'G14')

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
                              ('G12', True), ('G13', True)):
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


class CombTest(unittest.TestCase):
    """G13: a comb of five fronts five cells apart. Each front runs its own
    program (Pi[Address][page + front << logNP]) with its own register file;
    fronts outside the working cells only carry their registers."""

    def test_geometry_and_rom_columns(self):
        for name in ('G13', 'G14'):
            self._geometry(name)

    def _geometry(self, name):
        c = candidates.load(name)
        p = c.p
        self.assertEqual((p.fronts, p.delta, p.H, p.PL, p.R), (5, 5, 20, 288, 288))
        # level-1 bursts (200 cells) cannot reach two colonies' front state
        self.assertGreaterEqual(2 * p.margin - 2 * p.H - 3, 200)
        cols = np.nonzero(c.rom.any(axis=0))[0]
        fronts = set((cols >> p.logNP).tolist())
        self.assertEqual(fronts, set(range(p.fronts)))
        self.assertLess(int((cols & ((1 << p.logNP) - 1)).max()), p.NP)

    def test_fronts_arrive_delta_apart_and_carry_in_the_overhang(self):
        """Inside the final program, holders see arrivals at exactly the five
        comb positions of every colony (each front's five holders)."""
        c = candidates.load('G13')
        p, C = c.p, c.c_backend()
        up = codec.random_upper(c, 2, np.random.default_rng(3))
        X0 = codec.encode(c, up)
        for extra in (7, p.PL - 3):                       # a forward and a backward pass
            t = p.E0 + (p.MP + 3) * p.PL + extra
            X = C.unpack(C.run_packed(C.pack(X0), t, threads=4), 2 * p.Q)
            arr = netlist_outputs(c, X)[('arrive', 0)].astype(bool)
            page = (t - p.E0) // p.PL
            tt = extra if page % 2 == 0 else p.PL - 1 - extra
            want = [p.lo - p.H + tt + j * p.delta for j in range(p.fronts)]
            for col in range(2):
                got = np.nonzero(arr[col * p.Q:(col + 1) * p.Q])[0]
                holders = sorted({x + e for x in want for e in range(-2, 3)})
                self.assertEqual(got.tolist(), holders, (extra, col))

    def test_overhang_ignores_the_fetched_word_even_in_the_match_pass(self):
        """A front outside the working cells only carries: the cell's outputs
        do not depend on I, even in the match pass with the front's key equal
        to the cell's Address (front 0, which fetches one level down, never
        reaches the right overhang)."""
        c = candidates.load('G13')
        p, C = c.p, c.c_backend()
        up = codec.random_upper(c, 2, np.random.default_rng(6))
        t = p.E0 + p.MP * p.PL                      # first tick of the (backward) match pass
        X = C.unpack(C.run_packed(C.pack(codec.encode(c, up)), t, threads=4), 2 * p.Q)
        x = p.hi - 1 + (p.fronts - 1) * p.delta     # front 4, deep in the right overhang
        rows = [c.row[('reg', i)] for i in range(p.k)]
        for cell in range(x - 3, x + 6):
            for i, r in enumerate(rows):
                X[r, cell] = (x >> i) & 1           # the front's key = this Address
        base = netlist_outputs(c, X)
        self.assertTrue(base[('arrive', 0)][x])
        values = {}
        for name in c.comp.inputs:
            if name[0] == 'x':
                _, j, f, i = name
                values[name] = np.roll(X[c.row[(f, i)]], -j)
            else:
                values[name] = np.ones(X.shape[1], dtype=bool)
        ones = c.comp.evaluate(values, bool)
        for f, w in c.schema:
            for i in range(w):
                a, b = base[('y', f, i)], ones[('y', f, i)]
                self.assertTrue(np.array_equal(a[x - 2:x + 3], b[x - 2:x + 3]), (f, i))

    def test_multifront_scheduler_replays_on_random_data(self):
        """The comb scheduler's early and phase-A programs (F=3 on G12's
        netlist) compute the netlist on random inputs."""
        from gacsca.fixed_rule.design_optimization import multifront
        r = candidates.RECIPES['G12']
        params = dict(r['params'], NPe=250, MP=1051, NP=3000, nb=4000, m=21)
        p = candidates.FAMILIES['G'](**params).check()
        layout = compiler.proportional_layout(p, compiler.default_layout(p, False))
        skew, _ = compiler.choose_skew(p, layout, seed=0)
        p = replace(p, skew=skew).check()
        out, _ = multifront.compile_phases(p, layout, 3, 5, phases=('early', 'a'), cut=False,
                                           combine='spread', ctrl_fields=[])
        self.assertEqual(out['early']['replay_bad'], 0)
        self.assertEqual(out['a']['replay_bad'], 0)
        self.assertEqual(len(out['a']['per_front']), 3)


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
