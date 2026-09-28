import itertools
import random
import unittest
from dataclasses import replace
from gacsca.fixed_rule import signal_rule as r,signal_native as native


def neighborhood(address=100,age=0):
    return tuple(r.Cell(address=(address+j)%r.Q,age=age) for j in range(-5,6))


def copies(cells,target,value=1):
    cells=list(cells)
    for e in range(-2,3):
        i=5+target+e;mask=1<<(2-e)
        cells[i]=replace(cells[i],signal=(cells[i].signal&~mask)|(value<<(2-e)))
    return tuple(cells)


class SignalRuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.lib=native.library()

    def test_complete_description_and_native_cover_raw_controller_and_signals(self):
        rng=random.Random(9031);desc=r.self_description()
        for i in range(240):
            cells=tuple(r.Cell(**{name:rng.getrandbits(width) for name,width in r.SCHEMA}) for _ in range(11))
            if i<160:
                address=(0,1,3,4,r.Q-5,r.Q-3,r.Q-1,100)[i%8]
                age=(r.CAPTURE_AGE-1,96*r.Q-1,96*r.Q,98*r.Q-1,r.U-1)[i%5]
                cells=tuple(replace(c,address=(address+j)%r.Q,age=age) for j,c in zip(range(-5,6),cells))
            expected=r.local_step(cells)
            self.assertEqual(expected,r.decode_cell(desc.evaluate(tuple(w for c in cells for w in r.encode_cell(c)))))
            self.assertEqual(expected,native.local_step(cells,self.lib))
        raw=r.Cell(**{name:(1<<width)-1 for name,width in r.SCHEMA})
        self.assertEqual(r.decode_cell(r.encode_cell(raw)),raw)
        with self.assertRaises(ValueError):r.decode_cell(r.encode_cell(raw)[:-1])
        self.assertEqual(r.WIDTH,788);self.assertEqual(r.FIELDS,32)

    def test_five_copies_recover_any_two_damaged_holders(self):
        # Evaluate all five repaired output slots representing logical cell 100.
        for damaged in itertools.combinations(range(-2,3),2):
            world={x:r.Cell(address=x,age=81*r.Q) for x in range(93,108)}
            for e in range(-2,3):world[100+e]=replace(world[100+e],signal=0 if e in damaged else 1<<(2-e))
            for e in range(-2,3):
                result=r.local_step(tuple(world[100+e+j] for j in range(-5,6)))
                self.assertEqual((result.signal>>(2-e))&1,1)

    def test_capture_uses_computed_address_and_all_five_backup_slots(self):
        for target in (3,r.Q-3):
            for d in range(-2,3):
                cells=list(neighborhood(target-d,r.CAPTURE_AGE-1))
                cells[5]=replace(cells[5],address=100,data=1)
                out=r.local_step(tuple(cells))
                self.assertEqual(out.address,target-d)
                self.assertEqual(out.signal,1<<(d+2))
                early=tuple(replace(c,age=r.CAPTURE_AGE-2) for c in cells)
                self.assertEqual(r.local_step(early).signal,0)
        cells=list(copies(neighborhood(3,r.CAPTURE_AGE-1),0))
        cells[5]=replace(cells[5],address=100,data=1,f2=1)
        for i in (4,5,6):cells[i]=replace(cells[i],wf1=1)
        out=r.local_step(tuple(cells))
        self.assertEqual(out.f1,1);self.assertNotEqual(out.address,100)
        self.assertEqual(out.signal|out.wf1|out.wf2,0)

    def test_signal_creates_workspace_flags_with_computed_clock_and_priority(self):
        for address in (*range(5),*range(r.Q-5,r.Q)):
            target=3-address if address<5 else r.Q-3-address
            cells=copies(neighborhood(address,96*r.Q-1),target)
            out=r.local_step(cells)
            self.assertEqual((out.wf1,out.wf2),(0,1) if address<5 else (1,0))
            self.assertEqual(r.local_step(tuple(replace(c,age=98*r.Q-1) for c in cells)).wf1|r.local_step(tuple(replace(c,age=98*r.Q-1) for c in cells)).wf2,0)
        cells=list(copies(neighborhood(0,96*r.Q+1),3))
        for i in (6,7,8):cells[i]=replace(cells[i],wf1=1)
        self.assertEqual(r.local_step(tuple(cells)).f1,1)
        self.assertEqual(r.local_step(tuple(cells)).wf2,0)

    def test_remote_posttransition_semantics_is_not_radius_five(self):
        # Two configurations identical throughout the center's radius five.
        # At target +3, the right Address vote includes +6,+7,+8.
        a={x:r.Cell(address=x%r.Q,age=96*r.Q+10,f2=int(-1<=x<=3)) for x in range(-5,9)}
        for e in range(-2,3):a[3+e]=replace(a[3+e],signal=1<<(2-e))
        b=dict(a)
        for x in (6,7,8):b[x]=replace(b[x],address=x+1)
        center_a=tuple(a[x] for x in range(-5,6));center_b=tuple(b[x] for x in range(-5,6))
        self.assertEqual(center_a,center_b)
        self.assertEqual(r.local_step(center_a),r.local_step(center_b))
        self.assertEqual(r.local_step(center_a).wf2,1)
        target_a=r.local_step(tuple(a[x] for x in range(-2,9)))
        target_b=r.local_step(tuple(b[x] for x in range(-2,9)))
        self.assertEqual(target_a.address,3);self.assertEqual(target_b.address,4)
        self.assertEqual((target_a.signal>>2)&1,1);self.assertEqual((target_b.signal>>2)&1,0)
        for count in (10,12):
            with self.assertRaises(ValueError):r.local_step((r.Cell(),)*count)
        with self.assertRaises(ValueError):r.voted_signal(center_a,4)


if __name__=='__main__':unittest.main()
