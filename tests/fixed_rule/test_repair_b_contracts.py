"""Explicit modified-rule contracts, not a claim about the printed formula."""
from dataclasses import replace
import random
import unittest
from gacsca.fixed_rule import repair_b_rule as f,repair_b_native as native,delivery_rule as printed
from gacsca.level0_spec import Cfg,step_cell
from gacsca.params import Variant


class RepairBContracts(unittest.TestCase):
    def test_distinguishes_printed_and_no_ones_alternative(self):
        cells=tuple(f.Cell(address=100+j,age=98*f.Q,f2=int(j in (-1,0))) for j in range(-5,6))
        old=tuple(printed.Cell(**dict(zip((name for name,_ in f.SCHEMA),f.encode_cell(c)))) for c in cells)
        self.assertEqual(printed.maintenance(old)['f2'],1)
        self.assertEqual(f.maintenance(cells)['f2'],0)
        # Candidate A's no-left-ones erasure is false at the right damaged site.
        self.assertEqual(sum(c.f2 for c in cells[:5]),1)
        self.assertFalse(sum(c.f2 for c in cells[:5])==0)
        self.assertNotEqual(f.self_description().digest(),printed.self_description().digest())
        self.assertEqual(f.SCHEMA,printed.SCHEMA)
        self.assertEqual(f.identity()['flag2_healthy_erase'],'at_most_one')

    def test_all_healthy_self_and_left_patterns_agree_with_independent_baseline(self):
        variant=Variant(flag2_healthy_erase='at_most_one');lib=native.library()
        for address in (0,1,2,3,4,5,100,f.Q-1):
            for bits in range(64):
                cells=tuple(f.Cell(address=(address+j)%f.Q,age=98*f.Q,f2=(bits>>(-j))&1 if j<=0 else 0) for j in range(-5,6))
                cfg=Cfg(*([getattr(c,name) for c in cells] for name in ('address','age','f1','f2','wf1','wf2')))
                expected=step_cell(cfg,5,f.Q,f.U,variant)[:4];out=native.local_step(cells,lib)
                self.assertEqual((out.address,out.age,out.f1,out.f2),expected)
                self.assertEqual(f.maintenance(cells),dict(zip(('address','age','f1','f2'),expected)))

    def test_two_local_faults_restore_structure_with_all_eight_flag_bits(self):
        rng=random.Random(925);fields=('f1','f2','wf1','wf2');lib=native.library()
        for flags in range(256):
            site=(0,1,4,100,f.Q-2,f.Q-1)[flags%6];age=(0,96*f.Q,f.U-1)[flags%3]
            damaged={}
            for offset in (0,1):
                damaged[site+offset]=f.Cell(address=rng.randrange(f.Q),age=rng.randrange(f.U),**{name:(flags>>(4*offset+j))&1 for j,name in enumerate(fields)})
            for center in range(site-5,site+7):
                cells=tuple(damaged.get(position,f.Cell(address=position%f.Q,age=age)) for position in range(center-5,center+6))
                out=native.local_step(cells,lib)
                self.assertEqual((out.address,out.age,out.f1,out.f2),(center%f.Q,(age+1)%f.U,0,0),(flags,center))

    def test_random_damaged_geometry_matches_shared_scalar_maintenance(self):
        rng=random.Random(497);variant=Variant(flag2_healthy_erase='at_most_one')
        for k in range(300):
            cells=tuple(f.Cell(address=rng.randrange(f.Q),age=rng.randrange(f.U),f1=rng.randrange(2),f2=rng.randrange(2),wf1=rng.randrange(2),wf2=rng.randrange(2)) for _ in range(11))
            if k%2==0:
                address=rng.randrange(f.Q);age=rng.randrange(f.U)
                cells=tuple(replace(c,address=(address+j)%f.Q,age=age) if j not in (-2,0,1) else c for j,c in zip(range(-5,6),cells))
            cfg=Cfg(*([getattr(c,name) for c in cells] for name in ('address','age','f1','f2','wf1','wf2')))
            expected=step_cell(cfg,5,f.Q,f.U,variant)[:4]
            self.assertEqual(f.maintenance(cells),dict(zip(('address','age','f1','f2'),expected)))


if __name__=='__main__':unittest.main()
