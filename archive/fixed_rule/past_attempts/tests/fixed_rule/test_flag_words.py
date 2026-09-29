import ctypes
import random
import unittest
from dataclasses import replace
import numpy as np
from gacsca.fixed_rule import delivery_rule as r,delivery_native as native
from gacsca.fixed_rule.flag_words import World,pack_sparse,library,pointer,MASK,WORDS
from gacsca.fixed_rule.flag2_bits import Flag2Bits


def record(position,age,bits,signals,colonies):
    position%=colonies*r.Q;colony,address=divmod(position,r.Q)
    signal=0
    for d in range(-2,3):
        target=address+d
        if target==3 and signals[1][colony]:signal|=1<<(d+2)
        if target==r.Q-3 and signals[0][colony]:signal|=1<<(d+2)
    return r.Cell(address=address,age=age,signal=signal,f1=bits&1,f2=(bits>>1)&1,wf1=(bits>>2)&1,wf2=(bits>>3)&1)


class FlagWordsTests(unittest.TestCase):
    def test_packed_word_matches_complete_native_rule_at_every_bit(self):
        rng=random.Random(862);lib=library();complete=native.library()
        for k in range(36):
            address=(0,64,r.Q-64)[k%3];age=(96*r.Q-1,96*r.Q,98*r.Q-1,98*r.Q)[k%4]
            signals=((k%2,),(int(k%3!=0),));raw=np.array([rng.getrandbits(64) for _ in range(6)],dtype=np.uint64)
            out=np.empty(2,dtype=np.uint64)
            lib.fw_word(pointer(raw),pointer(out),address==0,address==r.Q-64,signals[0][0],signals[1][0],96*r.Q<=age<98*r.Q)
            def cell(offset):
                index,bit=divmod(offset,64);f1=(int(raw[2*(index+1)])>>bit)&1;f2=(int(raw[2*(index+1)+1])>>bit)&1
                a=(address+offset)%r.Q;window=96*r.Q<=age<98*r.Q
                wf1=int(window and a>=r.Q-5 and signals[0][0]);wf2=int(window and a<=4 and signals[1][0] and not f1)
                return record(a,age,f1|2*f2|4*wf1|8*wf2,signals,1)
            for bit in range(64):
                value=native.local_step(tuple(cell(bit+j) for j in range(-5,6)),complete)
                self.assertEqual((int(out[0])>>bit)&1,value.f1,(k,bit,'f1'))
                self.assertEqual((int(out[1])>>bit)&1,value.f2,(k,bit,'f2'))

    def test_run_compression_matches_literal_full_neighborhoods_and_cross_colonies(self):
        rng=random.Random(963);colonies=3;signals=((1,0,1),(0,1,1))
        positions=[(c*r.Q+p)%(colonies*r.Q) for c in range(colonies) for p in (*range(-9,10),*range(61,68))]
        states={p:rng.randrange(4) for p in positions}
        with World(*signals,runs=pack_sparse(states,colonies)) as world:
            for tick in range(20):
                # All possible nonzero descendants of initial flags and forcing.
                support={((p+j)%(colonies*r.Q)) for p in states for j in range(-5,6)}
                support.update((c*r.Q+p)%(colonies*r.Q) for c in range(colonies) for p in (*range(-9,10),))
                age=world.info['age'];expected={}
                for position in support:
                    cells=tuple(record(position+j,age,world.cell(*divmod((position+j)%(colonies*r.Q),r.Q)),signals,colonies) for j in range(-5,6))
                    out=r.local_step(cells);value=out.f1|(out.f2<<1)|(out.wf1<<2)|(out.wf2<<3)
                    if value:expected[position]=value
                world.run(1,skip_fixed=False)
                for position in support:self.assertEqual(world.cell(*divmod(position,r.Q)),expected.get(position,0),(tick,position))
                states={p:v&3 for p,v in expected.items() if v&3}

    def test_exact_one_sided_bitplane_agrees_for_longer_prefix(self):
        slow=Flag2Bits(age=96*r.Q+1)
        with World((0,),(1,),age=slow.age) as world:
            for target in (1,2,64,257,1024,4096,65536):
                delta=target-slow.time;slow.run(delta);world.run(delta)
                runs=world.runs;bits=0;begin=0
                for end,f1,f2 in map(lambda row:tuple(map(int,row)),runs):
                    self.assertEqual(f1,0)
                    if f2:
                        for word in range(begin,end):bits|=f2<<(64*word)
                    begin=end
                self.assertEqual(bits,slow.bits)

    def test_fixed_skip_cannot_cross_forcing_clock_and_invalid_domain_rejected(self):
        with World((0,),(0,)) as fast,World((0,),(0,)) as slow:
            fast.run(32);slow.run(32,skip_fixed=False)
            np.testing.assert_array_equal(fast.runs,slow.runs);self.assertEqual(fast.info['age'],slow.info['age'])
            self.assertGreater(fast.info['quiet_ticks'],0)
            fast.run(r.U-1-fast.info['age']);self.assertEqual(fast.info['age'],r.U-1)
            fast.run(1);self.assertEqual(fast.info['age'],0)
            with self.assertRaises(ValueError):fast.run(1)
        for runs in ([(0,0,0)],[(WORDS-1,0,0)],[(WORDS,0,0),(WORDS-1,0,0)]):
            with self.assertRaises(ValueError):World((0,),(0,),runs=runs)


if __name__=='__main__':unittest.main()
