from unittest.mock import patch
import random
import unittest
import numpy as np
from gacsca.fixed_rule import clock_rule as f,clock_projected as r,clock_program as p,clock_native as native
from gacsca.fixed_rule.wordcode import Program,LIT
from gacsca.fixed_rule.clock_world import World


class ClockClosureTests(unittest.TestCase):
    def test_compiler_embeds_complete_clock_description_and_raw_outputs(self):
        g=p.layout();d=f.self_description();start=g.description_instruction
        actual=g.instructions[start:start+len(d.operations)]
        self.assertEqual(tuple((op.kind,op.a,op.b,op.d) for op in actual),
            tuple((kind,a if kind==LIT else g.wires[a],0 if kind==LIT else g.wires[b],g.wires[d.inputs+i]) for i,(kind,a,b) in enumerate(d.operations)))
        output=g.instructions[start+len(d.operations):start+len(d.operations)+f.FIELDS]
        self.assertEqual(tuple(op.a for op in output),tuple(g.wires[w] for w in d.outputs))
        self.assertEqual(tuple(op.d for op in output),g.hold)
        meta=g.instructions[start+len(d.operations)+f.FIELDS:-1]
        self.assertEqual(len(meta),2*len(f.STATIC))
        for selector,name in enumerate(f.STATIC):
            load,lookup=meta[2*selector:2*selector+2]
            self.assertEqual((load.kind,load.a),(f.LOAD,g.hold[f.COL['address']]))
            self.assertEqual((lookup.kind,lookup.a,lookup.b),(f.META,g.hold[f.COL[name]],selector))
        boot=f.decode_cell(p.template()[0].tolist())
        self.assertEqual(tuple(f.entry(boot,stage) for stage in range(5)),g.entries)

    def test_native_locality_excludes_every_site_outside_radius_five(self):
        rng=random.Random(2708)
        def cell():return f.Cell(**{name:rng.randrange(1<<width) for name,width in f.SCHEMA})
        cells=tuple(cell() for _ in range(21));original=native.cells_from_array(native.dense_step(native.array_from_cells(cells)))
        for outside in (*range(5),*range(16,21)):
            changed=list(cells);changed[outside]=cell()
            actual=native.cells_from_array(native.dense_step(native.array_from_cells(changed)))
            self.assertEqual(actual[10],original[10],outside)
        self.assertEqual(original,f.step_ring(cells))

    def test_physical_stage_executes_without_python_transition_or_evaluation_callbacks(self):
        g=p.layout();top=(r.Cell(address=100,age=1,head=1,phase=f.READ_B,rb=100,value=f.MASK,data=f.MASK,alu=f.NAND),)
        expected=r.step_ring(top);raw=f.encode_cell(r.lift(top[0]));core=r.encode_cores(top);core[:,r.COL['age']]=112*f.Q
        for history in range(3):
            for neighbor in range(-5,6):
                core[[g.history(history,neighbor,k) for k in range(f.FIELDS)],r.COL['data']]=raw
        with World(core) as world:
            with patch.object(Program,'evaluate',side_effect=AssertionError('host evaluator')), \
                 patch.object(f,'local_step',side_effect=AssertionError('host transition')), \
                 patch.object(r,'step_ring',side_effect=AssertionError('host transition')), \
                 patch.object(native,'dense_step',side_effect=AssertionError('host transition')):
                result=world.run(16*f.Q)
            self.assertEqual(world.decode(),expected);self.assertTrue(world.check_boundary())
            self.assertEqual(result['physical_ticks'],16*f.Q);self.assertGreater(result['local_evaluations'],0)


if __name__=='__main__':unittest.main()
