from dataclasses import replace
import random
import unittest
from gacsca.fixed_rule import small_holder_rule as f,small_holder_core as c,small_holder_projected as r,small_holder_program as p,small_holder_initial as initial,small_holder_native as native

class HolderRule(unittest.TestCase):
    def test_arbitrary_raw_descriptor_native_and_scalar(self):
        rng=random.Random(90)
        for trial in range(120):
            cells=tuple(f.Cell(**{n:rng.getrandbits(w) for n,w in f.SCHEMA}) for _ in range(15))
            if trial%3:
                age=c.VOTE_AGES[trial%2]
                cells=tuple(replace(cell,age=age) for cell in cells)
                center=cells[7];changes={}
                for d in f.OFFSETS:changes.update({f'p{d+3}_kind':c.MEM,f'p{d+3}_first':0,f'p{d+3}_a':c.VOTE})
                cells=cells[:7]+(replace(center,**changes),)+cells[8:]
            want=f.local_step(cells);self.assertEqual(native.local_step(cells),want)
            self.assertEqual(f.decode_cell(f.self_description().evaluate(tuple(v for cell in cells for v in f.encode_cell(cell)))),want)
    def test_complete_self_description_and_three_depth_encoding(self):
        g=p.layout();d=f.self_description();self.assertTrue(g.timing_certificate()['fits'])
        from gacsca.fixed_rule.wordcode import LIT
        from gacsca.fixed_rule.wordcode import NAND,ADD,EQ
        def lowered(i,op,a,b):
            left,right=(a,0) if op==LIT else (g.wires[a],g.wires[b])
            if op in (NAND,ADD,EQ):left,right=sorted((left,right))
            return (op,left,right,g.wires[d.inputs+i])
        self.assertEqual(tuple((x.kind,x.a,x.b,x.d) for x in g.instructions[g.description_instruction:g.description_instruction+len(d.operations)]),tuple(lowered(i,*op) for i,op in enumerate(d.operations)))
        top=(r.Cell(**{n:(1<<w)-1 for n,w in r.SCHEMA}),);identity=r.identity()
        for depth in (1,2,3):
            self.assertEqual(initial.resources(1,depth)['fixed_rule'],identity)
            for k,value in enumerate(f.encode_cell(r.lift(top[0]))):
                pos=g.info[k]
                for _ in range(depth-1):pos=pos*f.Q+g.info[f.COL['s2_data']]
                self.assertEqual(initial.cell_at(top,depth,pos).s2_data,value,(depth,k))
            self.assertEqual(initial.decode_parent(top,depth,0),initial.cell_at(top,depth-1,0))
        self.assertEqual((f.FIELDS,len(r.SCHEMA),f.WIDTH,r.WIDTH),(154,105,4090,2704))
    def test_noiseless_coherent_procedures_match_the_logical_core(self):
        rng=random.Random(511)
        for age in (0,1,f.VOTE_AGES[0],c.CAPTURE_AGE-1,f.WF_START-1,f.RESET_AGES[4],f.U-1):
            logical={}
            for pos in range(-20,21):
                address=(p.layout().info[0]+pos)%f.Q
                static=r.record(address);dynamic={n:rng.getrandbits(w) for n,w in f.PROCEDURE}
                logical[pos]=c.Cell(**static,**dynamic,address=address,age=age)
            holders={pos:initial.coherent_cell(logical.__getitem__,pos) for pos in range(-10,11)}
            out=r.local_step(tuple(holders[pos] for pos in range(-7,8)))
            for d in f.OFFSETS:
                expected=c.local_step(tuple(logical[d+j] for j in range(-5,6)))
                for name,_ in f.PROCEDURE:self.assertEqual(getattr(out,f's{d+2}_{name}'),getattr(expected,name),(age,d,name))
            with self.assertRaises(ValueError):r.local_step(tuple(holders[pos] for pos in range(-6,7)))
    def test_native_fixed_neighborhood(self):
        rng=random.Random(413);cells=tuple(f.Cell(**{n:rng.getrandbits(w) for n,w in f.SCHEMA}) for _ in range(31));old=native.step_ring(cells)
        for pos in (0,7,23,30):
            changed=list(cells);changed[pos]=replace(changed[pos],address=(changed[pos].address+1)%f.Q,s2_data=0)
            self.assertEqual(native.step_ring(tuple(changed))[15],old[15])

if __name__=='__main__':unittest.main()
