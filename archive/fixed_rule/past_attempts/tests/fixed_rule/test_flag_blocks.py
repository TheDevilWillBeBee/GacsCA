import random
import unittest
import numpy as np
from gacsca.fixed_rule.flag_words import World as Words,pack_sparse,WORDS,MASK
from gacsca.fixed_rule.flag_blocks import World,from_word_runs,BLOCK
from gacsca.fixed_rule import delivery_rule as r


def unpack(runs,colonies):
    total=colonies*WORDS;blocks=(total+BLOCK-1)//BLOCK
    out=np.zeros((blocks,BLOCK,2),dtype=np.uint64);begin=0
    for row in runs:
        end=int(row[0]);out[begin:end,:,0]=row[1:1+BLOCK];out[begin:end,:,1]=row[1+BLOCK:];begin=end
    return out.reshape(-1,2)[:total]


def unpack_words(runs,colonies):
    out=np.empty((colonies*WORDS,2),dtype=np.uint64);begin=0
    for end,a,b in runs:
        end=int(end);out[begin:end]=(a,b);begin=end
    return out


class FlagBlocksTests(unittest.TestCase):
    def test_lossless_uint64_conversion_and_partial_last_block(self):
        for colonies in (1,2,3,9):
            rows=[(3,MASK,1<<63),(WORDS,0,MASK)]
            if colonies>1:rows.append((colonies*WORDS,MASK,MASK))
            actual=from_word_runs(rows,colonies)
            np.testing.assert_array_equal(unpack(actual,colonies),unpack_words(rows,colonies))
            self.assertEqual(actual.dtype,np.uint64)
            with World((0,)*colonies,(0,)*colonies,runs=actual) as world:np.testing.assert_array_equal(world.runs,actual)

    def test_arbitrary_profiles_and_colony_edges_match_existing_word_engine(self):
        rng=random.Random(583)
        for colonies in (1,2,3):
            signals=(tuple(rng.randrange(2) for _ in range(colonies)),tuple(rng.randrange(2) for _ in range(colonies)))
            for age in (96*r.Q-1,98*r.Q-1,112*r.Q):
                states={(c*r.Q+p)%(colonies*r.Q):rng.randrange(4) for c in range(colonies) for p in (*range(-12,12),*range(570,580))}
                rows=pack_sparse(states,colonies)
                with Words(*signals,age=age,runs=rows) as old,World(*signals,age=age,runs=from_word_runs(rows,colonies)) as new:
                    for steps in (1,2,5,17):
                        old.run(steps,skip_fixed=False);new.run(steps,skip_fixed=False)
                        np.testing.assert_array_equal(unpack(new.runs,colonies),unpack_words(old.runs,colonies))

    def test_periodic_postforcing_profile_is_preserved_and_compressed(self):
        rows=[(WORDS,MASK,MASK)]
        with Words((1,),(1,),age=98*r.Q,runs=rows) as old,World((1,),(1,),age=98*r.Q,runs=from_word_runs(rows,1)) as new:
            for target in (1,100,10000):
                delta=target-old.info['time'];old.run(delta);new.run(delta)
                np.testing.assert_array_equal(unpack(new.runs,1),unpack_words(old.runs,1))
            self.assertGreater(old.info['runs'],300);self.assertLess(new.info['runs'],10)
            self.assertEqual(new.info['quiet_ticks'],0)

    def test_forcing_and_period_boundary_guards(self):
        with World((0,),(0,)) as world:
            world.run(r.U-(96*r.Q-1));self.assertEqual(world.info['age'],0)
            with self.assertRaises(ValueError):world.run(1)


if __name__=='__main__':unittest.main()
