from dataclasses import replace
import random
import unittest
from gacsca.fixed_rule import clock_rule as r,clock_native as native


def neighborhood(age=1,**center):
    row=[r.Cell(address=100+j,age=age) for j in range(-5,6)]
    row[5]=replace(row[5],**center);return tuple(row)


class ClockRuleTests(unittest.TestCase):
    def test_complete_clock_description_and_native_on_raw_and_boundary_states(self):
        rng=random.Random(2701);desc=r.self_description();lib=native.library()
        self.assertEqual(desc.inputs,11*r.FIELDS);self.assertEqual(len(desc.outputs),r.FIELDS)
        ages={0,r.U-1}
        for age in (*r.RESET_AGES,*r.ACTIVE_ENDS,*r.VOTE_AGES,98*r.Q):
            ages.update((age-1 if age else r.U-1,age,age+1))
        rows=[]
        for age in sorted(ages):
            for _ in range(4):
                row=[r.Cell(**{name:rng.randrange(1<<width) for name,width in r.SCHEMA}) for _ in range(11)]
                row=[replace(c,address=100+j-5,age=age,f1=0,f2=0,wf1=0,wf2=0) for j,c in enumerate(row)]
                row[5]=replace(row[5],kind=r.MEM,a=127,first=rng.randrange(2));rows.append(tuple(row))
        rows += [tuple(r.Cell(**{n:rng.randrange(1<<w) for n,w in r.SCHEMA}) for _ in range(11)) for _ in range(80)]
        for row in rows:
            expected=r.local_step(row)
            self.assertEqual(native.local_step(row,lib),expected)
            self.assertEqual(r.decode_cell(desc.evaluate(tuple(x for c in row for x in r.encode_cell(c)))),expected)

    def test_all_stage_entries_and_resets_use_encoded_program_fields(self):
        pcs=(11,22,33,44,55)
        for stage,age in enumerate(r.RESET_AGES):
            row=neighborhood(age,first=1,a=pcs[0]|pcs[1]<<32,b=pcs[2]|pcs[3]<<32,d=pcs[4],data=99,head=1,pc=123,phase=r.READ_META,value=99)
            out=r.local_step(row)
            self.assertEqual((out.head,out.pc,out.phase,out.data),(1,pcs[stage],0,0))
            for mask in range(32):
                row=neighborhood(age,kind=r.MEM,a=mask,data=99,head=1,pc=123,lp_valid=1)
                out=r.local_step(row)
                self.assertEqual(out.data,0 if mask&(1<<stage) else 99)
                self.assertEqual((out.head,out.pc,out.lp_valid),(0,0,0))
        row=neighborhood(72*r.Q,first=1,d=987,head=0)
        self.assertEqual((r.local_step(row).head,r.local_step(row).pc),(1,987))

    def test_vote_keeps_three_histories_and_is_bitwise(self):
        for age in r.VOTE_AGES:
            for values in ((3,5,6),(3,3,6),(3,5,3),(5,3,3)):
                row=list(neighborhood(age,kind=r.MEM,a=r.VOTE|31,data=99))
                for j,value in zip((-1,1,2),values):row[j+5]=replace(row[j+5],data=value)
                self.assertEqual(r.local_step(row).data,(values[0]&values[1])|(values[0]&values[2])|(values[1]&values[2]))
                row[5]=replace(row[5],a=0)
                self.assertEqual(r.local_step(row).data,99)

    def test_commit_then_next_reset_preserves_info(self):
        row=list(neighborhood(r.U-1,kind=r.MEM,a=r.INFO,data=123))
        row[6]=replace(row[6],data=987,a=31)
        out=r.local_step(row);self.assertEqual((out.data,out.age),(987,0))
        row=[replace(c,age=0) for c in row];row[5]=out
        self.assertEqual(r.local_step(row).data,987)
        # Reversing the copy/reset order would commit zero, distinguished above.

    def test_rests_preserve_workspace_except_source_clearing(self):
        rng=random.Random(2702)
        for age in (16*r.Q,33*r.Q-1,48*r.Q,80*r.Q,104*r.Q,120*r.Q):
            if r.active(age):continue
            values={n:rng.randrange(1<<w) for n,w in r.SCHEMA if n in r.SIMULATION}
            values['wf1']=values['wf2']=0
            row=neighborhood(age,**values);out=r.local_step(row)
            for name in r.SIMULATION:self.assertEqual(getattr(out,name),getattr(row[5],name),name)
        row=list(neighborhood(16*r.Q,address=200,head=1,data=7,lp_valid=1,pc=123))
        for j in (4,5,6):row[j]=replace(row[j],wf1=1)
        out=r.local_step(row)
        self.assertEqual((out.f1,out.address),(1,100))
        self.assertEqual((out.head,out.data,out.lp_valid,out.pc),(0,0,0,0))

    def test_halt_is_a_described_local_head_transition(self):
        row=list(neighborhood(1));row[4]=replace(row[4],head=1,kind=r.HALT,index=7,pc=7)
        self.assertEqual(r.local_step(row).head,0)
        row[4]=replace(row[4],pc=6)
        self.assertEqual(r.local_step(row).head,1)


if __name__=='__main__':unittest.main()
