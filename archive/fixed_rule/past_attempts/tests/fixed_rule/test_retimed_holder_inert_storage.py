import unittest
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import retimed_holder_inert_storage as storage
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_literal_cone as cone


class InertStorage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with np.load('figs/fixed_rule/retimed_holder_contextual_macrostep_v1.npz',allow_pickle=False) as z:
            cls.words=z['final_words'].copy();cls.signals=z['final_signals'].copy()

    def test_unsupported_Data_rejected_before_gpu_allocation(self):
        words=self.words.copy();words[30000,storage.DATA]=17
        with patch.object(storage.general,'World',side_effect=AssertionError('GPU allocation should not occur')):
            with self.assertRaisesRegex(ValueError,'uncertified'):
                storage.World(words,self.signals,time=f.U+1)

    def test_missing_controller_word_rejected(self):
        with self.assertRaisesRegex(ValueError,'complete procedure'):
            storage.World(self.words[:,:-1],self.signals,time=f.U+1)

    def test_incorrect_entry_clock_rejected(self):
        with self.assertRaisesRegex(ValueError,'Age-one'):
            storage.World(self.words,self.signals,time=f.U+2)

    def test_native_rule_commutes_at_every_clock_boundary(self):
        rng=np.random.default_rng(2026092714)
        sites=np.arange(30940,30983)
        raw=rng.bit_generator.random_raw((len(sites),f.FIELDS))
        for i,(_,width) in enumerate(f.SCHEMA):
            if width<64:raw[:,i]&=np.uint64((1<<width)-1)
        raw[:,f.COL['address']]=sites
        cone.normalize(raw)
        values={30960:np.uint64(1<<63),30961:np.uint64(17),30962:np.uint64((1<<64)-1)}
        ages=sorted({0,f.U-1,17,*f.RESET_AGES,*f.VOTE_AGES,f.CAPTURE_AGE-1,f.WF_START-1,f.WF_START,f.WF_END-1,f.WF_END})
        for age in ages:
            before=raw.copy();before[:,f.COL['age']]=age
            for pos in values:
                for d in f.OFFSETS:before[pos-d-sites[0],f.COL[f's{d+2}_data']]=0
            noisy=before.copy()
            for pos,value in values.items():
                for d in f.OFFSETS:noisy[pos-d-sites[0],f.COL[f's{d+2}_data']]=value
            expected=cone.step(before)[7:-7].copy()
            actual=cone.step(noisy)[7:-7]
            for pos,value in values.items():
                for d in f.OFFSETS:
                    i,j=pos-d-sites[0]-7,f.COL[f's{d+2}_data']
                    self.assertEqual(int(expected[i,j]),0)
                    expected[i,j]=value
            np.testing.assert_array_equal(actual,expected,err_msg=f'Age {age}')


if __name__=='__main__':
    unittest.main()
