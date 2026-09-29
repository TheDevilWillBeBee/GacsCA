import unittest
from experiments.fixed_rule.certify_retimed_holder_embedding_cones import interior


class EmbeddingCones(unittest.TestCase):
    def test_actual_radius_seven_complete_colonies(self):
        result = interior(8*32768, 65*32768, 116418)
        self.assertEqual(result['physical_interval'], [1077070, 1314994])
        self.assertEqual(result['complete_colonies'], list(range(33, 40)))

    def test_billion_tick_commit_cannot_be_claimed_from_this_cone(self):
        self.assertEqual(interior(8*32768, 65*32768, 914864220)['physical_interval'], [])

    def test_endpoint_rounding_and_all_admissible_neighborhoods(self):
        # Exhaustively compare the interval formula to one-step erosion on a
        # small line, retaining whole blocks only if every raw site survives.
        for radius in range(1, 5):
            for ticks in range(8):
                safe = set(range(3, 41))
                for _ in range(ticks):
                    safe = {x for x in safe if all(x+d in safe for d in range(-radius, radius+1))}
                result = interior(3, 41, ticks, radius=radius, block=4)
                expected = [col for col in range(11) if set(range(4*col, 4*col+4)) <= safe]
                self.assertEqual(result['complete_colonies'], expected)


if __name__ == '__main__':
    unittest.main()
