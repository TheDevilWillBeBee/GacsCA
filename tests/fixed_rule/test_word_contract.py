"""Negative controls for complete-state encoding and fixed evaluator closure."""
from dataclasses import replace
from unittest.mock import patch
import unittest
import numpy as np
from gacsca.fixed_rule import word_rule as f,word_projected as r,word_program as p
from gacsca.fixed_rule.wordcode import Program,LIT
from gacsca.fixed_rule.word_world import World


class WordContractTests(unittest.TestCase):
    def test_every_dynamic_field_survives_raw_encoding(self):
        g=p.layout();base=r.Cell(address=100)
        for name,width in r.SCHEMA:
            value=(1<<width)-1
            cell=replace(base,**{name:value})
            cores=r.encode_cores((cell,))
            self.assertEqual(r.decode_cores(cores),(cell,),name)
            self.assertEqual(int(cores[g.info_start+f.COL[name],r.COL['data']]),value,name)
            mutated=cores.copy()
            mutated[g.info_start+f.COL[name],r.COL['data']]^=np.uint64(1)
            if name=='address':
                with self.assertRaises(ValueError):r.decode_cores(mutated)
            else:self.assertNotEqual(r.decode_cores(mutated),(cell,),name)

    def test_compiler_contains_complete_description_and_all_raw_outputs(self):
        g=p.layout();description=f.self_description()
        self.assertEqual(description.inputs,11*f.FIELDS)
        self.assertEqual(len(description.outputs),f.FIELDS)
        actual=g.instructions[g.description_instruction:g.description_instruction+len(description.operations)]
        self.assertEqual(tuple((op.kind,op.a,op.b,op.d) for op in actual),
                         tuple((kind,a,b,description.inputs+i) for i,(kind,a,b) in enumerate(description.operations)))
        self.assertEqual(set(op.kind for op in actual),set(f.ALU_KINDS)|{LIT})
        reconstruct=g.instructions[g.regeneration_instruction:g.commit_instruction]
        self.assertEqual(len(reconstruct),2*len(f.STATIC))
        for selector in range(len(f.STATIC)):
            load,meta=reconstruct[2*selector:2*selector+2]
            self.assertEqual((load.kind,load.a),(f.LOAD,g.hold_start+f.COL['address']))
            self.assertEqual((meta.kind,meta.a,meta.b),(f.META,g.hold_start+f.COL[f.STATIC[selector]],selector))
        commit=g.instructions[g.commit_instruction:]
        self.assertEqual(len(commit),f.FIELDS)
        self.assertEqual(tuple(op.d for op in commit),tuple(range(g.info_start,g.info_start+f.FIELDS)))

    def test_physical_execution_does_not_invoke_python_upper_transition_or_evaluator(self):
        top=(r.Cell(address=100,head=1,phase=f.READ_B,rb=100,value=(1<<64)-1),)
        with World.encode(top) as world:
            before=world.cores
            with patch.object(Program,'evaluate',side_effect=AssertionError('host descriptor evaluation')), \
                 patch.object(f,'local_step',side_effect=AssertionError('host upper transition')), \
                 patch.object(r,'step_ring',side_effect=AssertionError('host upper transition')):
                world.run(10000)
            self.assertFalse(np.array_equal(world.cores,before))
            self.assertEqual(world.time,10000)


if __name__=='__main__':unittest.main()
