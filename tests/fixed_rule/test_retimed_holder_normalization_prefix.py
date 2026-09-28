from dataclasses import replace
import unittest
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_core as c
from gacsca.fixed_rule import retimed_holder_program as p
from experiments.fixed_rule.certify_retimed_holder_normalization_prefix import analyze


class NormalizationPrefix(unittest.TestCase):
    def test_fixed_prefix_preserves_controller_inputs_and_mutable_Info(self):
        result = analyze()
        self.assertEqual(result['metadata_words_overwritten'], 49)
        self.assertEqual(result['normalization_age'], 10487886)
        self.assertEqual(result['first_SEND_birth_age'], 27674808)
        self.assertTrue(result['paired_controller_operands_and_META_queries_equal'])

    def test_reading_corrupt_metadata_before_overwrite_is_rejected(self):
        g = p.layout()
        instructions = list(g.instructions)
        first = next(i for i, op in enumerate(instructions) if op.kind == c.LOAD)
        instructions[first] = replace(instructions[first], a=g.info[0])
        with self.assertRaisesRegex(AssertionError, 'reads unnormalized metadata'):
            analyze(layout=replace(g, instructions=tuple(instructions)))

    def test_missing_metadata_destination_is_rejected(self):
        g = p.layout()
        instructions = list(g.instructions)
        meta = [i for i in range(128) if instructions[i].kind == c.META]
        instructions[meta[-1]] = replace(instructions[meta[-1]], a=instructions[meta[0]].a)
        with self.assertRaisesRegex(AssertionError, 'metadata not completely overwritten'):
            analyze(layout=replace(g, instructions=tuple(instructions)))

    def test_mutable_Info_write_is_rejected(self):
        g = p.layout()
        instructions = list(g.instructions)
        index = next(i for i in range(128) if instructions[i].kind == c.LIT)
        instructions[index] = replace(instructions[index], d=g.info[f.COL['address']])
        with self.assertRaisesRegex(AssertionError, 'normalizer changes mutable Info'):
            analyze(layout=replace(g, instructions=tuple(instructions)))


if __name__ == '__main__':
    unittest.main()
