import copy
import unittest

from gacsca.fixed_rule import small_holder_program as p
from experiments.fixed_rule import certify_small_holder_mail_schedule as proof


class MailSchedule(unittest.TestCase):
    def test_actual_schedule_covers_every_SEND_and_all_six_entries(self):
        result = proof.check(proof.load_inputs())
        self.assertEqual(result['actual_SEND_sites_checked'], 6478)
        self.assertEqual(len(result['phases']), 6)
        self.assertTrue(all(row['margin'] > 0 for row in result['phases']))

    def test_aliasing_a_memory_index_is_rejected(self):
        rom = p.base_rom().copy()
        rom[5, 1] = 6
        with self.assertRaises(AssertionError):
            proof.verify_geometry(rom)

    def test_same_track_overwrite_is_rejected(self):
        packets = [(1, 10, 100, 200, 0, 100, 110),
                   (2, 20, 110, 220, 0, 110, 130)]
        with self.assertRaises(AssertionError):
            proof.verify_packets(packets, {})

    def test_controller_access_at_delivery_is_rejected(self):
        packets = [(1, 10, 100, 200, 0, 100, 110)]
        self.assertTrue(proof.verify_packets(packets, {200: (109,)})['all_destination_accesses_before_delivery'])
        with self.assertRaises(AssertionError):
            proof.verify_packets(packets, {200: (110,)})

    def test_changed_instruction_duration_is_rejected(self):
        loaded = copy.deepcopy(proof.load_inputs())
        row = next(row for row in loaded['ordinary']['rows'] if row[0] == 0)
        row[3] += 1
        with self.assertRaises(AssertionError):
            proof.check(loaded)


if __name__ == '__main__':
    unittest.main()
