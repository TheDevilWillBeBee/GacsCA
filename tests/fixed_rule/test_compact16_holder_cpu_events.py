"""Literal full-state cones and rejection checks for CPU physical events."""
import hashlib
import json
from pathlib import Path
import unittest
import numpy as np
from gacsca.fixed_rule import compact16_holder_cpu_events as e,compact16_holder_native as native
from gacsca.fixed_rule import compact16_holder_rule as f,compact16_holder_core as c,compact16_holder_program as p
from experiments.fixed_rule import certify_compact16_holder_clock_events as paths


def world(at,phase,*,direction=0,age=c.RESET_AGES[4]+100,**controls):
    data=np.zeros((1,f.Q),dtype=np.uint64)
    data[0,:p.layout().memory_count]=np.arange(p.layout().memory_count,dtype=np.uint64)*0x1234567
    fields=dict(head=1,phase=phase,pc=17,ra=73,rb=73,rd=73,value=0x123456789abcdef0,alu=c.NAND,direction=direction)
    fields.update(controls)
    return e.World(data,[[fields[name] for name in e.CONTROL]],[at],age=age)


def literal_cone(read,center,ticks):
    rows={pos:read(pos) for pos in range(center-7*ticks,center+7*ticks+1)}
    for t in range(ticks):
        radius=7*(ticks-t-1)
        rows={pos:native.local_step(tuple(rows[pos+j] for j in f.NEIGHBORHOOD)) for pos in range(center-radius,center+radius+1)}
    return rows[center]


class CPUEvents(unittest.TestCase):
    def test_short_bursts_match_complete_raw_literal_cones(self):
        cases=[(73,phase,direction,{}) for phase in (c.READ_A,c.READ_B,c.WRITE,c.READ_LOAD,c.WAIT_META) for direction in (0,1)]
        cases.extend((at,c.READ_B,direction,{}) for at in (0,len(p.base_rom())-1) for direction in (0,1))
        for selector in range(7):cases.append((len(p.base_rom())-1,c.READ_META,0,dict(rb=selector,rd=len(p.base_rom())-1,value=1)))
        cases.append((p.layout().memory_count+p.layout().entries[4],c.FETCH,0,dict(pc=p.layout().entries[4])))
        for at,phase,direction,extra in cases:
            w=world(at,phase,direction=direction,**extra)
            expected={pos:literal_cone(w.cell,pos,3) for pos in (at-2,at,at+2)}
            w.advance(3)
            for pos,wanted in expected.items():self.assertEqual(w.cell(pos),wanted,(at,phase,direction,pos))

    def test_SEND_rejection_preserves_every_stored_word(self):
        w=world(73,c.TRANSMIT,ra=73,rb=80,rd=0)
        before=(w.data.copy(),w.heads.copy(),w.where.copy(),w.age,w.time)
        with self.assertRaisesRegex(RuntimeError,'rejected \\(-3\\)'):w.advance(1)
        for actual,wanted in zip((w.data,w.heads,w.where),before[:3]):np.testing.assert_array_equal(actual,wanted)
        self.assertEqual((w.age,w.time),before[3:])

    def test_event_budget_rejection_is_atomic(self):
        pc=p.layout().entries[4];w=world(p.layout().memory_count+pc,c.FETCH,pc=pc)
        before=(w.data.copy(),w.heads.copy(),w.where.copy(),w.age)
        with self.assertRaisesRegex(RuntimeError,'rejected \\(-2\\)'):w.advance(200000,event_budget=1)
        for actual,wanted in zip((w.data,w.heads,w.where),before[:3]):np.testing.assert_array_equal(actual,wanted)
        self.assertEqual(w.age,before[3])

    def test_bulk_capture_and_wrap_boundaries_rejected(self):
        self.assertEqual(e.regular_intervals(),paths.regular_intervals())
        for age,ticks in ((c.RESET_AGES[4],1),(c.CAPTURE_AGE-2,2),(f.U-1,1)):
            w=world(73,c.READ_A,age=age)
            with self.assertRaisesRegex(ValueError,'regular physical clock'):w.advance(ticks)

    def test_distance_body_is_the_recertified_function(self):
        doc=json.loads(Path('figs/fixed_rule/compact16_holder_backend_distance_v1.json').read_text())
        self.assertTrue(doc['passed'])
        self.assertEqual(hashlib.sha256(e.distance_source().encode()).hexdigest(),doc['extracted_function_sha256'])
        self.assertEqual(hashlib.sha256(p.base_rom().tobytes()).hexdigest(),doc['rom_sha256'])

    def test_invalid_inactive_controller_and_nonmemory_data_rejected(self):
        with self.assertRaisesRegex(ValueError,'inactive controller'):world(0,0,head=0)
        w=world(73,c.READ_A);w.data[0,p.layout().memory_count]=1
        with self.assertRaisesRegex(ValueError,'non-MEM'):e.World(w.data,w.heads,w.where,age=w.age)

if __name__=='__main__':unittest.main()
