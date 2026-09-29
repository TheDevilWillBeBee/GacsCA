"""Distinguishing checks for the generic local gluing argument and entry guard."""
import unittest
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_program as p
from experiments.fixed_rule.join_retimed_holder_noisy_commit_embedding import guard_empty_tails, NAMES


def collars_equal(first, second, left, right, radius):
    assert first.shape == second.shape
    return (np.array_equal(first[left-radius:left+radius], second[left-radius:left+radius])
            and np.array_equal(first[right-radius:right+radius], second[right-radius:right+radius]))


def paste(first, second, left, right):
    result = second.copy()
    result[left:right] = first[left:right]
    return result


def local(array, radius):
    # An arbitrary nonlinear local map is sufficient to test the neighborhood
    # substitution lemma. This is not a replacement physical evolution backend.
    return (~(array & np.roll(array, radius, axis=0))) + np.roll(array, -radius, axis=0)


class Gluing(unittest.TestCase):
    def test_complete_word_neighborhood_substitution(self):
        rng = np.random.default_rng(20260927)
        for radius in (1, 3, 7):
            outer = rng.integers(0, 1 << 32, size=(61, f.FIELDS), dtype=np.uint64)
            inner = outer.copy()
            inner[20+radius:41-radius] ^= np.uint64(91)
            inner[:20-radius] ^= np.uint64(43)
            inner[41+radius:] ^= np.uint64(67)
            self.assertTrue(collars_equal(inner, outer, 20, 41, radius))
            np.testing.assert_array_equal(local(paste(inner, outer, 20, 41), radius),
                                          paste(local(inner, radius), local(outer, radius), 20, 41))

    def test_omitted_controller_word_or_thin_collar_breaks_the_join(self):
        outer = np.zeros((61, f.FIELDS), dtype=np.uint64)
        inner = outer.copy()
        inner[26, f.COL['s2_pc']] = 42
        self.assertTrue(collars_equal(inner, outer, 20, 41, 6))
        self.assertFalse(collars_equal(inner, outer, 20, 41, 7))
        self.assertFalse(np.array_equal(local(paste(inner, outer, 20, 41), 7),
                                        paste(local(inner, 7), local(outer, 7), 20, 41)))

    def test_only_named_exceptional_tail_is_allowed(self):
        words = np.zeros((3*f.Q, len(NAMES)), dtype=np.uint64)
        words[f.Q+len(p.base_rom())+17, NAMES.index('pc')] = 42
        self.assertEqual(guard_empty_tails(words, 3, {1}), [1])
        with self.assertRaisesRegex(AssertionError, 'unexpected tail controller'):
            guard_empty_tails(words, 3, set())
        with self.assertRaises(AssertionError):
            guard_empty_tails(words[:, :1], 3, {1})


if __name__ == '__main__':
    unittest.main()
