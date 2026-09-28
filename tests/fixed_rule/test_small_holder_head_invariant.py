"""Sound mask normalization and mutations that break the head invariant."""
import itertools
import random
import unittest

from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c
from gacsca.fixed_rule import small_holder_projected as r, small_holder_program as p
from gacsca.fixed_rule.wordcode import ADD, NAND, EQ, LT, SHR, LIT, Program, MASK
from experiments.fixed_rule.certify_small_holder_head_invariant import BooleanAbstraction, certify_case, geometry
from experiments.fixed_rule.certify_small_holder_clock_mail_factorization import ClockTerms
from experiments.fixed_rule.audit_small_holder_position_events import evaluate


class HeadInvariant(unittest.TestCase):
    def test_boolean_abstraction_matches_concrete_word_bits(self):
        t=ClockTerms(p.base_rom());flags=[t.variable('b'+str(i),1) for i in range(3)]
        x=t.variable('x',64);y=t.variable('y',64)
        condition=t.any(t.all(flags[0],flags[1]),flags[2])
        nested=t.select(condition,x,t.select(flags[0],y,t.const(0)))
        expressions=[condition,t.inv(condition),nested,t.modular_add(t.inv(condition),1,1),
                     t.op(ADD,t.inv(condition),t.const(1)),t.op(ADD,t.op(NAND,flags[0],flags[1]),t.const(1)),
                     t.modular_add(nested,0,32),t.modular_add(x,7,32),t.op(SHR,nested,t.const(17)),
                     t.op(EQ,x,y),t.op(LT,x,y),t.op(ADD,x,y),t.op(EQ,condition,flags[0])]
        proof=BooleanAbstraction(t)
        self.assertTrue(proof.boolean(condition));self.assertFalse(proof.boolean(x))
        abstract=[tuple(proof.bit(term,k) for k in range(64)) for term in expressions]
        rng=random.Random(2026092609)
        words=[(0,0),(MASK,MASK),(1,2),(MASK,0)]+[(rng.getrandbits(64),rng.getrandbits(64)) for _ in range(12)]
        for bits in itertools.product((0,1),repeat=3):
            for a,b in words:
                values=evaluate(t,dict(zip(('b0','b1','b2','x','y'),(*bits,a,b))))
                assignment=0
                for (term,k),node in proof.atoms.items():
                    var=proof.b.nodes[node][0]
                    assignment|=((values[term]>>k)&1)<<var
                for term,outputs in zip(expressions,abstract):
                    decoded=sum(proof.b.value(node,assignment)<<k for k,node in enumerate(outputs))
                    self.assertEqual(decoded,values[term])
        proof.close()

    def test_detects_head_creation_away_from_entry(self):
        desc=f.self_description();outputs=list(desc.outputs)
        one=next(desc.inputs+i for i,(kind,a,_) in enumerate(desc.operations) if kind==LIT and a==1)
        outputs[f.COL['s2_head']]=one
        mutant=Program(desc.inputs,desc.operations,tuple(outputs))
        with self.assertRaisesRegex(AssertionError,'head routing'):certify_case(None,mutant)

    def test_detects_stale_inactive_controller(self):
        desc=f.self_description();outputs=list(desc.outputs)
        one=next(desc.inputs+i for i,(kind,a,_) in enumerate(desc.operations) if kind==LIT and a==1)
        outputs[f.COL['s2_pc']]=one
        mutant=Program(desc.inputs,desc.operations,tuple(outputs))
        with self.assertRaisesRegex(AssertionError,'inactive controller'):certify_case(None,mutant)

    def test_ROM_endpoint_mutations_rejected(self):
        for field,address,value in (('first',1,1),('first',0,0),('last',len(p.base_rom())-1,0)):
            def changed(at):
                row=dict(r.record(at))
                if at==address:row[field]=value
                return row
            with self.assertRaisesRegex(AssertionError,'ROM endpoint defect'):geometry(changed)

    def test_fixed_core_isolated_at_local_head_dependency_radius(self):
        result=geometry()
        self.assertEqual(result['core_cells'],p.layout().computation_cells)
        self.assertGreaterEqual(result['minimum_gap_to_next_colony_core'],8)


if __name__=='__main__':unittest.main()
