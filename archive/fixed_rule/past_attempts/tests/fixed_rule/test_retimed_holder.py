"""Typed compiler identities and literal events with the new fixed hard-wiring."""
from dataclasses import replace
import random
import unittest

from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_core as c
from gacsca.fixed_rule import retimed_holder_program as p,retimed_holder_projected as r,retimed_holder_initial as initial
from gacsca.fixed_rule import small_holder_rule as old,retimed_holder_native as native
from experiments.fixed_rule import certify_retimed_holder_clock_transfer as transfer
from gacsca.fixed_rule.wordcode import Builder,Program,NAND,ADD,SHR,EQ,LT,LIT,MASK,arithmetic
from gacsca.fixed_rule.word_identity_optimization import optimize
from experiments.fixed_rule.certify_retimed_holder_rom import equivalence


class IdentityCompiler(unittest.TestCase):
    def test_short_clock_keeps_full_alphabet_and_wraps_high_age(self):
        self.assertEqual(f.SCHEMA,old.SCHEMA);self.assertEqual(f.NEIGHBORHOOD,old.NEIGHBORHOOD)
        self.assertEqual(f.U,1<<31)
        for age in (f.U-2,f.U-1,f.U,2*f.U-1):
            cells=tuple(r.lift(r.Cell(address=(100+j)%f.Q,age=age)) for j in f.NEIGHBORHOOD)
            result=f.local_step(cells)
            self.assertEqual(result.age,(age+1)%f.U)
            self.assertEqual(result,native.local_step(cells))
        legacy=old.local_step(tuple(old.decode_cell(f.encode_cell(x)) for x in cells))
        cells=tuple(r.lift(r.Cell(address=(100+j)%f.Q,age=f.U-1)) for j in f.NEIGHBORHOOD)
        self.assertEqual(old.local_step(tuple(old.decode_cell(f.encode_cell(x)) for x in cells)).age,f.U)
        self.assertEqual(f.local_step(cells).age,0)

    def test_old_wrap_cannot_certify_new_clock(self):
        with self.assertRaisesRegex(AssertionError,'wrong new clock wrap'):
            transfer.prove_interval((f.U-1,f.U-1),old.U-1,old.self_description())

    def test_literal_commit_wrap_and_next_reset(self):
        info=p.layout().info[f.COL['s2_pc']];hold=info+1;payload=0x12345678
        def logical(at):
            address=at%f.Q
            return c.Cell(**r.record(address),address=address,age=f.U-1,
                          data=payload if address==hold else 7 if address==info else 0)
        def start(at):return r.lift(initial.coherent_cell(logical,at))
        for center in (0,info,f.Q-1):
            middle={at:native.local_step(tuple(start(at+j) for j in f.NEIGHBORHOOD)) for at in range(center-7,center+8)}
            after=native.local_step(tuple(middle[center+j] for j in f.NEIGHBORHOOD))
            self.assertEqual(after,f.local_step(tuple(middle[center+j] for j in f.NEIGHBORHOOD)))
            self.assertEqual(middle[center].age,0);self.assertEqual(after.age,1)
            if center==info:
                self.assertEqual(middle[center].s2_data,payload);self.assertEqual(after.s2_data,payload)
            if center==0:
                self.assertEqual(after.s2_head,1);self.assertEqual(after.s2_pc,p.layout().entries[0])

    def test_typed_mask_identity_keeps_wide_word_case(self):
        b=Builder(1);program=b.finish((b.band(0,b.const(1)),))
        narrow,_=optimize(program,input_widths=(1,));wide,_=optimize(program,input_widths=(64,))
        self.assertEqual(narrow.outputs,(0,))
        self.assertNotEqual(wide.outputs,(0,))
        self.assertEqual(wide.evaluate((2,)),(0,))
        with self.assertRaises(ValueError):optimize(program,input_widths=())

    def test_word_edges_and_typed_ranges(self):
        rng=random.Random(2026092642)
        for width in (1,3,15,32,64):
            b=Builder(2);x,y=0,1;zero=b.const(0);outputs=[]
            outputs.extend((b.nand(x,zero),b.nand(x,b.inv(x)),b.inv(b.inv(x)),b.add(x,zero),b.add(x,b.inv(x))))
            outputs.extend((b.shr(x,b.const(64)),b.shr(x,zero),b.eq(x,x),b.lt(x,x),b.eq(x,b.const(1)),b.nonzero(x)))
            outputs.extend(b.op(op,x,y) for op in (NAND,ADD,SHR,EQ,LT))
            old=b.finish(tuple(outputs));new,_=optimize(old,input_widths=(width,64))
            for a in (0,1,(1<<width)-1,*[rng.getrandbits(width) for _ in range(30)]):
                for d in (0,1,63,64,MASK):self.assertEqual(old.evaluate((a,d)),new.evaluate((a,d)))

    def test_full_equivalence_and_missing_controller_output_rejected(self):
        self.assertEqual(equivalence()['complete_raw_outputs'],154)
        original=p.compiled_description();outputs=list(original.outputs)
        outputs[f.COL['s2_pc']]=original.inputs+len(original.operations)
        bad=Program(original.inputs,original.operations+((LIT,0,0),),tuple(outputs))
        with self.assertRaisesRegex(AssertionError,'s2_pc'):equivalence(bad)

    def test_fixed_identity_and_controller_encoding_at_three_depths(self):
        top=(r.Cell(address=13,age=19,s2_head=1,s2_phase=c.READ_META,s2_pc=29,s2_ra=31,s2_rb=5,s2_rd=91,s2_value=0x123456789abcdef0),)
        identity=r.identity();rom=p.base_rom().tobytes()
        for depth in (1,2,3):
            position=0 if depth==1 else p.layout().info[f.COL['s2_value']]
            self.assertEqual(initial.decode_parent(top,depth,position),initial.cell_at(top,depth-1,position))
            self.assertEqual(r.identity(),identity);self.assertEqual(p.base_rom().tobytes(),rom)

    def event(self,center,control,data=0x1020304050607080):
        age=c.VOTE_AGES[0]+17
        def logical(at):
            values=dict(r.record(at%f.Q),address=at%f.Q,age=age,data=data if at==center else 0)
            if at==center:values.update(control)
            return c.Cell(**values)
        def raw(at):return r.lift(initial.coherent_cell(logical,at))
        outputs={}
        for holder in range(center-3,center+4):
            neighborhood=tuple(raw(holder+j) for j in f.NEIGHBORHOOD)
            got=f.local_step(neighborhood)
            described=f.decode_cell(f.self_description().evaluate(tuple(w for row in neighborhood for w in f.encode_cell(row))))
            self.assertEqual(got,described)
            self.assertEqual(got,native.local_step(neighborhood))
            outputs[holder]=got
        return logical(center),outputs

    def test_literal_fetch_updates_complete_controller(self):
        pc=next(i for i in range(p.layout().description_instruction,len(p.layout().instructions)) if p.layout().instructions[i].kind==NAND)
        center=p.layout().memory_count+pc
        old,after=self.event(center,dict(head=1,phase=c.FETCH,pc=pc,ra=123,rb=456,rd=789,value=0xdeadbeef,alu=2,direction=0))
        wanted=c.advance(old)
        self.assertEqual(after[center+1].s2_head,1)
        for name,value in wanted.items():self.assertEqual(getattr(after[center+1],'s2_'+name),value,name)

    def test_literal_active_ALU_and_send(self):
        center=100;x=0xfedcba9876543210;y=0x1020304050607080
        _,after=self.event(center,dict(head=1,phase=c.READ_B,pc=19,rb=center,value=x,alu=NAND),data=y)
        self.assertEqual(after[center+1].s2_value,arithmetic(NAND,x,y))
        self.assertEqual(after[center+1].s2_phase,c.WRITE)
        _,after=self.event(center,dict(head=1,phase=c.TRANSMIT,pc=19,ra=center,rb=200,rd=7),data=y)
        self.assertEqual((after[center].s2_lp_valid,after[center].s2_lp_remaining,after[center].s2_lp_target,after[center].s2_lp_data),(1,3,200,y))
        self.assertEqual(after[center+1].s2_pc,20)

    def test_literal_META_reads_new_ROM_endpoint(self):
        center=len(p.base_rom())-1
        self.assertEqual(r.record(center)['last'],1)
        for selector,name in enumerate(c.STATIC):
            _,after=self.event(center,dict(head=1,phase=c.READ_META,pc=19,ra=50,rb=selector,rd=center,value=1))
            # Rightward head reflects at this actual new endpoint.
            self.assertEqual(after[center].s2_head,1)
            self.assertEqual(after[center].s2_value,r.record(center)[name])
            self.assertEqual(after[center].s2_phase,c.WAIT_META)
            self.assertEqual(after[center].s2_rd,50)
            self.assertEqual(after[center].s2_direction,c.LEFT)


if __name__=='__main__':unittest.main()
