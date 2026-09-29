import unittest
from unittest.mock import patch
from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c, small_holder_program as p, small_holder_native as native
from gacsca.fixed_rule.wordcode import EQ
from experiments.fixed_rule import certify_small_holder_instruction_paths as paths
from experiments.fixed_rule.audit_small_holder_position_events import evaluate


class InstructionPaths(unittest.TestCase):
    def test_new_nonmemory_leaves_use_full_raw_rule(self):
        for key in paths.nonmemory_cases():
            self.assertEqual(paths.prove_leaf(key,paths.clock.regular_intervals()[0])['full_raw_outputs'],9*f.FIELDS)

    def test_matching_index_on_nonmemory_does_not_read(self):
        terms,raw=paths.leaf_prepare(('nonmem','flight_1'),paths.clock.regular_intervals()[0])
        old=tuple(raw(j) for j in f.NEIGHBORHOOD);wanted=raw(0,after=True)
        assignments={node[1]:0 for node in terms.nodes if node[0]=='variable'}
        assignments.update(physical_age=1,base_address=10000,meta_0_kind=c.NAND,meta_0_index=19,old_ra=19,old_value=77,data_0=23)
        values=evaluate(terms,assignments);self.assertTrue(terms.hypotheses_hold(values))
        neighbors=tuple(f.decode_cell(tuple(values[x] for x in row)) for row in old)
        result=f.local_step(neighbors);self.assertEqual(result,native.local_step(neighbors))
        self.assertEqual(f.encode_cell(result),tuple(values[x] for x in wanted))
        self.assertEqual(result.s3_phase,c.READ_A);self.assertEqual(result.s3_value,77)

    def test_alias_operands_share_one_old_memory_word(self):
        pc=next(i for i,op in enumerate(p.layout().instructions) if op.kind==EQ and op.a==op.b)
        path=paths.InstructionPath(pc);row=path.check()
        self.assertTrue(row['memory_aliases'])
        self.assertEqual(path.t.value(path.control['value']),1)

    def test_every_SEND_direction_and_hop_contract(self):
        for tag in range(16):
            pc=next(i for i,op in enumerate(p.layout().instructions) if op.kind==c.SEND and op.d==tag)
            path=paths.InstructionPath(pc);path.check();self.assertEqual(len(path.emissions),1)
            _,packet=path.emissions[0];track='lp' if tag&1 else 'rp'
            self.assertEqual(path.t.value(packet[track+'_valid']),1)
            self.assertEqual(path.t.value(packet[track+'_remaining']),tag>>1)
            self.assertEqual(path.writes,[])

    def test_dropped_packet_stale_field_and_tick_are_rejected(self):
        pcs={kind:next(i for i,op in enumerate(p.layout().instructions) if op.kind==kind) for kind in (c.SEND,c.LOAD,c.NAND)}
        class NoPacket(paths.InstructionPath):
            def event(self,key,**kwargs):
                super().event(key,**kwargs)
                if key[0]=='position' and key[1].startswith('send_'):self.emissions=[]
        class LostAlu(paths.InstructionPath):
            def event(self,key,**kwargs):
                super().event(key,**kwargs)
                if key==('position','load'):self.control['alu']=self.t.const(0)
        class LostTick(paths.InstructionPath):
            def seek(self,target,phase):super().seek(target,phase);self.elapsed-=1
        for cls,kind in ((NoPacket,c.SEND),(LostAlu,c.LOAD),(LostTick,c.NAND)):
            with self.assertRaises(AssertionError):cls(pcs[kind]).check()

    def test_both_IF_THIRD_branches_and_clock_domains(self):
        pc=next(i for i,op in enumerate(p.layout().instructions) if op.kind==c.IF_THIRD)
        for third in (False,True):
            path=paths.InstructionPath(pc,third=third);row=path.check()
            self.assertEqual(row['duration'],1);self.assertEqual(path.live,third)
            for lo,hi in row['legal_start_age_intervals']:
                self.assertEqual(c.RESET_AGES[2]<=lo<=hi<c.ACTIVE_ENDS[2],third)


if __name__=='__main__':unittest.main()
