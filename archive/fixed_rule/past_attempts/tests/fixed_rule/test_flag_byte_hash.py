import random
import unittest
from gacsca.fixed_rule.flag_byte_hash import Engine,leaf_step,segments_from_words,evolve,FIRST,LAST,MASK,WORDS,BITS
from gacsca.fixed_rule.flag_pair_hash import leaf_step as wide_step,FIRST as WFIRST,LAST as WLAST
from gacsca.fixed_rule import delivery_rule as r
from gacsca.fixed_rule.flag_words import World,WORDS as WWORDS
import numpy as np


class FlagByteHashTests(unittest.TestCase):
    def test_eight_site_leaf_matches_wide_physical_rule(self):
        rng=random.Random(1052)
        for _ in range(1500):
            left,center,right=(rng.getrandbits(16) for _ in range(3));first,last=rng.randrange(2),rng.randrange(2)
            # Embed the eight-cell center at the appropriate physical word edge,
            # or interior, then compare those same eight output physical bits.
            for offset,tag in ((0,WFIRST if first else 0),(56,WLAST if last else 0),(24,0)):
                f=((left&MASK)|((center&MASK)<<8)|((right&MASK)<<16));g=((left>>8)|((center>>8)<<8)|((right>>8)<<16))
                if offset==0:wl=(f&255)<<56|((g&255)<<120);wc=((f>>8)&((1<<64)-1))|(((g>>8)&((1<<64)-1))<<64)|tag;wr=0;smalltag=FIRST if first else 0
                elif offset==56:wl=0;wc=((f&65535)<<48)|((g&65535)<<112)|tag;wr=(f>>16)|((g>>16)<<64);smalltag=LAST if last else 0
                else:wl=wr=0;wc=(f<<16)|(g<<80);smalltag=0
                out=wide_step(wl,wc,wr);expect=((out>>offset)&MASK)|(((out>>(64+offset))&MASK)<<8)|smalltag
                self.assertEqual(leaf_step(left,center|smalltag,right),expect)

    def test_literal_center_and_periodic_colony_profile(self):
        rng=random.Random(63)
        for level in range(2,8):
            values=[rng.getrandbits(18) for _ in range(1<<level)];e=Engine();nodes=[e.leaf(v) for v in values]
            while len(nodes)>1:nodes=[e.join(a,b) for a,b in zip(nodes[::2],nodes[1::2])]
            q=1<<(level-2)
            for ticks in (0,1,q//3,q):
                actual=e.center(nodes[0],ticks);old=values[:]
                for _ in range(ticks):old=[leaf_step(old[i-1] if i else 0,v,old[i+1] if i+1<len(old) else 0) for i,v in enumerate(old)]
                self.assertEqual([e.at(actual,i) for i in range(2*q)],old[q:3*q])
        rows=[(WWORDS//2,(1<<64)-1,(1<<64)-1),(WWORDS,0,(1<<64)-1)]
        e,initial,final=evolve(rows,1,98*r.Q,1000)
        with World((0,),(0,),age=98*r.Q,runs=rows) as world:
            world.run(1000);runs=world.runs
            for byte in (*range(20),*range(WORDS//2-20,WORDS//2+20),*range(WORDS-20,WORDS)):
                k=int(np.searchsorted(runs[:,0],byte//8,side='right'));shift=(byte%8)*8;v=e.at(final,byte)
                self.assertEqual(v&MASK,(int(runs[k,1])>>shift)&MASK)
                self.assertEqual((v>>BITS)&MASK,(int(runs[k,2])>>shift)&MASK)


if __name__=='__main__':unittest.main()
