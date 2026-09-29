import unittest
from gacsca.fixed_rule import small_holder_program as p,small_holder_rule as f,small_holder_core as c,small_holder_projected as r
from gacsca.fixed_rule.wordcode import ADD,NAND,SHR,EQ,LT,LIT,MASK,arithmetic
from experiments.fixed_rule.certify_small_holder_rom_dataflow import Terms,certify


class RomDataflow(unittest.TestCase):
    def test_complete_actual_rom_certificate(self):
        result=certify()
        self.assertTrue(result['passed']);self.assertEqual(result['complete_raw_outputs_per_colony'],154)
        self.assertEqual(result['input_raw_words'],15*154)
        self.assertEqual(result['descriptor_sha256'],'af2de0673ac685bb83e8a319751b7f10e22c05037809ff0479bdf292a789fbb6')
        self.assertTrue(result['not_an_execution_backend'])
        self.assertTrue(result['missing_physical_obligations'])

    def test_missing_raw_controller_output_is_rejected(self):
        g=p.layout();bad=p.base_rom().copy();target=g.hold[f.COL['s2_pc']]
        found=[i for i,op in enumerate(g.instructions) if i>=g.description_instruction and op.kind==ADD and op.d==target]
        self.assertEqual(len(found),1)
        # Still a legal supported instruction. Omit the raw controller output.
        bad[g.memory_count+found[0],0]=LIT;bad[g.memory_count+found[0],2]=0
        with self.assertRaisesRegex(AssertionError,'computed raw Hold mismatch'):certify(bad)

    def test_wrong_self_metadata_query_is_rejected(self):
        g=p.layout();bad=p.base_rom().copy()
        first=g.description_instruction+len(f.self_description().operations)+f.FIELDS
        i=next(i for i in range(first,len(g.instructions)) if g.instructions[i].kind==c.META)
        bad[g.memory_count+i,3]=7
        with self.assertRaisesRegex(AssertionError,'computed raw Hold mismatch'):certify(bad)

    def test_wrong_gather_route_and_Info_reset_are_rejected(self):
        g=p.layout();bad=p.base_rom().copy()
        i=next(i for i,op in enumerate(g.instructions) if op.kind==c.SEND)
        bad[g.memory_count+i,4]^=1
        with self.assertRaises(AssertionError):certify(bad)
        bad=p.base_rom().copy();bad[g.info[f.COL['address']],2]|=1
        with self.assertRaisesRegex(AssertionError,'Info not fully regenerated'):certify(bad)

    def test_symbolic_rewrites_and_total_ROM_lookup(self):
        terms=Terms(p.base_rom());a=terms.intern(('input',0,'a',64));zero=terms.const(0)
        self.assertEqual(terms.op(ADD,a,zero),a);self.assertEqual(terms.op(SHR,a,zero),a)
        self.assertEqual(terms.value(terms.op(EQ,a,a)),1)
        for op in (NAND,ADD,SHR,EQ,LT):
            for x in (0,1,63,64,MASK):
                for y in (0,1,63,64,MASK):self.assertEqual(terms.value(terms.op(op,terms.const(x),terms.const(y))),arithmetic(op,x,y))
        for address in (0,p.layout().memory_count-1,len(p.base_rom())-1,len(p.base_rom()),f.Q-5,f.Q-1):
            for selector in range(8):
                expected=r.record(address)[c.STATIC[selector]] if selector<7 else 0
                self.assertEqual(terms.value(terms.lookup(terms.const(address),selector)),expected)

if __name__=='__main__':unittest.main()
