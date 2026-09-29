"""Local temporal-majority revision, not yet a redundant-controller rule."""
from dataclasses import replace
import random
import unittest
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import serial_vote_rule as f,serial_vote_projected as r,serial_vote_program as p,serial_vote_native as native,serial_vote_initial as initial
from gacsca.fixed_rule.serial_vote_prefix_world import World
from gacsca.fixed_rule.wordcode import Program,LIT

class SerialVote(unittest.TestCase):
    def test_complete_raw_rule_description_and_native(self):
        rng=random.Random(822);lib=native.library()
        for trial in range(250):
            cells=tuple(f.Cell(**{n:rng.getrandbits(w) for n,w in f.SCHEMA}) for _ in range(11))
            want=f.local_step(cells)
            self.assertEqual(native.local_step(cells,lib),want)
            self.assertEqual(f.decode_cell(f.self_description().evaluate(tuple(v for c in cells for v in f.encode_cell(c)))),want)

    def test_temporal_majorities_are_physical_NAND_operations(self):
        g=p.layout();rng=np.random.default_rng(415)
        with World.encode((r.Cell(address=100),)) as fresh:a=fresh.stored
        a[:,r.COL['age']]=f.VOTE_AGES[0]
        samples=rng.bit_generator.random_raw(3*11*f.FIELDS).reshape(3,-1)
        for stage in range(3):
            addresses=[g.history(stage,j,k) for j in range(-5,6) for k in range(f.FIELDS)]
            a[addresses,r.COL['data']]=samples[stage]
        a[np.array(g.votes),r.COL['data']]=42
        duration=g.schedule(g.entries[4],g.description_instruction)[0]
        with World(a) as w:
            w.run(1)
            np.testing.assert_array_equal(w.cores[np.array(g.votes),r.COL['data']],np.full(11*f.FIELDS,42,dtype=np.uint64))
            with patch.object(Program,'evaluate',side_effect=AssertionError('host evaluator')),patch.object(f,'local_step',side_effect=AssertionError('host upper transition')):w.run(duration-1)
            x,y,z=samples;np.testing.assert_array_equal(w.cores[np.array(g.votes),r.COL['data']],(x&y)|(x&z)|(y&z))
            for stage in range(3):
                addresses=[g.history(stage,j,k) for j in range(-5,6) for k in range(f.FIELDS)]
                np.testing.assert_array_equal(w.cores[addresses,r.COL['data']],samples[stage])

    def test_same_complete_description_and_capacity_at_every_depth(self):
        g=p.layout();d=f.self_description();start=g.description_instruction
        self.assertTrue(g.timing_certificate()['fits']);self.assertEqual(start-g.entries[4],6*d.inputs)
        self.assertEqual(tuple((x.kind,x.a,x.b,x.d) for x in g.instructions[start:start+len(d.operations)]),tuple((kind,a if kind==LIT else g.wires[a],0 if kind==LIT else g.wires[b],g.wires[d.inputs+i]) for i,(kind,a,b) in enumerate(d.operations)))
        cell=r.Cell(**{name:(1<<width)-1 for name,width in r.SCHEMA});identity=r.identity()
        for depth in (1,2,3):
            self.assertEqual(initial.resources(1,depth)['fixed_rule'],identity)
            for k,word in enumerate(f.encode_cell(r.lift(cell))):
                pos=g.info[k]
                for _ in range(depth-1):pos=pos*f.Q+g.info[f.COL['data']]
                self.assertEqual(initial.cell_at((cell,),depth,pos).data,word)
        self.assertEqual(r.WIDTH,594);self.assertEqual(f.NEIGHBORHOOD,tuple(range(-5,6)))

    def test_healthy_computation_no_longer_reads_data_at_distance_two(self):
        g=p.layout();address=g.votes[5*f.FIELDS]
        cells=tuple(r.lift(r.Cell(address=address+j,age=f.VOTE_AGES[0],data=(0xFFFF if j in (-1,1) else 0))) for j in range(-5,6))
        altered=list(cells);altered[7]=replace(altered[7],data=(1<<64)-1)
        self.assertEqual(f.local_step(cells).data,f.local_step(tuple(altered)).data)
        self.assertEqual(f.local_step(cells).data,cells[5].data)

if __name__=='__main__':unittest.main()
