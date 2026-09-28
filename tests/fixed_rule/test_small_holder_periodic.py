from dataclasses import replace
import random
import unittest
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import small_holder_rule as f,small_holder_native as native
from gacsca.fixed_rule import small_holder_raw_packed as packed,small_holder_periodic_cuda as gpu
from gacsca.fixed_rule import small_holder_projected as r,small_holder_initial as initial
from gacsca.fixed_rule import small_holder_periodic_initial as init,small_holder_prefix_world as prefix


class PeriodicWorld(unittest.TestCase):
    def test_all_raw_fields_pack_losslessly_and_reject_bad_padding(self):
        rng=random.Random(1293)
        raw=np.array([[rng.getrandbits(w) for _,w in f.SCHEMA] for _ in range(30)],dtype=np.uint64)
        self.assertEqual((packed.WIDTH,packed.WORDS),(4090,64))
        np.testing.assert_array_equal(packed.unpack(packed.pack(raw)),raw)
        bad=packed.pack(raw);bad[0,-1]|=np.uint64(1)<<np.uint64(63)
        with self.assertRaises(ValueError):packed.unpack(bad)
        raw[0,f.COL['age']]=f.U
        with self.assertRaises(ValueError):packed.pack(raw)

    def test_synchronous_global_evolution_matches_dense_ring(self):
        rng=random.Random(395)
        for period,repeats in ((1,43),(3,9),(17,3)):
            bg=tuple(f.Cell(**{n:rng.getrandbits(w) for n,w in f.SCHEMA}) for _ in range(period))
            dense=list(bg*repeats);size=len(dense)
            faults={0:replace(dense[0],age=0,s2_data=9),size-1:replace(dense[-1],f1=1-fault_flag(dense[-1]))}
            for pos,value in faults.items():dense[pos]=value
            with gpu.World(native.array_from_cells(bg),size,faults) as world:
                for step in range(5):
                    self.assertEqual(world.read(tuple(range(size))),tuple(dense))
                    direct=f.local_step(tuple(dense[j%size] for j in f.NEIGHBORHOOD))
                    dense=native.step_ring(tuple(dense));self.assertEqual(dense[0],direct)
                    with patch.object(f,'local_step',side_effect=AssertionError('CPU transition')),patch.object(native,'step_ring',side_effect=AssertionError('CPU transition')):
                        world.step()
                    self.assertEqual(world.time,step+1)
                self.assertEqual(world.read(tuple(range(size))),tuple(dense))
                self.assertLess(world.device_bytes,64*1024**2)

    def test_organized_colony_background_and_two_holder_repair(self):
        parent=r.Cell(address=123,age=9,s2_head=1,s2_pc=27,s2_value=987)
        bg=init.encoded_background(parent)
        for pos in (0,1,100,32765,32767):
            self.assertEqual(f.decode_cell(bg[pos].tolist()),r.lift(initial.cell_at((parent,),1,pos)))
        size=f.Q*3
        faults={}
        for pos in (100,101):
            values=dict(zip((n for n,_ in f.SCHEMA),map(int,bg[pos])))
            values.update({f's{k+2}_{n}':(1<<w)-1 for k in f.OFFSETS for n,w in f.PROCEDURE})
            faults[pos]=f.Cell(**values)
        probes=(0,1,2,7,98,99,100,101,102,103,f.Q-2,f.Q-1,f.Q,f.Q+2,size-1)
        with prefix.World.encode((parent,)) as reference,gpu.World(bg,size,faults) as world:
            self.assertEqual(len(world.positions),2)
            for step in range(4):
                world.step();reference.run(1)
                self.assertEqual(world.positions,())
                wanted=tuple(r.lift(reference.cell(0,pos%f.Q)) for pos in probes)
                self.assertEqual(world.read(probes),wanted)
            self.assertEqual(world.local_evaluations,4*f.Q+16)

    def test_capacity_rejection_is_atomic_and_empty_defects_stay_empty(self):
        bg=native.array_from_cells((f.Cell(),));size=30000
        faults={x:replace(f.Cell(),s2_data=1) for x in range(0,size,30)}
        with gpu.World(bg,size,faults) as world:
            before=world.read((0,1,29,30))
            with self.assertRaises(ValueError):world.step()
            self.assertEqual(world.time,0);self.assertEqual(world.read((0,1,29,30)),before)
        with gpu.World(bg,1) as world:
            for _ in range(3):world.step()
            self.assertEqual(world.positions,())
        with self.assertRaises(ValueError):world.read((0,))
        with self.assertRaises(ValueError):gpu.World(bg,0)
        with self.assertRaises(ValueError):gpu.World(np.repeat(bg,3,axis=0),4)


def fault_flag(cell):return cell.f1


if __name__=='__main__':unittest.main()
