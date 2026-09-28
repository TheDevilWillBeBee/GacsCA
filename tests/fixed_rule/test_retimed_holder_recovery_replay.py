from types import SimpleNamespace
import unittest
import numpy as np

from experiments.fixed_rule.retimed_holder_recovery_replay import RecoveryReplay
from experiments.fixed_rule.audit_retimed_holder_contextual_recovery import GlobalProcedures
from gacsca.fixed_rule import retimed_holder_rule as f
from gacsca.fixed_rule import retimed_holder_literal_cone as cone
from tests.fixed_rule.test_retimed_holder_global_events import ring


class RecoveryReplayTests(unittest.TestCase):
    def test_flags_and_full_controllers_match_uncached_scalar_and_native(self):
        raw = ring([{200:dict(pc=4000000,rb=2**63+17),202:dict(pc=4000001,direction=1)},
                    {200:dict(pc=4000000,rb=2**63+19)}])
        raw[[0,5,f.Q-1,f.Q+20],f.COL['f1']] = 1
        raw[100:108,f.COL['f1']] = 1
        age = int(raw[0,f.COL['age']])
        view = SimpleNamespace(base=SimpleNamespace(size=len(raw),age=age),cells=lambda sites:raw[np.asarray(sites)%len(raw)])
        actual,expected = RecoveryReplay(view),GlobalProcedures(view)
        native = raw.copy()
        for tick in range(1,5):
            actual.step(age+tick-1);expected.step(age+tick-1)
            native = cone.step(native)
            np.testing.assert_array_equal(actual.words,expected.words)
            self.assertEqual(actual.flags,expected.flags)
            for start in (0,f.Q):
                sites = np.arange(start,start+f.Q)
                np.testing.assert_array_equal(actual.cells(sites,age+tick),native[sites])
        self.assertGreater(sum(value.bit_count() for value in actual.flags),4)

    def test_memoization_uses_all_raw_registers(self):
        # Nearly identical heads differ in high bits of a raw register.
        # Reusing a phase/PC-only result would erase that difference.
        raw = ring([{200:dict(pc=4000000,rb=2**63+17)},
                    {200:dict(pc=4000000,rb=2**63+19)}])
        age = int(raw[0,f.COL['age']])
        view = SimpleNamespace(base=SimpleNamespace(size=len(raw),age=age),cells=lambda sites:raw[np.asarray(sites)%len(raw)])
        actual,expected = RecoveryReplay(view),GlobalProcedures(view)
        actual.step(age);expected.step(age)
        np.testing.assert_array_equal(actual.words,expected.words)
        self.assertNotEqual(int(actual.words[201,5]),int(actual.words[f.Q+201,5]))


if __name__ == '__main__':unittest.main()
