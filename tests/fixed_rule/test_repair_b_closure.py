from dataclasses import replace
import random
import unittest
from gacsca.fixed_rule import repair_b_rule as f,repair_b_projected as r,repair_b_program as p,repair_b_initial as initial,repair_b_native as native
from gacsca.fixed_rule.wordcode import LIT


class RepairBClosureTests(unittest.TestCase):
    def test_every_raw_word_follows_real_encoded_paths_at_three_depths(self):
        top=(r.Cell(**{name:(1<<width)-1 for name,width in r.SCHEMA}),r.Cell(address=0,signal=21,data=0x123456789ABCDEF0))
        g=p.layout();identity=r.identity()
        for depth in (1,2,3):
            for t,c in enumerate(top):
                for k,word in enumerate(f.encode_cell(r.lift(c))):
                    position=t*f.Q+g.info[k]
                    for _ in range(depth-1):position=position*f.Q+g.info[f.COL['data']]
                    raw=initial.cell_at(top,depth,position)
                    self.assertEqual(raw.data,word,(depth,t,k));self.assertEqual(len(r.encode_cell(raw)),25)
            self.assertEqual(initial.resources(len(top),depth)['fixed_rule'],identity)
            self.assertEqual(initial.decode_parent(top,depth,0),initial.cell_at(top,depth-1,0))
        self.assertEqual(r.WIDTH,590)

    def test_program_embeds_the_complete_description_including_its_controller(self):
        g=p.layout();d=f.self_description();start=g.description_instruction
        ops=g.instructions[start:start+len(d.operations)]
        self.assertEqual(tuple((op.kind,op.a,op.b,op.d) for op in ops),tuple((kind,a if kind==LIT else g.wires[a],0 if kind==LIT else g.wires[b],g.wires[d.inputs+i]) for i,(kind,a,b) in enumerate(d.operations)))
        copies=g.instructions[start+len(d.operations):start+len(d.operations)+f.FIELDS]
        self.assertEqual(tuple(op.a for op in copies),tuple(g.wires[w] for w in d.outputs))
        self.assertEqual(tuple(op.d for op in copies),g.hold)
        boot=f.decode_cell(p.template()[0].tolist());self.assertEqual(tuple(f.entry(boot,s) for s in range(5)),g.entries)

    def test_native_rule_reads_only_radius_five(self):
        rng=random.Random(11191)
        def cell():return f.Cell(**{name:rng.getrandbits(width) for name,width in f.SCHEMA})
        cells=tuple(cell() for _ in range(23));lib=native.library()
        original=native.cells_from_array(native.dense_step(native.array_from_cells(cells),lib))
        for outside in (*range(6),*range(17,23)):
            changed=list(cells);changed[outside]=cell()
            actual=native.cells_from_array(native.dense_step(native.array_from_cells(changed),lib))
            self.assertEqual(actual[11],original[11])
        self.assertEqual(original,f.step_ring(cells))

    def test_zero_payload_flagged_cap_is_an_exact_orbit_but_nonzero_is_not(self):
        for age in (0,1,*f.RESET_AGES,70*f.Q,f.CAPTURE_AGE-1,96*f.Q-1,96*f.Q,98*f.Q-1,f.U-1):
            top=initial.terminal_data(age=age)
            self.assertEqual(r.step_ring(top),(replace(top[0],age=(age+1)%f.U),))
        cap=replace(initial.terminal_data()[0],data=1)
        self.assertEqual(r.step_ring((cap,))[0].data,0)
        with self.assertRaises(ValueError):initial.terminal_data(payload=1)


if __name__=='__main__':unittest.main()
