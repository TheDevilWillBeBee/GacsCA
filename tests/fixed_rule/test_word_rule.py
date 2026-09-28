from dataclasses import fields,replace
import random
import unittest
from gacsca.fixed_rule import word_rule as r
from gacsca.fixed_rule import word_native as native
from gacsca.level0_spec import Cfg,step_cell


def random_cell(rng):return r.Cell(**{name:rng.randrange(1<<width) for name,width in r.SCHEMA})
def healthy(rng=None,address=100,age=77):
    return tuple(replace(random_cell(rng) if rng else r.Cell(),address=(address+j)%r.Q,age=age,f1=0,f2=0,wf1=0,wf2=0) for j in range(-5,6))


class WordRuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.lib=native.library()

    def test_complete_raw_description_scalar_native(self):
        self.assertEqual(r.WIDTH,783);self.assertEqual(r.FIELDS,31)
        self.assertEqual(tuple(f.name for f in fields(r.Cell)),tuple(n for n,_ in r.SCHEMA))
        self.assertEqual(r.self_description().digest(),'43aa649dcea0e6b8c1fc2c5065b854e92c950d4c935549d5062b8f131ac62ffb')
        rng=random.Random(2181)
        cases=[tuple(random_cell(rng) for _ in range(11)) for _ in range(100)]
        cases += [healthy(rng,address=rng.randrange(r.Q),age=rng.randrange(r.U)) for _ in range(100)]
        for phase in range(8):
            for kind in range(16):
                for direction in range(2):
                    row=list(healthy())
                    cell=r.Cell(kind=kind,index=17,head=1,phase=phase,pc=17,ra=17,rb=17,
                                rd=17,value=(1<<64)-1,data=1<<63,alu=kind&7,direction=direction,
                                first=1,last=1,address=100,age=77,a=(1<<64)-1,b=63,d=29)
                    row[5]=cell;row[4]=replace(cell,address=99,first=0,last=0)
                    cases.append(tuple(row))
        for selector in (*range(9),(1<<64)-1):
            for ready in (0,1,1<<63):
                for direction in (0,1):
                    row=list(healthy());row[5]=replace(row[5],kind=15,index=0xFFFFFFFF,
                        a=(1<<64)-1,b=1<<63,d=0xABCDEF01,head=1,first=1,last=1,
                        phase=r.READ_META,value=ready,rd=100,rb=selector,direction=direction)
                    cases.append(tuple(row))
        for row in cases:
            expected=r.local_step(row)
            words=tuple(word for cell in row for word in r.encode_cell(cell))
            self.assertEqual(r.decode_cell(r.self_description().evaluate(words)),expected,row)
            self.assertEqual(native.local_step(row,self.lib),expected,row)
            for c in row:self.assertEqual(r.decode_cell(r.encode_cell(c)),c)

    def test_printed_maintenance_matches_independent_scalar_source(self):
        rng=random.Random(2182)
        cases=[healthy(address=a,age=t) for a in (0,1,4,5,r.Q-5,r.Q-1) for t in (0,15,r.U-1)]
        cases += [tuple(random_cell(rng) for _ in range(11)) for _ in range(100)]
        names=('age','f1','f2','wf1','wf2')
        for row in cases:
            cfg=Cfg(addr=[c.address for c in row],**{name:[getattr(c,name) for c in row] for name in names})
            a,t,f1,f2,_=step_cell(cfg,5,r.Q,r.U)
            self.assertEqual(r.maintenance(row),dict(address=a,age=t,f1=f1,f2=f2))

    def test_address_age_repair_and_printed_flag2_failure_execute(self):
        cells=list(healthy(age=r.U-1))
        cells[5]=replace(cells[5],address=234,age=321,f2=1,data=0x123456789ABCDEF0)
        expected=r.local_step(cells);actual=native.local_step(cells,self.lib)
        self.assertEqual(actual,expected)
        self.assertEqual((actual.address,actual.age,actual.f2),(100,0,1))
        self.assertEqual(actual.data,0x123456789ABCDEF0)

    def test_computed_flag1_clears_mail_and_changed_address_workspace(self):
        row=list(healthy());row[5]=replace(row[5],address=200,data=0xFF,head=1,pc=32,phase=6,value=1,rd=100)
        for i in (4,5,6):row[i]=replace(row[i],wf1=1)
        row[4]=replace(row[4],rp_valid=1,rp_data=99,rp_target=999,rp_remaining=3)
        out=native.local_step(row,self.lib)
        self.assertEqual(out.f1,1);self.assertEqual(out.address,100)
        for name in ('data','head',*r.CONTROL,'wf1','wf2','rp_valid','lp_valid'):
            self.assertEqual(getattr(out,name),0,name)

    def test_native_dense_radius_five_and_exterior_locality(self):
        rng=random.Random(2183)
        cells=tuple(random_cell(rng) for _ in range(21))
        expected=r.step_ring(cells)
        self.assertEqual(native.cells_from_array(native.dense_step(native.array_from_cells(cells),self.lib)),expected)
        for p in set(range(21))-set(range(5,16)):
            changed=list(cells);changed[p]=random_cell(rng)
            self.assertEqual(r.step_ring(changed)[10],expected[10])
        for n in (1,2,3,5):
            small=cells[:n]
            self.assertEqual(native.cells_from_array(native.dense_step(native.array_from_cells(small),self.lib)),r.step_ring(small))


if __name__=='__main__':unittest.main()
