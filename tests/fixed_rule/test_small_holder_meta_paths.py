import unittest
from unittest.mock import patch
from gacsca.fixed_rule import small_holder_program as p, small_holder_core as c
from experiments.fixed_rule import certify_small_holder_meta_paths as paths


class MetaPaths(unittest.TestCase):
    def test_affine_bounds_and_nonempty_loop_domains(self):
        for lo in range(5):
            for hi in range(lo, 6):
                domain=(lo,hi)
                for slope in (-1,0,1):
                    for intercept in range(-5,6):
                        a=paths.Affine(slope,intercept)
                        values=[slope*q+intercept for q in range(lo,hi+1)]
                        self.assertEqual(a.bounds(domain),(min(values),max(values)))
                        good=[q for q in range(lo,hi+1) if slope*q+intercept>=1]
                        self.assertEqual(paths.nonempty_domain(a,domain),(good[0],good[-1]) if good else None)

    def test_all_actual_META_paths_and_start_clock_guards(self):
        rom=paths.verify_rom();self.assertEqual(rom['META_instructions'],98)
        L=rom['core_cells'];domains=((0,L-2),(L-1,L-1),(L,paths.f.Q-6),(paths.f.Q-5,paths.f.Q-1))
        for pc,op in enumerate(p.layout().instructions):
            if op.kind!=c.META:continue
            for domain in domains:
                row=paths.MetaPath(pc,domain).check()
                for (lo,hi),(start,end) in zip(paths.clock.regular_intervals(),row['legal_start_age_intervals']):
                    self.assertEqual(start,lo)
                    self.assertEqual(end+row['duration']-1,hi)
                self.assertTrue(row['complete_controller_and_one_Data_write'])

    def test_missing_last_marked_left_leaf_is_detected(self):
        pc=next(i for i,op in enumerate(p.layout().instructions) if op.kind==c.META)
        original=paths.template
        def wrong(key):return original(('scan','left_flight') if key==paths.LAST_LEFT else key)
        with patch.object(paths,'template',side_effect=wrong),self.assertRaisesRegex(AssertionError,'ROM precondition'):
            paths.MetaPath(pc,(0,len(p.base_rom())-2)).check()

    def test_lost_controller_and_skipped_reflection_are_detected(self):
        pc=next(i for i,op in enumerate(p.layout().instructions) if op.kind==c.META)
        class LostAlu(paths.MetaPath):
            def event(self,key,**kwargs):
                super().event(key,**kwargs)
                if key==('position','write'):self.control['alu']=self.t.const(0)
        class SkippedReflection(paths.MetaPath):
            def event(self,key,**kwargs):
                if key!=('scan','meta_unready_1'):super().event(key,**kwargs)
        for cls in (LostAlu,SkippedReflection):
            with self.assertRaises(AssertionError):cls(pc,(0,len(p.base_rom())-2)).check()

    def test_ROM_memory_index_and_endpoint_mutations_are_detected(self):
        for address,field,value in ((17,1,18),(len(p.base_rom())-1,6,0),(1,5,1)):
            rom=p.base_rom().copy();rom[address,field]=value
            with patch.object(p,'base_rom',return_value=rom),self.assertRaises(AssertionError):paths.verify_rom()

    def test_added_last_left_leaf_uses_full_descriptor(self):
        for interval in paths.clock.regular_intervals():
            self.assertEqual(paths.prove_last_left(interval)['full_raw_outputs'],9*paths.f.FIELDS)


if __name__=='__main__':unittest.main()
