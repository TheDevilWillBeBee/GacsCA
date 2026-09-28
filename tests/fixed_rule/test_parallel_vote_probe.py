"""The optimization must preserve locality and two-holder correction."""
from dataclasses import replace
from itertools import combinations
import random
import unittest
from gacsca.fixed_rule import holder_rule as f, parallel_vote_probe as v
from gacsca.fixed_rule.wordcode import LIT, MASK


def coherent(words):
    return tuple(f.Cell(**{f's{d+2}_data':words.get(x+d,0) for d in f.OFFSETS}) for x in range(-7,8))


def expected(words):
    out=[]
    for d in f.OFFSETS:
        a,b,c=(words.get(d+h,0) for h in v.HISTORY)
        out.append((a&b)|(a&c)|(b&c))
    return tuple(out)


class ParallelVoteProbe(unittest.TestCase):
    def test_all_boolean_inputs_and_arbitrary_raw_description(self):
        for mask in range(256):
            words={x:(mask>>(x+3))&1 for x in range(-3,5)}
            self.assertEqual(v.local_votes(coherent(words)),expected(words))
        rng=random.Random(827)
        for _ in range(128):
            cells=tuple(f.Cell(**{n:rng.getrandbits(w) for n,w in f.SCHEMA}) for _ in range(15))
            raw=tuple(z for cell in cells for z in f.encode_cell(cell))
            self.assertEqual(v.description().evaluate(raw),v.local_votes(cells))

    def test_every_pair_of_arbitrarily_corrupted_complete_holders(self):
        rng=random.Random(829)
        words={x:rng.getrandbits(64) for x in range(-9,10)}
        cells=coherent(words);want=expected(words)
        for a,b in combinations(range(15),2):
            damaged=list(cells)
            for i in (a,b):
                damaged[i]=f.Cell(**{n:rng.getrandbits(w) for n,w in f.SCHEMA})
            self.assertEqual(v.local_votes(damaged),want,(a,b))

    def test_exact_support_and_rejection_of_short_neighborhood(self):
        class Guard:
            def __len__(self):return 15
            def __getitem__(self,index):
                if index-7 not in v.SUPPORT:raise AssertionError('out-of-support read')
                return f.Cell()
        self.assertEqual(v.local_votes(Guard()),(0,)*5)
        self.assertEqual(v.SUPPORT,tuple(range(-5,7)))
        p=v.description();pending=list(p.outputs);seen=set();inputs=set()
        while pending:
            w=pending.pop()
            if w in seen:continue
            seen.add(w)
            if w<p.inputs:inputs.add(w);continue
            op,a,b=p.operations[w-p.inputs]
            if op!=LIT:pending.extend((a,b))
        self.assertEqual({w//f.FIELDS-7 for w in inputs},set(v.SUPPORT))
        self.assertTrue(all(f.SCHEMA[w%f.FIELDS][0].endswith('_data') for w in inputs))
        with self.assertRaises(ValueError):v.local_votes((f.Cell(),)*13)

    def test_radius_five_indistinguishability_and_three_fault_negative(self):
        worlds=[]
        for bit in (0,1):
            cells=list(coherent({1:0,3:1,4:bit}))
            for x in ((4,5) if bit==0 else (2,3)):
                key=f's{4-x+2}_data';cells[x+7]=replace(cells[x+7],**{key:1-bit})
            worlds.append(cells)
        self.assertEqual(worlds[0][2:13],worlds[1][2:13])
        self.assertEqual(v.local_votes(worlds[0])[-1],0)
        self.assertEqual(v.local_votes(worlds[1])[-1],1)
        words={1:0,3:MASK,4:0};cells=list(coherent(words))
        for x in (2,3,4):cells[x+7]=replace(cells[x+7],**{f's{4-x+2}_data':MASK})
        self.assertNotEqual(v.local_votes(cells),expected(words))

if __name__=='__main__':unittest.main()
