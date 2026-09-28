import random
import unittest
from gacsca.fixed_rule.retimed_holder_spacetime_domain import eligible


class SpacetimeDomain(unittest.TestCase):
    def test_against_independent_counting(self):
        rng = random.Random(2026092712)
        for _ in range(10000):
            size = rng.randrange(11, 50)
            previous = {rng.randrange(size) for _ in range(rng.randrange(8))}
            current = {rng.randrange(size) for _ in range(rng.randrange(8))}
            expected = all(sum((p-start) % size < 11 for p in current) <= 2 and sum((p-start) % size < 5 for p in previous | current) <= 2 for start in range(size))
            self.assertEqual(eligible(previous, current, size=size), expected)

    def test_individual_pulses_do_not_imply_union_condition(self):
        self.assertTrue(eligible((), (20, 21), size=100))
        self.assertTrue(eligible((), (22,), size=100))
        self.assertFalse(eligible((20, 21), (22,), size=100))

    def test_support_can_move_or_repeat_and_wrap(self):
        self.assertTrue(eligible((20,), (21,), size=100))
        self.assertTrue(eligible((20, 21), (20, 21), size=100))
        self.assertTrue(eligible((99,), (0,), size=100))
        self.assertFalse(eligible((99, 0), (1,), size=100))
        # Previous residuals need only the five-site bound, not the eleven-site one.
        self.assertTrue(eligible((0, 5, 10), (), size=100))

    def test_positions_are_not_silently_wrapped(self):
        for previous, current, size in (((-1,), (), 100), ((), (100,), 100), ((), (), 10), ((True,), (), 100)):
            with self.assertRaises(ValueError):
                eligible(previous, current, size=size)


if __name__ == '__main__':
    unittest.main()
