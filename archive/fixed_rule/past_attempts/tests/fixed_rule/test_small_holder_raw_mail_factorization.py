from functools import lru_cache
import unittest

from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c, small_holder_native as native
from experiments.fixed_rule import certify_small_holder_raw_mail_factorization as proof


def neighborhood_source(*, age=1, target=100, corrupt=0, flags=False):
    """Canonical infinite local fixture, with a packet at relative primary -1."""
    @lru_cache(None)
    def cell(pos):
        values={name:0 for name,_ in f.SCHEMA}
        values.update(address=(100+pos)%f.Q,age=age,f1=int(flags and pos in (1,2,3)))
        for delta in f.STATIC_OFFSETS:
            values[f'p{delta+3}_index']=(100+pos+delta)%f.Q
        for delta in f.OFFSETS:
            values[f's{delta+2}_data']=7
            if pos+delta==-1:
                for suffix,value in (('target',target),('data',55),('remaining',0),('valid',1)):
                    name='rp_'+suffix
                    if pos in tuple(-1+e for e in f.OFFSETS)[:corrupt]:
                        value^=(1<<dict(c.SCHEMA)[name])-1
                    values[f's{delta+2}_{name}']=value
        return f.Cell(**values)
    return cell


def step_at(source,pos):
    neighbors=tuple(source(pos+j) for j in f.NEIGHBORHOOD)
    result=f.local_step(neighbors)
    assert result==native.local_step(neighbors)
    return result


class RawMailFactorization(unittest.TestCase):
    def test_every_phase_covers_independent_raw_replicas(self):
        for phase in (None,*range(8)):
            row=proof.certify_case(phase)
            self.assertEqual(row['all_clock_ages'],1<<32)
            self.assertTrue(row['independent_raw_mail_replicas'])

    def test_two_corrupt_mail_copies_correct_but_three_do_not(self):
        self.assertEqual(step_at(neighborhood_source(corrupt=2),0).s2_data,55)
        self.assertEqual(step_at(neighborhood_source(corrupt=3),0).s2_data,7)

    def test_rest_repairs_mail_copies_without_transport(self):
        source=neighborhood_source(age=c.ACTIVE_ENDS[0],corrupt=2)
        for e in f.OFFSETS:
            holder=-1+e
            out=step_at(source,holder)
            self.assertEqual((getattr(out,f's{2-e}_rp_target'),getattr(out,f's{2-e}_rp_data'),
                              getattr(out,f's{2-e}_rp_remaining'),getattr(out,f's{2-e}_rp_valid')),
                             (100,55,0,1))
        self.assertEqual(step_at(source,0).s2_data,7)

    def test_two_physical_steps_keep_flag_masked_replicas_raw(self):
        outcomes=[]
        for flags in (False,True):
            source=neighborhood_source(target=101,flags=flags)
            first={pos:step_at(source,pos) for pos in range(-6,9)}
            copies=[getattr(first[e],f's{2-e}_rp_valid') for e in f.OFFSETS]
            if flags:self.assertEqual(set(copies),{0,1})
            else:self.assertEqual(copies,[1]*5)
            # Feed the raw first-step cells directly to the next radius-seven F.
            outcomes.append(step_at(first.__getitem__,1).s2_data)
        self.assertEqual(outcomes,[55,7])


if __name__=='__main__':unittest.main()
