"""Guard soundness, alphabet closure, and physical-period interface mutations."""
from copy import deepcopy
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from gacsca.fixed_rule import retimed_holder_projected as projected
from experiments.fixed_rule import certify_retimed_holder_local_transfer as transfer
from experiments.fixed_rule import join_small_holder_structural_invariant as structure
from gacsca.fixed_rule.wordcode import Builder, Program, LIT, MASK, arithmetic
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_program as p
from experiments.fixed_rule.certify_small_holder_rom_dataflow import Terms
from experiments.fixed_rule.small_holder_guarded_bounds import GuardedBounds
from experiments.fixed_rule import compose_retimed_holder_noiseless_period as period
from experiments.fixed_rule import certify_retimed_holder_open_dataflow as opened


def counter_description(mode='guarded'):
    b=Builder(3);count,edge,other=0,1,2
    guard=b.all(edge,b.nonzero(other if mode=='wrong_counter' else count))
    if mode=='unguarded':guard=edge
    decrement=b.add(count,b.const(MASK))
    return b.finish((b.select(guard,decrement,count),))


def bounds(description, edge_width=1):
    t=Terms(p.base_rom())
    inputs=tuple(t.intern(('input',0,name,width)) for name,width in (('count',3),('edge',edge_width),('other',3)))
    output=t.expression(description,inputs)[0];known=GuardedBounds(t)
    return known.at(output),known


def evaluate(description, inputs):
    values=list(inputs)
    for op,a,b in description.operations:
        values.append(a&MASK if op==LIT else arithmetic(op,values[a],values[b]))
    return values[description.outputs[0]]


class NoiselessPeriod(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.loaded=period.load_inputs()

    def test_guarded_decrement_exhaustive(self):
        description=counter_description();(ones,zeros),known=bounds(description)
        self.assertEqual(ones,7);self.assertTrue(known.refinements)
        for count in range(8):
            for edge in range(2):
                for other in range(8):
                    result=evaluate(description,(count,edge,other))
                    self.assertEqual(result,count-int(bool(count and edge)))
                    self.assertEqual(result&(MASK^ones),0)
                    self.assertEqual((MASK^result)&(MASK^zeros),0)

    def test_missing_or_wrong_guard_not_certified(self):
        for mode in ('unguarded','wrong_counter'):
            description=counter_description(mode);(ones,_),known=bounds(description)
            self.assertEqual(ones,MASK);self.assertFalse(known.refinements)
            self.assertEqual(evaluate(description,(0,1,1)),MASK)

    def test_nonboolean_selection_not_refined(self):
        (ones,_),known=bounds(counter_description(),edge_width=2)
        # The conjunction still forces the condition to one bit through NZ.
        self.assertEqual(ones,7);self.assertTrue(known.refinements)
        b=Builder(3);condition=b.add(b.nonzero(0),1)
        description=b.finish((b.select(condition,b.add(0,b.const(MASK)),0),))
        (_, _),known=bounds(description,edge_width=2)
        self.assertFalse(known.refinements)

    def test_complete_alphabet_and_overwide_output_mutation(self):
        good=period.output_types()
        self.assertEqual(good['raw_outputs_checked'],154)
        self.assertEqual(len(good['guarded_decrements']),10)
        description=f.self_description();outputs=list(description.outputs)
        outputs[f.COL['s0_lp_remaining']]=description.inputs+len(description.operations)
        bad=Program(description.inputs,description.operations+((LIT,8,0),),tuple(outputs))
        with self.assertRaisesRegex(AssertionError,'output exceeds fixed alphabet'):period.output_types(bad)

    def test_phase_and_query_coverage_mutations(self):
        self.assertTrue(period.interfaces(self.loaded)['passed'])
        for name in ('missing_phase','late_halt','wide_query','packet_after_forcing'):
            bad=deepcopy(self.loaded)
            if name=='missing_phase':bad['schedule']['phases'].pop(0)
            elif name=='late_halt':
                phase=bad['schedule']['phases'][0]
                phase['head_stopped']=phase['deadline']
                next(row for row in bad['timed']['phases'] if row['name']==phase['name'])['head_stopped']=phase['deadline']
            elif name=='wide_query':bad['queries']['maximum_possible_query_mask']=f.Q
            else:bad['capture']['no_SEND_during_or_after_forcing']=False
            with self.assertRaises((AssertionError,KeyError),msg=name):period.interfaces(bad)

    def test_open_lattice_ignores_wrapped_destinations(self):
        original=opened.batch.Checker.execute
        def scrambled(checker,*args,**kwargs):
            result=original(checker,*args,**kwargs)
            result['messages']=[(row[0],1000000,*row[2:]) for row in result['messages']]
            return result
        with patch.object(opened.batch.Checker,'execute',new=scrambled):
            result=opened.certify(self.loaded['schedule'])
        self.assertTrue(result['center_commit_equals_normalized_full_descriptor'])
        self.assertFalse(result['periodic_destination_used'])

    def test_open_lattice_reversed_direction_fails(self):
        with patch.object(opened,'destination',side_effect=lambda source,direction,hops:source+(hops if direction else -hops)):
            with self.assertRaisesRegex(AssertionError,'open history mismatch'):opened.certify(self.loaded['schedule'])

    def test_clock_transfer_rejects_missing_or_wrong_premises(self):
        good=transfer.load_inputs()
        self.assertTrue(transfer.validate_premises(good)['passed'])
        for mode in ('missing_interval','wrong_clock_mode','missing_phase','omitted_output','restricted_context'):
            bad=deepcopy(good)
            if mode=='missing_interval':bad['clock']['intervals'].pop()
            elif mode=='wrong_clock_mode':bad['clock']['intervals'][-1]['reference_age']=0
            elif mode=='missing_phase':bad['head']['cases'].pop()
            elif mode=='omitted_output':bad['clock']['intervals'][0]['non_Age_words']=152
            else:bad['clock']['intervals'][0]['arbitrary_other_raw_fields']=False
            with self.assertRaises(AssertionError,msg=mode):transfer.validate_premises(bad)

    def test_actual_new_ROM_endpoint_and_static_wire_required(self):
        last=len(p.base_rom())-1
        def broken_record(address):
            row=projected.record(address)
            if address==last:row['last']=0
            return row
        with self.assertRaisesRegex(AssertionError,'ROM endpoint defect'):transfer.geometry(broken_record)
        desc=f.self_description();outputs=list(desc.outputs);outputs[0]=desc.inputs+len(desc.operations)
        bad=Program(desc.inputs,desc.operations+((LIT,0,0),),tuple(outputs))
        with self.assertRaisesRegex(AssertionError,'static metadata changed'):structure.support(bad)

    def test_period_needs_full_new_clock_and_structure(self):
        for mode in ('old_period','unproved_structure','short_gap','missing_control','missing_entry'):
            bad=deepcopy(self.loaded)
            if mode=='old_period':bad['transfer']['legal_new_ages']=1<<32
            elif mode=='unproved_structure':bad['transfer']['canonical_structural_domain_preserved']=False
            elif mode=='short_gap':bad['transfer']['geometry']['minimum_gap_to_next_colony_core']=7
            elif mode=='missing_control':bad['rom']['equivalence']['complete_raw_outputs']=153
            else:bad['entry']['represented_raw_fields']=153
            with self.assertRaises(AssertionError,msg=mode):period.interfaces(bad)


if __name__=='__main__':unittest.main()
