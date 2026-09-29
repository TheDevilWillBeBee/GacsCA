"""Mutation and distinguishing tests for context and quiet-barrier premises."""
from dataclasses import replace
import unittest

from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c
from gacsca.fixed_rule.wordcode import Program,LIT
from experiments.fixed_rule import certify_small_holder_procedure_context as context
from experiments.fixed_rule import certify_small_holder_quiet_barriers as barrier
from experiments.fixed_rule.audit_small_holder_procedure_barriers import erase,quiet_expected
from experiments.fixed_rule.small_holder_flag_masked_mail_witnesses import initial


class ProcedureBarriers(unittest.TestCase):
    def test_context_dependency_in_controller_is_rejected(self):
        desc=f.self_description();out=list(desc.outputs)
        out[f.COL['s2_pc']]=7*f.FIELDS+f.COL['f1']
        with self.assertRaisesRegex(AssertionError,'context changes Data/controller'):
            context.certify(Program(desc.inputs,desc.operations,tuple(out)))

    def test_dropped_entry_pc_is_rejected(self):
        desc=f.self_description();out=list(desc.outputs)
        zero=next(desc.inputs+i for i,(op,a,_) in enumerate(desc.operations) if op==LIT and a==0)
        out[f.COL['s2_pc']]=zero
        with self.assertRaisesRegex(AssertionError,'quiet barrier'):
            barrier.certify(Program(desc.inputs,desc.operations,tuple(out)))

    def test_context_erasure_is_not_a_physical_time_step(self):
        source=initial(flags=True);out=[]
        for old in (source,lambda pos:erase(source(pos))):
            first={pos:f.local_step(tuple(old(pos+j) for j in f.NEIGHBORHOOD)) for pos in range(-6,9)}
            out.append(f.local_step(tuple(first[1+j] for j in f.NEIGHBORHOOD)).s2_data)
        self.assertEqual(out,[7,55])

    def test_canonical_geometry_is_necessary(self):
        cells=[replace(initial()(pos),f1=1,f2=1) for pos in f.NEIGHBORHOOD]
        cells[7]=replace(cells[7],address=1000)
        actual=f.local_step(tuple(cells));clean=f.local_step(tuple(map(erase,cells)))
        self.assertEqual(actual.address,100);self.assertEqual(actual.f1,1)
        self.assertEqual(actual.s2_data,0);self.assertNotEqual(actual.s2_data,clean.s2_data)

    def quiet(self,age,mark):
        cells=[]
        for pos in f.NEIGHBORHOOD:
            words=dict(address=(100+pos)%f.Q,age=age)
            for delta in f.STATIC_OFFSETS:
                words[f'p{delta+3}_index']=(100+pos+delta)%f.Q
                words[f'p{delta+3}_a']=mark if pos+delta==0 else 0
            for delta in f.OFFSETS:words[f's{delta+2}_data']={-1:1,1:3,2:1}.get(pos+delta,7)
            cells.append(f.Cell(**words))
        return cells

    def test_vote_reads_old_Data_and_overrides_simultaneous_reset(self):
        cells=self.quiet(c.RESET_AGES[4],31|c.VOTE)
        actual=f.local_step(tuple(cells));self.assertEqual(actual.s2_data,1)
        self.assertEqual(actual.s2_data,quiet_expected(tuple(cells))['s2_data'])

    def test_commit_reads_old_right_neighbor(self):
        cells=self.quiet(f.U-1,c.INFO)
        actual=f.local_step(tuple(cells));self.assertEqual(actual.s2_data,3)
        self.assertEqual(actual.age,0)

    def test_live_old_head_invalidates_quiet_reset_premise(self):
        cells=self.quiet(c.RESET_AGES[0],c.INFO)
        for i,pos in enumerate(f.NEIGHBORHOOD):
            for delta in f.OFFSETS:
                if pos+delta==0:
                    cells[i]=replace(cells[i],**{f's{delta+2}_{name}':value for name,value in
                        dict(head=1,phase=c.WRITE,rd=100,value=55,direction=c.RIGHT).items()})
        actual=f.local_step(tuple(cells));self.assertEqual(actual.s2_data,55)
        self.assertEqual(quiet_expected(tuple(cells))['s2_data'],7)


if __name__=='__main__':unittest.main()
