import random
import unittest
from dataclasses import replace
from gacsca.fixed_rule import repair_b_rule as r,repair_b_native as native,repair_b_description
from gacsca.fixed_rule.word_prune import prune
from gacsca.fixed_rule.wordcode import Builder


def neighbors(address,age):return tuple(r.Cell(address=(address+j)%r.Q,age=age) for j in range(-5,6))


class RepairBRuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):cls.lib=native.library()

    def test_complete_scalar_unpruned_pruned_and_native_agree(self):
        rng=random.Random(15109);original=repair_b_description.build(optimize=False);small=r.self_description()
        self.assertEqual(original.inputs,small.inputs);self.assertEqual(len(original.outputs),r.FIELDS)
        self.assertLess(len(small.operations),len(original.operations))
        self.assertEqual(prune(small),small)
        for k in range(400):
            cells=tuple(r.Cell(**{n:rng.getrandbits(w) for n,w in r.SCHEMA}) for _ in range(11))
            if k<300:
                address=(0,1,3,5,100,r.Q-6,r.Q-5,r.Q-1)[k%8]
                age=(0,64*r.Q,70*r.Q,72*r.Q,r.CAPTURE_AGE-1,80*r.Q-1,96*r.Q,112*r.Q,120*r.Q-1)[k%9]
                cells=tuple(replace(c,address=(address+j)%r.Q,age=age) for j,c in zip(range(-5,6),cells))
            raw=tuple(w for c in cells for w in r.encode_cell(c))
            expected=r.local_step(cells)
            self.assertEqual(expected,r.decode_cell(original.evaluate(raw)))
            self.assertEqual(expected,r.decode_cell(small.evaluate(raw)))
            self.assertEqual(expected,native.local_step(cells,self.lib))

    def test_stage_gate_is_local_described_and_halts_stage_five(self):
        for age in (64*r.Q+1,70*r.Q+100,79*r.Q,112*r.Q+1,119*r.Q):
            cells=list(neighbors(101,age));cells[4]=replace(cells[4],head=1,kind=r.IF_THIRD,index=6,pc=6,phase=r.FETCH)
            out=r.local_step(tuple(cells))
            self.assertEqual(out.head,int(age<80*r.Q))
            self.assertEqual(out.pc,7 if age<80*r.Q else 0)
            self.assertEqual(out,native.local_step(tuple(cells),self.lib))
        # Metadata must still read the literal IF_THIRD kind, not a remapped
        # ordinary opcode used as an implementation shortcut.
        cells=list(neighbors(100,70*r.Q+1));cells[4]=replace(cells[4],kind=r.IF_THIRD,index=6,head=1,phase=r.READ_META,value=1,rd=99,ra=7,rb=0)
        self.assertEqual(r.local_step(tuple(cells)).value,r.IF_THIRD)

    def test_tail_buffer_metadata_fallback_is_part_of_the_rule(self):
        for address in (r.Q-6,r.Q-5,r.Q-1):
            for selector in range(8):
                cells=list(neighbors(0,70*r.Q+1));cells[5]=replace(cells[5],first=1,head=1,direction=1,phase=r.READ_META,value=1,rd=address,ra=123,rb=selector)
                expected=r.fallback(address,selector)
                out=r.local_step(tuple(cells))
                self.assertEqual(out.value,expected);self.assertEqual(out.rd,123)
                self.assertEqual(out,native.local_step(tuple(cells),self.lib))

    def test_buffer_receive_and_signal_capture_are_distinct_local_ticks(self):
        address=r.Q-3;cells=list(neighbors(address,r.CAPTURE_AGE-2))
        cells[5]=replace(cells[5],kind=r.MEM,index=address,a=31)
        cells[4]=replace(cells[4],rp_target=address,rp_data=1,rp_remaining=0,rp_valid=1)
        out=r.local_step(tuple(cells));self.assertEqual(out.data,1);self.assertEqual(out.signal,0);self.assertEqual(out.rp_valid,0)
        cells=list(neighbors(address,r.CAPTURE_AGE-1));cells[5]=out
        self.assertEqual(r.local_step(tuple(cells)).signal,4)

    def test_pruning_retains_raw_inputs_and_all_output_dependencies(self):
        b=Builder(3);unused=b.add(0,1);constant=b.const(7);out=b.add(2,constant)
        original=b.finish((out,0));small=prune(original)
        self.assertEqual(small.inputs,3);self.assertEqual(len(small.operations),2)
        for words in ((0,0,0),(1,2,3),((1<<64)-1,4,5)):
            self.assertEqual(original.evaluate(words),small.evaluate(words))


if __name__=='__main__':unittest.main()
