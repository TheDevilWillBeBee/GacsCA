"""Physical pulses preserve inherited scratch and explicitly retain every bit."""
import unittest
import numpy as np
from gacsca.fixed_rule import retimed_holder_checkpoint_pulse as pulse
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_program as p


def faults(col,field):
    primary=col*f.Q+p.layout().info[field]
    return np.array([((primary-d)%(2*f.Q),f.COL[f's{d+2}_data'],1) for d in f.OFFSETS],dtype=np.uint64)


class CheckpointPulse(unittest.TestCase):
    def test_explicit_physical_set_and_scratch_preserved(self):
        g=p.layout();bank=np.arange(2*(g.memory_count+5),dtype=np.uint64).reshape(2,-1);original=bank.copy()
        bits=np.concatenate((faults(0,f.COL['s0_rb']),faults(1,f.COL['s1_rb'])))
        info,updates=pulse.apply(bank,bits);np.testing.assert_array_equal(bank,original)
        patched=bank.copy()
        for col,address,xor in updates:patched[int(col),int(address)]^=xor
        np.testing.assert_array_equal(patched[:,g.info],info)
        self.assertEqual(np.count_nonzero(patched!=bank),2)
        changed=[]
        for col,address,xor in updates:
            primary=int(col)*f.Q+int(address)
            for d in f.OFFSETS:changed.append(((primary-d)%(2*f.Q),f.COL[f's{d+2}_data'],int(xor)))
        self.assertEqual(sorted(changed),sorted(map(tuple,bits.tolist())))
        mask=np.ones(g.memory_count+5,dtype=bool);mask[list(g.info)]=False
        np.testing.assert_array_equal(patched[:,mask],bank[:,mask])

    def test_partial_and_wrong_field_patterns_rejected_without_mutation(self):
        g=p.layout();bank=np.ones((2,g.memory_count+5),dtype=np.uint64);bits=faults(0,0)
        badfield=bits.copy();badfield[0,1]=f.COL['age'];badbit=bits.copy();badbit[0,2]=2
        for bad in (bits[:4],np.concatenate((bits,bits[:1])),badfield,badbit):
            with self.assertRaises(ValueError):pulse.apply(bank,bad)
            self.assertTrue(np.all(bank==1))

    def test_empty_pulse_retains_complete_actual_info(self):
        g=p.layout();bank=np.arange(g.memory_count+5,dtype=np.uint64).reshape(1,-1)
        info,updates=pulse.apply(bank,np.empty((0,3),dtype=np.uint64))
        np.testing.assert_array_equal(info,bank[:,g.info]);self.assertEqual(updates.shape,(0,3))
        info[:]=0;self.assertTrue(np.any(bank[:,g.info]))

if __name__=='__main__':unittest.main()
