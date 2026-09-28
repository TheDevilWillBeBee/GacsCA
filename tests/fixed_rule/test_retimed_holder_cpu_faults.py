"""Exact projected defects, causal support, and state-preserving Data rebases."""
from dataclasses import replace
import random
import unittest
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import retimed_holder_cpu_faults as overlay
from gacsca.fixed_rule import retimed_holder_cpu_general as general,retimed_holder_cpu_events as events
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_projected as r
from gacsca.fixed_rule import retimed_holder_core as c,retimed_holder_program as p


def world(age=100, *, n=1, capacity=1024, frontier=4096):
    data=np.zeros((n,f.Q),dtype=np.uint64)
    data[:,:p.layout().memory_count]=np.arange(p.layout().memory_count,dtype=np.uint64)+17
    data[:,1:6]=1;data[:,f.Q-5:]=1  # Coherent healthy capture on both sides.
    background=general.World(data,np.zeros((n,len(events.CONTROL)),dtype=np.uint64),np.zeros(n,dtype=np.uint64),age=age,right=[1]*n,left=[1]*n)
    return overlay.World(background,capacity=capacity,frontier_capacity=frontier)


def cone(read,at,ticks):
    rows={pos:r.project(read(pos)) for pos in range(at-7*ticks,at+7*ticks+1)}
    for step in range(ticks):
        radius=7*(ticks-step-1)
        rows={pos:r.local_step(tuple(rows[pos+j] for j in f.NEIGHBORHOOD)) for pos in range(at-radius,at+radius+1)}
    return r.lift(rows[at])


class RawExceptions(unittest.TestCase):
    def test_one_bad_Info_replica_repairs_in_one_literal_tick(self):
        w=world();at=p.layout().info[f.COL['s2_rb']]
        before={pos:cone(w.cell,pos,1) for pos in range(at-7,at+8)}
        w.inject({at:replace(r.project(w.cell(at)),s2_data=w.cell(at).s2_data^1)})
        result=w.step();self.assertEqual(result['candidates'],15);self.assertFalse(w.positions)
        for pos,expected in before.items():self.assertEqual(w.cell(pos),expected)

    def test_two_bad_procedure_holders_preserve_live_computation(self):
        w=world();at=73;rng=random.Random(1291)
        values=dict(head=1,phase=c.WRITE,rd=at,value=0x123456789abcdef0)
        w.background.heads[0]=[values.get(name,0) for name in events.CONTROL];w.background.where[0]=at
        clean={pos:cone(w.cell,pos,1) for pos in range(at-7,at+10)}
        faults={pos:replace(r.project(w.cell(pos)),**{f's{d+2}_{name}':rng.getrandbits(width) for d in f.OFFSETS for name,width in f.PROCEDURE}) for pos in (at,at+2)}
        w.inject(faults);w.step();self.assertFalse(w.positions)
        for pos,expected in clean.items():self.assertEqual(w.cell(pos),expected)
        self.assertEqual(w.cell(at).s2_data,0x123456789abcdef0)

    def test_geometry_controller_Signal_defects_match_literal_projected_cones(self):
        rng=random.Random(901)
        for age in (1,c.CAPTURE_AGE-1,c.WF_START-1,f.U-1):
            w=world(age);at=f.Q-2
            w.inject({pos:r.Cell(**{name:rng.getrandbits(width) for name,width in r.SCHEMA}) for pos in (at,at+1)})
            points=[(at+d)%w.sites for d in (-14,-3,0,1,7,15)]
            expected={pos:cone(w.cell,pos,2) for pos in points}
            w.step();w.step()
            for pos,wanted in expected.items():self.assertEqual(w.cell(pos),wanted,(age,pos))
            # Exact evolution, not a universal two-tick recovery claim.

    def test_three_bad_copies_persist_and_rebase_keeps_wrong_value(self):
        w=world();target=73;correct=w.cell(target).s2_data
        w.inject({target+d:replace(r.project(w.cell(target+d)),**{f's{2-d}_data':correct^1}) for d in (-1,0,1)})
        w.step();self.assertTrue(w.positions)
        before={pos:w.cell(pos) for pos in range(target-9,target+10)}
        result=w.absorb_data();self.assertEqual(result['data_cells'],1)
        self.assertFalse(w.positions);self.assertEqual(w.cell(target).s2_data,correct^1)
        for pos,wanted in before.items():self.assertEqual(w.cell(pos),wanted)
        w.advance(10);self.assertEqual(w.cell(target).s2_data,correct^1)

    def test_capacity_and_owner_guards_are_atomic(self):
        w=world(capacity=1,frontier=1);at=73
        dirty=replace(r.project(w.cell(at)),s2_data=w.cell(at).s2_data^1)
        w.inject({at:dirty});before=w.cell(at)
        with self.assertRaisesRegex(ValueError,'causal frontier'):w.step()
        self.assertEqual(w.time,0);self.assertEqual(w.cell(at),before)
        with self.assertRaisesRegex(ValueError,'exception capacity'):w.inject({at+1:dirty})
        self.assertEqual(w.positions,(at,))
        w.background.quiet_advance(1)
        with self.assertRaisesRegex(ValueError,'outside exception owner'):w.cell(at)

    def test_defect_step_reads_only_its_fixed_physical_cone(self):
        w=world(n=2);at=0
        w.inject({at:replace(r.project(w.cell(at)),s2_data=w.cell(at).s2_data^1)})
        original=w.cell;reads=[]
        def recorded(pos):
            reads.append(pos%w.sites);return original(pos)
        with patch.object(w,'cell',side_effect=recorded),patch.object(r,'step_ring',side_effect=AssertionError('upper transition forbidden')):w.step()
        self.assertTrue(reads);self.assertLessEqual(set(reads),{d%w.sites for d in range(-14,15)})


if __name__=='__main__':unittest.main()
