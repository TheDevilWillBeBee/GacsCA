"""Exact endpoint GPU operator, entry-domain rejection, and atomic failure."""
from contextlib import ExitStack
import random
import unittest
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import retimed_holder_endpoint_gpu as gpu,retimed_holder_terminal_dag as dag,retimed_holder_terminal_reference as replay
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_projected as r,retimed_holder_program as p,retimed_holder_quotient as q,retimed_holder_terminal_checks as checks
from gacsca.fixed_rule.wordcode import Program


def initial(parents):
    g=p.layout();bank=np.zeros((len(parents),g.memory_count+5),dtype=np.uint64)
    for col,parent in enumerate(parents):bank[col,list(g.info)]=f.encode_cell(r.lift(parent))
    return bank,np.zeros((len(parents),2),dtype=np.uint64)


def guarded(world,method):
    with ExitStack() as stack:
        for module,name in ((Program,'evaluate'),(r,'local_step'),(r,'step_ring'),(f,'local_step'),(dag,'terminal'),(replay,'terminal')):
            stack.enter_context(patch.object(module,name,side_effect=AssertionError('host simulated transition')))
        getattr(world,method)()


class Endpoint(unittest.TestCase):
    def test_random_typed_successive_periods(self):
        rng=random.Random(2026092702)
        parents=tuple(r.Cell(**{name:rng.getrandbits(width) for name,width in r.SCHEMA}) for _ in range(3))
        bank,signals=initial(parents)
        with gpu.World(bank,signals) as world:
            for epoch in range(2):
                expected=dag.terminal(parents);guarded(world,'precommit')
                checks.check(world.snapshot(),expected,age=f.U-1,time=(epoch+1)*f.U-1)
                guarded(world,'commit');checks.check(world.snapshot(),expected,age=0,time=(epoch+1)*f.U)
                parents=r.step_ring(parents)

    def test_aliasing_and_extreme_fields(self):
        parents=(r.Cell(**{name:(1<<width)-1 for name,width in r.SCHEMA}),)
        expected=dag.terminal(parents)
        with gpu.World(*initial(parents)) as world:
            guarded(world,'period');checks.check(world.snapshot(),expected,age=0,time=f.U)

    def test_bad_raw_width_and_metadata_reject_without_mutation(self):
        for name,value in (('s2_head',2),('p0_index',12345)):
            bank,signals=initial((r.Cell(),));bank[0,p.layout().info[f.COL[name]]]=value
            with gpu.World(bank,signals) as world:
                before=world.read()
                with self.assertRaisesRegex(ValueError,'rejected atomically'):guarded(world,'precommit')
                after=world.read()
                for a,b in zip(before,after):np.testing.assert_array_equal(a,b)
                self.assertEqual((world.age,world.time),(0,0))

    def test_live_controller_flags_and_signal_shape_rejected(self):
        bank,signals=initial((r.Cell(),));signals[0]=1
        with gpu.World(bank,signals) as world:original=world.snapshot()
        for name in ('controller','flag','signal'):
            state={k:v.copy() for k,v in original.items()}
            if name=='controller':state['active_rows'][0,0,q.COL['rb']]=1
            elif name=='flag':state['flags'][0,1]=1
            else:state['active_rows'][0,0,q.COL['signal']]=0
            with self.assertRaises(AssertionError,msg=name):gpu.World.from_snapshot(state)

    def test_valid_snapshot_import_and_phase_guards(self):
        bank,signals=initial((r.Cell(),))
        with gpu.World(bank,signals) as original:state=original.snapshot()
        with gpu.World.from_snapshot(state) as world:
            with self.assertRaises(ValueError):world.commit()
            guarded(world,'precommit')
            with self.assertRaises(ValueError):world.precommit()
            guarded(world,'commit')
            with self.assertRaises(ValueError):world.read(max_bytes=1)

    def test_budget_and_fixed_binary(self):
        bank,signals=initial((r.Cell(),))
        with self.assertRaises(ValueError):gpu.World(bank,signals,device_budget=gpu.allocation_bytes(1)-1)
        with gpu.World(bank,signals) as a,gpu.World(*initial((r.Cell(),)*3)) as b:
            self.assertEqual(a.lib._name,b.lib._name)
            self.assertEqual(a.device_bytes,gpu.allocation_bytes(1));self.assertEqual(b.device_bytes,gpu.allocation_bytes(3))


if __name__=='__main__':unittest.main()
