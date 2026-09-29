"""Failure tests for the new-ROM physical timing and proof bindings."""
import copy
import unittest

from gacsca.fixed_rule import retimed_holder_program as p, retimed_holder_rule as f
from gacsca.fixed_rule import small_holder_program as original_p
from experiments.fixed_rule import certify_retimed_holder_mail_schedule as schedule
from experiments.fixed_rule import certify_retimed_holder_paths as paths
from experiments.fixed_rule import certify_small_holder_instruction_paths as original_paths
from experiments.fixed_rule import certify_small_holder_mail_schedule as original_schedule
from experiments.fixed_rule.certify_retimed_holder_rom import Terms
from experiments.fixed_rule.certify_retimed_holder_meta_query_bounds import KnownBits


class RetimedComposition(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loaded=schedule.load_inputs()

    def test_all_six_phases_fit_with_complete_SEND_coverage(self):
        result=schedule.check(self.loaded)
        self.assertEqual(result['actual_SEND_sites_checked'],6478)
        self.assertEqual(len(result['phases']),6)
        self.assertTrue(all(row['margin']>0 for row in result['phases']))
        self.assertLess(max(row['head_stopped'] for row in result['phases']),f.U)

    def test_frozen_old_path_catalog_cannot_replace_new_paths(self):
        old=original_schedule.load_inputs()
        loaded=dict(self.loaded,ordinary=old['ordinary'])
        with self.assertRaises(AssertionError):schedule.check(loaded)

    def test_changed_duration_is_rejected(self):
        loaded=copy.deepcopy(self.loaded)
        row=next(row for row in loaded['ordinary']['rows'] if row[0]==0)
        row[3]+=1
        with self.assertRaises(AssertionError):schedule.check(loaded)

    def test_memory_index_alias_is_rejected(self):
        rom=p.base_rom().copy();rom[5,1]=6
        with self.assertRaises(AssertionError):schedule.verify_geometry(rom)

    def test_packet_collision_and_late_access_are_rejected(self):
        first=(1,10,100,200,0,100,110)
        with self.assertRaises(AssertionError):
            schedule.verify_packets([first,(2,20,110,220,0,110,130)],{})
        self.assertTrue(schedule.verify_packets([first],{200:(109,)})['all_destination_accesses_before_delivery'])
        with self.assertRaises(AssertionError):schedule.verify_packets([first],{200:(110,)})

    def test_new_bindings_preserve_original_proof_module(self):
        original_layout=original_p.layout();old_intervals=original_paths.clock.regular_intervals()
        path=paths.Ordinary(0);result=path.check()
        self.assertIs(path.g,p.layout())
        self.assertNotEqual(path.L,len(original_p.base_rom()))
        self.assertTrue(all(0<=lo<=hi<f.U for lo,hi in result['legal_start_age_intervals']))
        self.assertEqual(original_paths.clock.regular_intervals(),old_intervals)
        self.assertIs(original_paths.p,original_p)
        self.assertIs(original_p.layout(),original_layout)
        pc=1;target=p.layout().memory_count+pc
        dispatch=paths.Dispatch(target,pc);dispatch.rom=dispatch.rom.copy()
        dispatch.rom[target,1]=pc+1
        with self.assertRaises(AssertionError):dispatch.check()

    def test_query_proof_rejects_unbounded_and_off_by_one_width(self):
        terms=Terms(p.base_rom());known=KnownBits(terms)
        narrow=terms.variable('Address',15)
        self.assertEqual(known.valid_query(narrow),f.Q-1)
        for width in (16,64):
            with self.assertRaises(AssertionError):known.valid_query(terms.variable('wide_'+str(width),width))
        with self.assertRaises(AssertionError):known.valid_query(terms.const(f.Q))


if __name__=='__main__':unittest.main()
