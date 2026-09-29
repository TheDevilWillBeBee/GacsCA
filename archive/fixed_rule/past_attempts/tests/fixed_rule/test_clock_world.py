from dataclasses import replace
import random
import unittest
import numpy as np
from gacsca.fixed_rule import clock_rule as f,clock_projected as r,clock_program as p,clock_native
from gacsca.fixed_rule.clock_world import World,library,pointer
from gacsca.fixed_rule.clock_description import build


def blank(n=1,age=1):
    cores=r.project_array(p.template()).copy();cores[:,r.COL['age']]=age
    return np.tile(cores,(n,1))

def at(world,x):
    colony,address=divmod(x%(world.colonies*f.Q),f.Q);return world.cell(colony,address)


class ClockWorldTests(unittest.TestCase):
    def test_healthy_specialization_is_the_complete_rule_on_its_domain(self):
        rng=random.Random(2703);program=build(healthy_domain=True);lib=library()
        for age in (0,1,16*f.Q,32*f.Q,64*f.Q,72*f.Q,96*f.Q,98*f.Q-1,112*f.Q,120*f.Q,f.U-1):
            for _ in range(5):
                cells=tuple(f.Cell(**{n:rng.randrange(1<<w) for n,w in f.SCHEMA}) for _ in range(11))
                cells=tuple(replace(c,address=100+i-5,age=age,f1=0,f2=0,wf1=0,wf2=0) for i,c in enumerate(cells))
                expected=f.local_step(cells);raw=clock_native.array_from_cells(cells[3:8]);out=np.empty((1,f.FIELDS),dtype=np.uint64)
                lib.ww_healthy_local(pointer(raw),pointer(out))
                self.assertEqual(f.decode_cell(out[0].tolist()),expected)
                self.assertEqual(f.decode_cell(program.evaluate(tuple(raw.reshape(-1).tolist()))),expected)

    def test_scan_matches_literal_for_all_phases_both_directions(self):
        rng=random.Random(2704);g=p.layout();scanned=0
        for phase in range(8):
            for direction in range(2):
                core=blank(2)
                for colony in range(2):
                    a=100+colony*100
                    fields=dict(head=1,phase=phase,direction=direction,pc=g.description_instruction,
                                ra=177,rb=210,rd=144,value=1,alu=f.NAND)
                    for key,value in fields.items():core[colony*g.computation_cells+a,r.COL[key]]=value
                core[:,r.COL['data']]=np.array([rng.getrandbits(64) for _ in range(len(core))],dtype=np.uint64)
                with World(core) as fast,World(core) as literal:
                    metrics=fast.run(50000);literal.run(50000,skip_wait=False,skip_scan=False)
                    np.testing.assert_array_equal(fast.cores,literal.cores,err_msg=str((phase,direction)))
                    self.assertEqual(fast.pending,literal.pending);scanned+=metrics['scan_ticks_skipped']
        self.assertGreater(scanned,100000)

    def test_duplicate_heads_disable_unsafe_scan_and_match_literal(self):
        core=blank(2);g=p.layout()
        for address,direction in ((100,0),(125,1)):
            for name,value in dict(head=1,direction=direction,phase=f.WAIT_META,rd=33).items():core[address,r.COL[name]]=value
        with World(core) as fast,World(core) as literal:
            fast.run(1000);literal.run(1000,skip_wait=False,skip_scan=False)
            np.testing.assert_array_equal(fast.cores,literal.cores)

    def test_bulk_boundaries_match_full_native_local_rule(self):
        rng=np.random.default_rng(2705);g=p.layout()
        for age in (*f.RESET_AGES,72*f.Q,f.U-1):
            core=blank(age=age);core[:,r.COL['data']]=rng.integers(0,1<<63,len(core),dtype=np.uint64)
            core[100,r.COL['head']]=1;core[100,r.COL['phase']]=f.READ_B
            with World(core) as world:
                actual_old=tuple(at(world,x) for x in range(-5,g.computation_cells+5))
                expected_full=clock_native.cells_from_array(clock_native.dense_step(clock_native.array_from_cells(tuple(r.lift(c) for c in actual_old))))
                expected=r.array_from_cells(tuple(r.project(c) for c in expected_full[5:-5]))
                world.run(1);np.testing.assert_array_equal(world.cores,expected,err_msg=str(age))

    def test_mail_freezes_during_rest_and_is_erased_at_next_reset(self):
        g=p.layout();core=blank(age=16*f.Q-3)
        for name,value in dict(rp_valid=1,rp_target=7,rp_data=99,rp_remaining=1).items():core[g.computation_cells-1,r.COL[name]]=value
        with World(core) as world:
            world.run(3);position=g.computation_cells+2
            self.assertEqual(world.cell(0,position).rp_data,99)
            old=world.cell(0,position);world.run(16*f.Q)
            self.assertEqual(world.cell(0,position),replace(old,age=32*f.Q))
            self.assertEqual(world.pending,1);world.run(1)
            self.assertEqual(world.pending,0);self.assertEqual(world.cell(0,position).rp_valid,0)

    def test_partial_gather_schedule_and_raw_neighbor_histories(self):
        rng=random.Random(2706);g=p.layout()
        top=tuple(r.Cell(address=100+i,data=rng.getrandbits(64),phase=i%8,age=i,rd=rng.getrandbits(64)) for i in range(11))
        expected=tuple(f.encode_cell(r.lift(c)) for c in top)
        with World.encode(top) as world:
            world.run(16*f.Q)
            core=world.cores
            for colony in range(11):
                for neighbor in range(-5,6):
                    addresses=[colony*g.computation_cells+g.history(0,neighbor,k) for k in range(f.FIELDS)]
                    self.assertEqual(tuple(map(int,core[addresses,r.COL['data']])),expected[(colony+neighbor)%11])
            self.assertEqual(world.decode(),top)
            self.assertEqual(world.pending,0)
            self.assertFalse(np.any(core[:,r.COL['head']]))


if __name__=='__main__':unittest.main()
