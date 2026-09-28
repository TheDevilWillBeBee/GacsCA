from dataclasses import replace
from unittest.mock import patch
import unittest
import numpy as np
from gacsca.fixed_rule import delivery_rule as f,delivery_projected as r,delivery_program as p
from gacsca.fixed_rule.delivery_prefix_world import World as PrefixWorld
from gacsca.fixed_rule.delivery_control_world import World
from gacsca.fixed_rule.flag_words import World as Flags,pack_sparse
from gacsca.fixed_rule.wordcode import Program


def initial(top,age):
    with PrefixWorld.encode(top) as world:stored=world.stored
    stored[:,r.COL['age']]=age;return stored


class DeliveryControlTests(unittest.TestCase):
    def test_stage_five_gate_halt_and_actual_commit_without_host_evaluation(self):
        g=p.layout();top=(r.Cell(address=100,age=1,head=1,phase=f.WRITE,rd=100,value=0x123456789ABCDEF0),)
        expected=r.step_ring(top);stored=initial(top,112*f.Q);raw=f.encode_cell(r.lift(top[0]))
        for history in range(3):
            for neighbor in range(-5,6):stored[[g.history(history,neighbor,k) for k in range(f.FIELDS)],r.COL['data']]=raw
        ticks=g.timing_certificate()['evaluation_ticks']
        with World(stored) as world:
            with patch.object(Program,'evaluate',side_effect=AssertionError('host evaluation')),patch.object(f,'local_step',side_effect=AssertionError('host transition')):
                world.run(ticks-1);self.assertEqual(int(world.cores[:,r.COL['head']].sum()),1)
                world.run(1);self.assertFalse(np.any(world.cores[:,r.COL['head']]))
                world.run(16*f.Q-world.time)
            self.assertEqual(world.decode(),expected)
            self.assertEqual(world.decode()[0].data,0x123456789ABCDEF0)
            self.assertTrue(np.all(world.stored[:,r.COL['age']]==0));self.assertEqual(world.pending,0)
            with self.assertRaises(RuntimeError):world.run(1)

    def test_controller_and_actual_flags_compose_to_complete_local_outputs(self):
        g=p.layout();stored=initial((r.Cell(address=100),),112*f.Q+5);address=g.info[0]
        stored[address,r.COL['head']]=1;stored[address,r.COL['phase']]=f.WRITE;stored[address,r.COL['rd']]=address;stored[address,r.COL['value']]=81
        for sites in (np.arange(1,6),np.arange(g.computation_cells,g.computation_cells+5)):stored[sites,r.COL['signal']]=[16,8,4,2,1]
        positions=[0,1,3,4,5,address-1,address,address+1,f.Q-5,f.Q-3,f.Q-1]
        states={position:3 for position in range(address-8,address+9)}
        with World(stored) as control,Flags((1,),(1,),age=112*f.Q+5,runs=pack_sparse(states)) as flags:
            def cell(position):
                position%=f.Q;base=control.cell(0,position);value=flags.cell(0,position)
                return replace(base,f1=value&1,f2=(value>>1)&1,wf1=(value>>2)&1,wf2=(value>>3)&1)
            expected={position:r.local_step(tuple(cell(position+j) for j in range(-5,6))) for position in positions}
            control.run(1);flags.run(1)
            for position in positions:self.assertEqual(cell(position),expected[position])

    def test_initial_and_generated_mail_and_unrepresented_signals_are_rejected(self):
        stored=initial((r.Cell(address=100),),112*f.Q+5);g=p.layout()
        bad=stored.copy();bad[10,r.COL['lp_target']]=1
        with self.assertRaises(ValueError):World(bad)
        bad=stored.copy();bad[10,r.COL['signal']]=1
        with self.assertRaises(ValueError):World(bad)
        source=g.hold[0]
        stored[source,r.COL['head']]=1;stored[source,r.COL['phase']]=f.TRANSMIT;stored[source,r.COL['ra']]=source;stored[source,r.COL['rb']]=10
        with World(stored) as world:
            with self.assertRaises(RuntimeError):world.run(1)


if __name__=='__main__':unittest.main()
