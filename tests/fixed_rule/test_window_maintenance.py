"""Source-component parity, including counterexamples rather than silent fixes."""
import random
import unittest
from gacsca.fixed_rule.window_maintenance import Q, U, SCHEMA, description, pack, unpack
from gacsca.level0_spec import Cfg, step_cell


def neighborhood(address=100, age=71):
    return [dict(addr=(address + j) % Q, age=age, f1=0, f2=0, wf1=0, wf2=0)
            for j in range(-5, 6)]


def oracle(records):
    cfg = Cfg(**{name: [r[name] for r in records] for name, _ in SCHEMA})
    addr, age, f1, f2, _ = step_cell(cfg, 5, Q, U)
    return dict(addr=addr, age=age, f1=f1, f2=f2,
                wf1=records[5]['wf1'], wf2=records[5]['wf2'])


def bits(records):
    return tuple(bit for r in records for bit in pack(r))


class WindowMaintenanceTests(unittest.TestCase):
    def test_printed_rule_circuit_parity(self):
        rng = random.Random(923)
        cases = [neighborhood(a, age) for a in (0, 1, 4, 5, 100, Q-5, Q-1)
                 for age in (0, 15, U-1)]
        for _ in range(50):
            r = neighborhood(rng.randrange(Q), rng.randrange(U))
            for _ in range(rng.randrange(1, 6)):
                r[rng.randrange(11)] = {name: rng.randrange(1 << width) for name, width in SCHEMA}
            cases.append(r)
        cases.extend([{name: rng.randrange(1 << width) for name, width in SCHEMA}
                      for _ in range(11)] for _ in range(20))
        for case in cases:
            self.assertEqual(unpack(description().evaluate(bits(case))), oracle(case))

    def test_flag2_printed_persistence_is_preserved(self):
        records = neighborhood(age=U-1)
        records[5]['f2'] = 1
        expected = oracle(records)
        self.assertEqual(expected['f2'], 1)
        self.assertEqual(expected['age'], 0)
        # This port is a component/capacity check, not a claim that the wider
        # printed maintenance circuit is coupled into the current physical rule.
        self.assertEqual(unpack(description().evaluate(bits(records))),expected)


if __name__ == '__main__':
    unittest.main()
