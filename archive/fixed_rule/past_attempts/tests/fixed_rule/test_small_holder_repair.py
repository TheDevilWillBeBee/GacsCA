from dataclasses import replace
from functools import lru_cache
import random
import unittest
from gacsca.fixed_rule import small_holder_rule as f,small_holder_core as c,small_holder_projected as r,small_holder_program as p,small_holder_initial as initial
from gacsca.fixed_rule.small_holder_faults import recovery


def fixture(age,base,*,live=True):
    @lru_cache(maxsize=None)
    def logical(pos):
        address=(base+pos)%f.Q
        dynamic={'data':(address*0x9E3779B97F4A7C15)&((1<<64)-1)}
        if live and pos==0:dynamic.update(head=1,phase=c.WRITE,rd=address,value=0x123456789ABCDEF0)
        return c.Cell(**r.record(address),address=address,age=age,**dynamic)
    @lru_cache(maxsize=None)
    def read(pos):return initial.coherent_cell(logical,pos)
    return read


class HolderRepair(unittest.TestCase):
    def test_single_physical_Info_bit_is_repaired_in_one_tick(self):
        top=(r.Cell(address=100,s2_data=17),);base=p.layout().info[f.COL['s2_data']]
        @lru_cache(maxsize=None)
        def read(pos):return initial.cell_at(top,1,base+pos)
        dirty=replace(read(0),s2_data=read(0).s2_data^1)
        result=recovery(read,{0:dirty},1)
        self.assertTrue(result['restored'],result['mismatch'])
        # Every possibly affected output is included; equality extends globally
        # by the fixed local neighborhood, hence to every later noiseless tick.
        self.assertEqual(len(result['frames'][-1][0]),15)

    def test_two_bad_simulation_holders_repair_before_live_procedure(self):
        rng=random.Random(130);read=fixture(1,p.layout().info[3])
        faults={pos:replace(read(pos),**{f's{d+2}_{name}':rng.getrandbits(width) for d in f.OFFSETS for name,width in f.PROCEDURE}) for pos in (0,2)}
        result=recovery(read,faults,1);self.assertTrue(result['restored'],result['mismatch'])
        center=result['frames'][-1][1][-result['final_start']]
        self.assertEqual(center.s2_data,0x123456789ABCDEF0)

    def test_two_arbitrary_physical_holders_repair_in_two_ticks(self):
        rng=random.Random(917)
        for age in (0,1,f.VOTE_AGES[0],c.CAPTURE_AGE-1,f.WF_START-1,f.RESET_AGES[4],f.U-1):
            for base in (0,p.layout().info[3],p.layout().votes[10],p.layout().computation_cells-1,f.Q-3):
                read=fixture(age,base)
                faults={pos:r.Cell(**{name:rng.getrandbits(width) for name,width in r.SCHEMA}) for pos in (-1,1)}
                result=recovery(read,faults,2)
                self.assertTrue(result['restored'],(age,base,result['mismatch']))

    def test_three_bad_copies_are_outside_the_two_small_holder_contract(self):
        read=fixture(f.ACTIVE_ENDS[0]+10,p.layout().info[3],live=False)
        faults={pos:replace(read(pos),**{f's{2-pos}_data':getattr(read(pos),f's{2-pos}_data')^1}) for pos in (-1,0,1)}
        result=recovery(read,faults,1);self.assertFalse(result['restored'])

if __name__=='__main__':unittest.main()
