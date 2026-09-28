import unittest
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_program as p
from gacsca.fixed_rule import retimed_holder_literal_cone as cone
from gacsca.fixed_rule import retimed_holder_wide_inert_storage as storage
from experiments.fixed_rule.join_retimed_holder_full_ring_repair import post_reset_words, assert_only_metadata_changed


class FullRepairJoin(unittest.TestCase):
    def parent(self):
        row = np.array([(17*i+3) % (1 << width) for i, (_, width) in enumerate(f.SCHEMA)], dtype=np.uint64)
        return cone.normalize(row[None, :])[0]

    def test_every_encoded_controller_word_survives_the_expected_reset_frame(self):
        parent = self.parent()
        words = post_reset_words(parent, {30960: 123, 30961: 456, 30962: 789})
        np.testing.assert_array_equal(words[np.array(p.layout().info), storage.DATA], parent)
        self.assertEqual(int(words[0, storage.NAMES.index('head')]), 1)
        np.testing.assert_array_equal(words[[30960, 30961, 30962], storage.DATA], [123, 456, 789])
        with self.assertRaises(AssertionError):
            post_reset_words(parent[len(f.STATIC):])

    def test_diagnostic_normalization_cannot_change_mutable_controller_state(self):
        correct = self.parent()[None, :]
        malformed = correct.copy()
        malformed[:, :len(f.STATIC)] = 0
        assert_only_metadata_changed(malformed, correct)
        wrong = correct.copy()
        wrong[0, f.COL['s2_pc']] ^= np.uint64(1)
        with self.assertRaises(AssertionError):
            assert_only_metadata_changed(malformed, wrong)

    def test_uncertified_retained_address_is_rejected(self):
        with self.assertRaises(AssertionError):
            post_reset_words(self.parent(), {p.layout().info[0]: 123})


if __name__ == '__main__':
    unittest.main()
