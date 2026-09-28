import unittest
from dataclasses import replace
import numpy as np
from gacsca.fixed_rule import repair_b_rule as r,repair_b_program as p,repair_b_projected as g


class RepairBProgramTests(unittest.TestCase):
    def test_full_rom_and_schedule_include_actual_flag_delivery(self):
        x=p.layout();certificate=x.timing_certificate()
        self.assertTrue(certificate['fits']);self.assertEqual(certificate['descriptor_operations'],2648)
        self.assertEqual(x.description_sha256,r.self_description().digest())
        self.assertEqual(len(x.info),r.FIELDS);self.assertEqual(len(x.wires),r.self_description().wires)
        self.assertEqual(x.instructions[x.stage_ranges[4][1]-1].kind,r.IF_THIRD)
        send=x.instructions[x.stage_ranges[4][1]:x.delivery_range[1]-1]
        self.assertEqual(len(send),10)
        for op,target in zip(send,(*range(1,6),*range(r.Q-5,r.Q))):
            self.assertEqual(op.kind,r.SEND);self.assertEqual(op.b,target)
            self.assertEqual(op.a,x.hold[r.COL['f2' if target<6 else 'f1']])
        self.assertGreater(certificate['capture_margin'],0);self.assertGreater(certificate['evaluation_margin'],0)

    def test_buffer_metadata_and_raw_controller_encoding(self):
        x=p.layout()
        for address in (1,5,r.Q-6,r.Q-5,r.Q-1):
            raw=g.lift(g.Cell(address=address))
            if address>=r.Q-5:
                self.assertEqual((raw.kind,raw.index,raw.a),(r.MEM,address,31))
                self.assertEqual(tuple(getattr(raw,n) for n in r.STATIC),tuple(r.fallback(address,i) for i in range(7)))
        top=g.Cell(**{n:(1<<w)-1 for n,w in g.SCHEMA})
        core=g.encode_cores((top,));self.assertEqual(g.decode_cores(core),(top,))
        self.assertEqual(tuple(map(int,core[np.array(x.info),g.COL['data']])),r.encode_cell(g.lift(top)))
        for name in (*r.CONTROL,'head','signal'):
            changed=core.copy();changed[x.info[r.COL[name]],g.COL['data']]=0
            self.assertNotEqual(g.decode_cores(changed),(top,))
        self.assertEqual(g.WIDTH,590);self.assertEqual(len(g.SCHEMA),25)


if __name__=='__main__':unittest.main()
