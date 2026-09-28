"""Storage reuse must retain exact DAG meaning, all outputs and pinned values."""
from dataclasses import replace
import random
import unittest
from gacsca.fixed_rule.word_allocation import allocate,verify
from gacsca.fixed_rule.wordcode import Program,LIT,ADD,NAND,SHR,EQ,LT,arithmetic
from gacsca.fixed_rule import parallel_holder_rule as f, reuse_holder_program as p


def execute(program,allocation,words):
    verify(program,allocation);bank=[None]*allocation.count
    def read(w):return words[w] if w<program.inputs else bank[allocation.slots[w-program.inputs]]
    for i,(op,a,b) in enumerate(program.operations):
        bank[allocation.slots[i]]=a if op==LIT else arithmetic(op,read(a),read(b))
    return tuple(read(w) for w in program.outputs),tuple(read(w) for w in allocation.pins)


class WordAllocation(unittest.TestCase):
    def test_complete_controller_descriptor_for_arbitrary_raw_words(self):
        rng=random.Random(2837);d=f.self_description()
        zero=next(d.inputs+i for i,(op,a,b) in enumerate(d.operations) if op==LIT and a==0)
        a=allocate(d,pins=(zero,),capacity=p.RESULT_CAPACITY)
        self.assertEqual(a.count,362)
        for _ in range(64):
            words=[rng.getrandbits(64) for _ in range(d.inputs)]
            actual,pins=execute(d,a,words)
            self.assertEqual(actual,d.evaluate(words));self.assertEqual(pins,(0,))
        self.assertEqual(len(actual),f.FIELDS)

    def test_random_dags_all_word_operations_and_unused_results(self):
        rng=random.Random(2841)
        for _ in range(100):
            ops=[]
            for i in range(120):
                op=rng.choice((LIT,ADD,NAND,SHR,EQ,LT))
                ops.append((LIT,rng.getrandbits(64),0) if op==LIT else (op,rng.randrange(i+7),rng.randrange(i+7)))
            d=Program(7,tuple(ops),tuple(rng.randrange(127) for _ in range(20)))
            words=[rng.getrandbits(64) for _ in range(7)]
            for cap in (None,128):self.assertEqual(execute(d,allocate(d,capacity=cap),words)[0],d.evaluate(words))

    def test_output_retention_and_zero_pin_are_not_optional(self):
        d=Program(0,((LIT,0,0),(LIT,9,0),(LIT,3,0)),(2,))
        unpinned=allocate(d);pinned=allocate(d,pins=(0,))
        self.assertEqual((unpinned.count,pinned.count),(1,2))
        self.assertEqual(execute(d,pinned,()),((3,),(0,)))
        with self.assertRaises(ValueError):verify(d,replace(unpinned,pins=(0,)))
        with self.assertRaises(ValueError):verify(d,replace(pinned,slots=(0,0,0)))
        with self.assertRaises(ValueError):verify(replace(d,outputs=(1,)),pinned)

    def test_invalid_graph_and_insufficient_storage_rejected(self):
        for d in (Program(0,((ADD,0,0),),(0,)),Program(0,((99,0,0),),(0,)),Program(0,((LIT,-1,0),),(0,))):
            with self.assertRaises(ValueError):allocate(d)
        d=Program(0,((LIT,1,0),(LIT,2,0)),(0,1))
        with self.assertRaises(ValueError):allocate(d,capacity=1)
        with self.assertRaises(ValueError):allocate(d,pins=(20,))

if __name__=='__main__':unittest.main()
