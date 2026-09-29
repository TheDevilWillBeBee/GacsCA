"""Complete entry state, depth-independent encoding and timed-event mutations."""
from copy import deepcopy
from dataclasses import replace
from functools import lru_cache
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c, small_holder_projected as r
from gacsca.fixed_rule import small_holder_program as p, small_holder_initial as initial, small_holder_period_relation as relation
from experiments.fixed_rule import certify_small_holder_timed_dataflow as timed


class PeriodSemantics(unittest.TestCase):
    def parent(self):
        return r.Cell(address=123,age=19,s2_head=1,s2_phase=c.READ_META,s2_pc=17,
                      s2_ra=31,s2_rb=(1<<63)+5,s2_rd=(1<<64)-1,s2_value=77,
                      s2_alu=3,s2_direction=1,s2_rp_valid=1,s2_rp_data=1234567,signal=31)

    def test_all_raw_controller_fields_round_trip(self):
        parent=self.parent();read=lambda at:relation.encode_at(lambda col:parent,1,at)
        self.assertEqual(relation.decode_colony(read,1,0),parent)
        at=p.layout().info[f.COL['s2_pc']]
        bad_parent=replace(parent,s2_pc=0)
        bad=lambda pos:relation.encode_at(lambda col:bad_parent,1,pos)
        with self.assertRaisesRegex(ValueError,'represented raw state'):
            relation.validate_at(bad,1,at,parent=lambda col:parent)

    def test_physical_stale_controller_and_invalid_mail_rejected(self):
        parent=self.parent();base=lambda at:relation.encode_at(lambda col:parent,1,at)
        for field in ('s2_pc','s2_rp_target'):
            bad=lambda at:replace(base(at),**{field:1}) if at==100 else base(at)
            with self.assertRaisesRegex(ValueError,'controller/mail'):
                relation.validate_at(bad,1,100,parent=lambda col:parent)

    def test_retained_signal_and_scratch_are_allowed(self):
        parent=self.parent()
        read=lambda at:relation.encode_at(lambda col:parent,1,at,scratch=lambda at:(at+1)*17,signal=lambda at:31)
        for at in (0,1,5,f.Q-1,p.layout().info[0]):self.assertTrue(relation.validate_at(read,1,at,parent=lambda col:parent))

    def test_one_fixed_relation_at_three_initializer_depths(self):
        top=(self.parent(),);identity=(f.identity(),r.identity())
        for depth in (1,2,3):
            count=initial.physical_cells(len(top),depth-1)
            read=lru_cache(maxsize=64)(lambda pos:r.lift(initial.cell_at(top,depth,pos)))
            parent=lambda col:initial.cell_at(top,depth-1,col)
            col=0 if depth==1 else p.layout().info[f.COL['s2_pc']]
            for address in (0,1,p.layout().info[f.COL['s2_head']],p.layout().info[f.COL['s2_pc']],f.Q-1):
                self.assertTrue(relation.validate_at(read,count,col*f.Q+address,parent=parent))
            self.assertEqual(relation.decode_colony(read,count,col),parent(col))
            self.assertEqual((f.identity(),r.identity()),identity)
            read.cache_clear()

    def test_unmarked_scratch_mutation_rejected(self):
        def bad(address):
            row=dict(r.record(address))
            if address==1:row['a']=0
            return row
        with self.assertRaisesRegex(AssertionError,'scratch survives'):relation.layout_obligations(bad)

    def schedule(self):
        root=Path(__file__).resolve().parents[2]
        return json.loads((root/'figs/fixed_rule/small_holder_mail_schedule_v1.json').read_text())

    def test_packet_arrival_mutation_rejected(self):
        phase=deepcopy(self.schedule()['phases'][0]);phase['packets'][0][-1]+=1
        with self.assertRaises(AssertionError):timed.events(phase,p.layout())

    def test_dropping_real_operand_read_rejected(self):
        phase=self.schedule()['phases'][0];ref=timed.batch.Checker(p.base_rom());checker=timed.Timed(ref)
        ref.reset(0);checker.reset(0);original=timed.events
        def missing(phase,g):
            events,stop=original(phase,g)
            index=next(i for i,row in enumerate(events) if row[3]=='read_a')
            return events[:index]+events[index+1:],stop
        with patch.object(timed,'events',side_effect=missing):
            with self.assertRaises(AssertionError):checker.phase(phase)


if __name__=='__main__':unittest.main()
