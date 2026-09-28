"""Distinguish capture priority, flag ancestry and schedule/capture mistakes."""
from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c
from gacsca.fixed_rule.wordcode import Program
from experiments.fixed_rule import certify_small_holder_signal_flag_boundaries as proof
from experiments.fixed_rule.join_small_holder_signal_schedule import check


class SignalFlagBoundaries(unittest.TestCase):
    def neighborhood(self,address=100):
        return tuple(f.Cell(address=(address+j)%f.Q,age=c.WF_END+1) for j in f.NEIGHBORHOOD)

    def test_single_nearest_neighbor_cannot_sustain_flag(self):
        for name,direction in (('f1',1),('f2',-1)):
            cells=list(self.neighborhood());cells[7]=replace(cells[7],**{name:1})
            cells[7+direction]=replace(cells[7+direction],**{name:1})
            self.assertEqual(getattr(f.local_step(tuple(cells)),name),0)
            cells[7+2*direction]=replace(cells[7+2*direction],**{name:1})
            self.assertEqual(getattr(f.local_step(tuple(cells)),name),1)

    def test_erasure_ancestry_cannot_cross_colony_boundary(self):
        for name,address,direction in (('f1',f.Q-1,1),('f2',0,-1)):
            cells=list(self.neighborhood(address));cells[7]=replace(cells[7],**{name:1})
            for j in range(1,6):cells[7+direction*j]=replace(cells[7+direction*j],**{name:1})
            self.assertEqual(getattr(f.local_step(tuple(cells)),name),0)

    def test_Signal_passthrough_mutation_rejected(self):
        desc=f.self_description();outputs=list(desc.outputs)
        outputs[f.COL['signal']]=7*f.FIELDS+f.COL['signal']
        mutant=Program(desc.inputs,desc.operations,tuple(outputs))
        with patch.object(f,'self_description',return_value=mutant):
            with self.assertRaisesRegex(AssertionError,'canonical boundary formula'):proof.certify_formulas()

    def test_capture_packet_mutations_rejected(self):
        root=Path(__file__).resolve().parents[2]/'figs/fixed_rule'
        schedule=json.loads((root/'small_holder_mail_schedule_v1.json').read_text())
        boundary=json.loads((root/'small_holder_signal_flag_boundaries_v1.json').read_text())
        for mutation in ('late','wrong_target','wrong_source'):
            damaged=deepcopy(schedule)
            phase=next(row for row in damaged['phases'] if row['name']=='third_evaluation')
            row=phase['packets'][0]
            if mutation=='late':row[-1]=c.CAPTURE_AGE
            elif mutation=='wrong_target':row[3]=6
            else:row[2]+=1
            with self.assertRaises(AssertionError):check(damaged,boundary)

    def test_boundary_age_wrap_and_clearing_budget(self):
        result=proof.off_window()
        self.assertEqual(result['intervals'][-1]['old_age_interval'],(f.U-1,f.U-1))
        self.assertEqual(result['both_flags_zero_by_age'],c.WF_END+f.Q)
        self.assertGreater(result['margin_before_final_evaluation'],0)


if __name__=='__main__':unittest.main()
