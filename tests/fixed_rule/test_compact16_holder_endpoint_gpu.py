"""Explicit bounded GPU guards and complete-state endpoint witness."""
import os
import unittest
import numpy as np
from dataclasses import replace
from gacsca.fixed_rule import compact16_holder_endpoint_gpu as gpu
from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_projected as r, compact16_holder_program as p
from gacsca.fixed_rule import compact16_holder_terminal_dag as dag
from experiments.fixed_rule.compact16_holder_active_fixture import parents
from experiments.fixed_rule.validate_compact16_holder_endpoint import guard


@unittest.skipUnless(os.environ.get('FIXED_RULE_GPU_TESTS')=='1','explicit GPU test opt-in')
class Endpoint(unittest.TestCase):
    def test_rejects_overwide_and_changed_own_metadata_atomically(self):
        g=p.layout();bank=np.zeros((1,g.memory_count+5),dtype=np.uint64)
        bank[0,list(g.info)]=f.encode_cell(r.lift(r.Cell()))
        for field,xor in (('age',1<<40),('p3_index',1)):
            changed=bank.copy();changed[0,g.info[f.COL[field]]]^=np.uint64(xor)
            with gpu.World(changed,np.zeros((1,2),dtype=np.uint64)) as world:
                with self.assertRaises(ValueError):world.precommit()
                actual,signals=world.read()
                np.testing.assert_array_equal(actual,changed)
                self.assertEqual(world.time,0)
                self.assertFalse(np.any(signals))

    def test_full_scratch_witness_on_device(self):
        healthy=parents();damaged=list(healthy);damaged[15]=replace(damaged[15],s0_value=damaged[15].s0_value^1)
        results=[];g=p.layout()
        for states in (healthy,tuple(damaged)):
            bank=np.zeros((len(states),g.memory_count+5),dtype=np.uint64)
            bank[:,list(g.info)]=[f.encode_cell(r.lift(cell)) for cell in states]
            expected=dag.terminal(states)
            with gpu.World(bank,np.zeros((len(states),2),dtype=np.uint64)) as world:
                with guard():world.period()
                actual,signals=world.read()
                np.testing.assert_array_equal(actual,expected['committed_bank'])
                np.testing.assert_array_equal(signals,expected['signals'])
                results.append(actual)
        np.testing.assert_array_equal(results[0][:,list(g.info)],results[1][:,list(g.info)])
        self.assertEqual(np.count_nonzero(results[0]!=results[1]),28)


if __name__=='__main__':unittest.main()
