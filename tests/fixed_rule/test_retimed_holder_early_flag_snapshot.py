import unittest
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_program as p,retimed_holder_quotient as q
from gacsca.fixed_rule import retimed_holder_resident_period as period
from gacsca.fixed_rule import retimed_holder_early_flags_gpu as early
from gacsca.fixed_rule.retimed_holder_early_flag_snapshot import View


def state():
    bank=np.zeros((1,p.layout().memory_count+5),dtype=np.uint64);bank[0,123]=11
    rows=np.zeros((1,period.SLOTS,len(q.SCHEMA)),dtype=np.uint64)
    for name,value in dict(address=123,age=640,data=11,head=1,phase=3,pc=71,ra=13,rb=17,rd=81,value=(1<<64)-7,alu=2,direction=1,lp_target=19,lp_data=23,lp_remaining=3,lp_valid=1,rp_target=29,rp_data=31,rp_remaining=4,rp_valid=1,f1=1).items():rows[0,0,q.COL[name]]=value
    flags=np.zeros((f.Q//64,2),dtype=np.uint64);flags[123//64,0]=np.uint64(1)<<np.uint64(123%64)
    return dict(bank=bank,active_rows=rows,counts=np.array([1],dtype=np.uint64),flags=flags,
                signals=np.zeros((1,2),dtype=np.uint64),age=np.array(640,dtype=np.uint64),time=np.array(4*f.U+640,dtype=np.uint64))


class EarlyFlagSnapshot(unittest.TestCase):
    def test_device_transition_body_is_unchanged(self):
        old=Path(early.old.__file__).with_suffix('.cu').read_text()
        self.assertEqual(early.source_text(),old.replace('age<WF_START-1||age>=PERIOD','age>=UINT64_C(32768)'))
        self.assertEqual(old.split('extern "C" int sf_create')[0],early.source_text().split('extern "C" int sf_create')[0])

    def test_flags_and_every_controller_copy_survive_view(self):
        initial=state();view=View(initial);sites=np.arange(121,126);raw=view.cells(sites)
        for d in f.OFFSETS:
            at=np.flatnonzero(sites+d==123)[0]
            for name,_ in f.PROCEDURE:
                self.assertEqual(raw[at,f.COL[f's{d+2}_{name}']],initial['active_rows'][0,0,q.COL[name]])
        self.assertEqual(raw[2,f.COL['f1']],1)
        self.assertEqual(np.count_nonzero(raw[:,f.COL['f1']]),1)

    def test_inconsistent_active_flag_is_rejected(self):
        initial=state();initial['active_rows'][0,0,q.COL['f1']]=0
        with self.assertRaises(AssertionError):View(initial)

    def test_view_rejects_clock_outside_early_domain(self):
        initial=state();initial['age']=np.array(32768,dtype=np.uint64)
        with self.assertRaisesRegex(ValueError,'early snapshot'):View(initial)

    def test_complete_exception_overrides_raw_controller(self):
        base=View(state());row=base.cells(np.array([123]));row[0,f.COL['s2_value']]=99
        self.assertEqual(View(state(),[123],row).cells(np.array([123]))[0,f.COL['s2_value']],99)
        with self.assertRaises(ValueError):View(state(),[123],row[:,:105])


if __name__=='__main__':unittest.main()
