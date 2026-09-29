"""Complete live-controller snapshots, restoration and rejection checks."""
import os
import unittest
import numpy as np
from gacsca.fixed_rule import compact16_holder_active_snapshot as active
from gacsca.fixed_rule import compact16_holder_cuda_general_snapshot as snapshots
from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_records as q
from experiments.fixed_rule.validate_compact16_holder_endpoint import guard


def fixture():
    with np.load('figs/fixed_rule/compact16_holder_active_faults_v1.npz',allow_pickle=False) as z:
        state={key[len('checkpoint_'):]:z[key].copy() for key in z.files if key.startswith('checkpoint_') and key!='checkpoint_raw'}
        return state,z['checkpoint_raw'].copy(),z['after_raw'].copy()


class Checkpoint(unittest.TestCase):
    def test_raw_controller_is_preserved(self):
        state,raw,_=fixture();np.testing.assert_array_equal(active.render(state),raw)
        rows=state['active_rows'];head=int(np.flatnonzero(rows[0,:,q.COL['head']])[0]);address=int(rows[0,head,q.COL['address']])
        rows[0,head,q.COL['rb']]^=np.uint64(1)
        altered=active.render(state);different=np.argwhere(altered!=raw)
        self.assertEqual(len(different),5)
        self.assertEqual(set(map(tuple,different)),{((address-offset)%f.Q,f.COL[f's{offset+2}_rb']) for offset in f.OFFSETS})

    def test_inconsistent_data_and_missing_signal_rejected(self):
        state,_,_=fixture();at=int(np.flatnonzero(state['active_rows'][0,:,q.COL['head']])[0])
        state['active_rows'][0,at,q.COL['data']]^=np.uint64(1)
        with self.assertRaises(ValueError):active.render(state)
        state,_,_=fixture();at=int(np.flatnonzero(state['active_rows'][0,:,q.COL['signal']])[0])
        state['active_rows'][0,at,q.COL['signal']]=0
        with self.assertRaises(ValueError):active.render(state)

    @unittest.skipUnless(os.environ.get('FIXED_RULE_GPU_TESTS')=='1','explicit GPU test opt-in')
    def test_exact_restore_then_physical_tick(self):
        state,_,after=fixture()
        with active.restore(state) as world:
            observed=snapshots.snapshot(world)
            for key in state:np.testing.assert_array_equal(observed[key],state[key],err_msg=key)
            with guard():world.step()
            np.testing.assert_array_equal(active.render(snapshots.snapshot(world)),after)


if __name__=='__main__':unittest.main()
