from copy import deepcopy
from types import FunctionType, SimpleNamespace
import unittest
from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_program as p
from gacsca.fixed_rule import compact16_holder_projected as r
from gacsca.fixed_rule.wordcode import LIT, Program
from experiments.fixed_rule import compose_compact16_holder_noiseless_period as period
from experiments.fixed_rule import certify_compact16_holder_period_foundations as foundations
from experiments.fixed_rule import certify_compact16_holder_open_dataflow as opened
from experiments.fixed_rule import certify_compact16_holder_timed_dataflow as timed
from experiments.fixed_rule import certify_compact16_holder_rom as batch
from experiments.fixed_rule import certify_compact16_holder_head_invariant as head
from experiments.fixed_rule import join_compact16_holder_structural_invariant as structure


def bind(function, **changes):
    namespace = dict(function.__globals__, **changes)
    result = FunctionType(function.__code__, namespace, function.__name__,
                          function.__defaults__, function.__closure__)
    result.__kwdefaults__ = function.__kwdefaults__
    return result


class Compact16NoiselessPeriod(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.docs = period.load_inputs()
        cls.schedule = cls.docs['paths']['packet_schedule']

    def test_complete_period_and_phase_mutations(self):
        result = period.interfaces(self.docs)
        self.assertTrue(result['complete_entry_restored_at_commit'])
        self.assertEqual(len(result['phase_interfaces']), 6)
        for mode in ('missing_phase', 'late_halt', 'wide_query', 'mail_during_forcing', 'no_controller_output'):
            bad = deepcopy(self.docs)
            if mode == 'missing_phase':
                bad['paths']['packet_schedule']['phases'].pop()
            elif mode == 'late_halt':
                row = bad['paths']['packet_schedule']['phases'][0]
                row['head_stopped'] = row['deadline']
                next(item for item in bad['semantic']['timed']['phases'] if item['name']==row['name'])['head_stopped'] = row['deadline']
            elif mode == 'wide_query':
                bad['semantic']['queries']['maximum_possible_query_mask'] = f.Q
            elif mode == 'mail_during_forcing':
                bad['barriers']['signal_schedule_join']['no_SEND_during_or_after_forcing'] = False
            else:
                bad['rom']['equivalence']['complete_raw_outputs'] = 153
            with self.assertRaises((AssertionError, KeyError), msg=mode):
                period.interfaces(bad)

    def test_full_structural_domain_is_required(self):
        for mode in ('old_clock', 'missing_phase', 'unproved_structure', 'short_gap', 'coherent_mail_only', 'missing_entry_controller'):
            bad = deepcopy(self.docs)
            if mode == 'old_clock':
                bad['structural']['cases'][0]['head']['all_clock_ages'] = 1 << 31
            elif mode == 'missing_phase':
                bad['structural']['cases'].pop()
            elif mode == 'unproved_structure':
                bad['structural']['canonical_structural_domain_preserved'] = False
            elif mode == 'short_gap':
                bad['structural']['geometry']['minimum_gap_to_next_colony_core'] = 7
            elif mode == 'coherent_mail_only':
                bad['structural']['cases'][0]['raw_mail']['independent_raw_mail_replicas'] = False
            else:
                bad['entry']['represented_raw_fields'] = 153
            with self.assertRaises(AssertionError, msg=mode):
                period.interfaces(bad)

    def test_open_lattice_is_independent_of_wrapped_destination(self):
        class Scrambled(batch.Checker):
            def execute(self, *args, **kwargs):
                result = super().execute(*args, **kwargs)
                result['messages'] = [(row[0], 1000000, *row[2:]) for row in result['messages']]
                return result
        prove = bind(opened.certify, batch=SimpleNamespace(Checker=Scrambled))
        result = prove(self.schedule)
        self.assertTrue(result['center_commit_equals_normalized_full_descriptor'])
        self.assertFalse(result['periodic_destination_used'])

    def test_open_lattice_rejects_wrong_physical_direction(self):
        prove = bind(opened.certify, destination=lambda source, direction, hops: source+(hops if direction else -hops))
        with self.assertRaisesRegex(AssertionError, 'open history mismatch'):
            prove(self.schedule)

    def test_literal_ROM_change_breaks_timed_symbolic_refinement(self):
        rom = p.base_rom().copy()
        first_evaluation = p.layout().memory_count+p.layout().entries[4]
        self.assertEqual(int(rom[first_evaluation, 0]), LIT)
        self.assertEqual(int(rom[first_evaluation, 2]), (1 << 64)-1)
        rom[first_evaluation, 2] = 0
        with self.assertRaises(AssertionError):
            timed.prove(self.schedule, checker=batch.Checker(rom=rom))

    def test_query_bound_observes_instead_of_truncating(self):
        terms = foundations.QueryTerms(p.base_rom())
        narrow = terms.variable('narrow', 14)
        terms.lookup(narrow, 0)
        self.assertEqual(terms.query_mask, f.Q-1)
        wide = terms.variable('wide', 15)
        with self.assertRaisesRegex(AssertionError, 'META query exceeds'):
            terms.lookup(wide, 0)

    def test_output_alphabet_and_static_aliases_are_required(self):
        good = foundations.output_types()
        self.assertEqual(good['raw_outputs_checked'], 154)
        self.assertEqual(len(good['guarded_decrements']), 10)
        desc = f.self_description()
        outputs = list(desc.outputs)
        outputs[f.COL['s0_lp_remaining']] = desc.wires
        bad = Program(desc.inputs, desc.operations+((LIT, 8, 0),), tuple(outputs))
        with self.assertRaisesRegex(AssertionError, 'output exceeds fixed alphabet'):
            foundations.output_types(bad)
        outputs = list(desc.outputs)
        outputs[0] = desc.wires
        bad = Program(desc.inputs, desc.operations+((LIT, 0, 0),), tuple(outputs))
        with self.assertRaisesRegex(AssertionError, 'static metadata changed'):
            structure.support(bad)

    def test_actual_endpoint_and_history_preservation_are_required(self):
        last = len(p.base_rom())-1
        def no_endpoint(address):
            row = r.record(address)
            if address == last:
                row['last'] = 0
            return row
        with self.assertRaisesRegex(AssertionError, 'ROM endpoint defect'):
            head.geometry(no_endpoint)
        wire = p.layout().gathered_inputs[0]
        at = p.layout().history(0, wire//f.FIELDS-7, wire%f.FIELDS)
        def erased_history(address):
            row = r.record(address)
            if address == at:
                row['a'] |= 1 << 4
            return row
        check = bind(foundations.layout, r=SimpleNamespace(record=erased_history))
        with self.assertRaisesRegex(AssertionError, 'late reset erases a vote operand'):
            check()


if __name__ == '__main__':
    unittest.main()
