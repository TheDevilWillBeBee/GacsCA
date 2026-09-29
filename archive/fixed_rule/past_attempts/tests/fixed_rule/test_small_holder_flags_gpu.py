"""Packed arbitrary flags against full radius-seven physical transitions."""
import unittest
import random
from dataclasses import replace
import numpy as np
from gacsca.fixed_rule import small_holder_flags_gpu as gpu
from gacsca.fixed_rule import small_holder_rule as f,small_holder_projected as r
from gacsca.fixed_rule import small_holder_native as native,small_holder_core as c
from gacsca.fixed_rule import small_holder_initial as initial


def cell(raw,position,age,right,left):
    position%=len(right)*f.Q;col,a=divmod(position,f.Q)
    def flags(pos):
        pos%=len(right)*f.Q;word,bit=divmod(pos,64)
        return (int(raw[word,0])>>bit)&1,(int(raw[word,1])>>bit)&1
    f1,f2=flags(position);signal=left[col]<<(5-a) if 1<=a<=5 else right[col]<<(f.Q-1-a) if a>=f.Q-5 else 0
    fields=dict(address=a,age=age%f.U,f1=f1,f2=f2,signal=signal)
    for d in f.OFFSETS:
        target=(position+d)%(len(right)*f.Q);other,at=divmod(target,f.Q);active=f.WF_START<=age<f.WF_END
        fields[f'w{d+2}_wf1']=int(active and at>=f.Q-5 and right[other])
        fields[f'w{d+2}_wf2']=int(active and at<=4 and left[other] and not flags(target)[0])
    return r.lift(r.Cell(**fields))


class GeneralFlags(unittest.TestCase):
    def test_arbitrary_bits_match_complete_physical_rule_and_backup_wf(self):
        rng=np.random.default_rng(456);right=(1,0,1);left=(0,1,1)
        for age in (f.WF_START-1,f.WF_START,f.WF_END-1,f.WF_END):
            raw=rng.integers(0,2**64,size=(3*gpu.WORDS,2),dtype=np.uint64)
            positions=tuple(sorted({(col*f.Q+a)%(3*f.Q) for col in range(3) for a in (*range(-8,9),*range(60,69),100,1000)}))
            with gpu.World(right,left,age=age,initial=raw) as world:
                world.run(1);new=world.read()
            for position in positions:
                actual=native.local_step(tuple(cell(raw,position+j,age,right,left) for j in f.NEIGHBORHOOD))
                expected=cell(new,position,age+1,right,left)
                for name in ('address','age','f1','f2','signal',*(f'w{i}_{field}' for i in range(5) for field in ('wf1','wf2'))):
                    self.assertEqual(getattr(actual,name),getattr(expected,name),(age,position,name))

    def test_graph_batches_equal_literal_steps_across_clock_boundaries(self):
        rng=np.random.default_rng(458)
        raw=rng.integers(0,2**64,size=(2*gpu.WORDS,2),dtype=np.uint64)
        for age,ticks in ((f.WF_START-1,259),(f.WF_END-129,260)):
            with gpu.World((1,0),(1,1),age=age,initial=raw) as fast,gpu.World((1,0),(1,1),age=age,initial=raw) as slow:
                fast.run(ticks)
                for _ in range(ticks):slow.run(1)
                np.testing.assert_array_equal(fast.read(),slow.read())
                self.assertEqual((fast.age,fast.time),(slow.age,slow.time))
                # A second odd-length call catches stale CUDA graph pointers.
                fast.run(131)
                for _ in range(131):slow.run(1)
                np.testing.assert_array_equal(fast.read(),slow.read())

    def test_mail_free_procedure_outputs_do_not_depend_on_canonical_flags(self):
        rng=random.Random(77)
        for trial in range(32):
            center=(0,f.Q-1,100,20000)[trial%4];age=(f.WF_START-1,f.WF_START,f.WF_END-1,f.WF_END)[trial%4]
            logical={i:c.Cell(**r.record((center+i)%f.Q),address=(center+i)%f.Q,age=age,**{name:rng.getrandbits(width) for name,width in f.PROCEDURE if not name.startswith(('lp_','rp_'))}) for i in range(-9,10)}
            clean=tuple(r.lift(initial.coherent_cell(logical.__getitem__,j)) for j in range(-7,8))
            changed=tuple(replace(x,f1=rng.randrange(2),f2=rng.randrange(2),**{f'w{i}_{name}':rng.randrange(2) for i in range(5) for name in ('wf1','wf2')}) for x in clean)
            a=native.local_step(clean);b=native.local_step(changed)
            self.assertEqual((a.address,a.age),(b.address,b.age))
            for offset in range(5):
                for name,_ in f.PROCEDURE:self.assertEqual(getattr(a,f's{offset}_{name}'),getattr(b,f's{offset}_{name}'))

    def test_invalid_domain_rejected_before_mutation(self):
        with self.assertRaises(ValueError):gpu.World((1,),(1,),age=0)
        with self.assertRaises(ValueError):gpu.World((1,),(2,))
        with gpu.World((0,),(1,)) as world:
            before=world.read()
            with self.assertRaises(ValueError):world.run(f.U)
            np.testing.assert_array_equal(world.read(),before)
            self.assertEqual(world.time,0)


if __name__=='__main__':unittest.main()
