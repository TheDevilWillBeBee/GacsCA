"""One fixed tiled evaluator, complete image reconstruction, device-only decode."""
from contextlib import ExitStack
from dataclasses import replace
import random
import unittest
import os
from unittest.mock import patch
import numpy as np
from experiments.fixed_rule.audit_compact16_holder_terminal import step as diagnostic_step
from gacsca.fixed_rule import compact16_holder_endpoint_tiles as gpu,compact16_holder_terminal_dag as dag,compact16_holder_terminal_reference as replay,compact16_holder_terminal_image as image
from gacsca.fixed_rule import compact16_holder_rule as f,compact16_holder_projected as r,compact16_holder_program as p,compact16_holder_initial as initial
from gacsca.fixed_rule.wordcode import Program


def raw(parents):return np.array([f.encode_cell(r.lift(x)) for x in parents],dtype=np.uint64)
def parents(n):
    rng=random.Random(2026092703)
    return tuple(r.Cell(**{name:rng.getrandbits(width) for name,width in r.SCHEMA}) for _ in range(n))
def evaluate(window,source,start,count,**kwargs):
    with ExitStack() as guard:
        for module,name in ((Program,'evaluate'),(f,'local_step'),(r,'local_step'),(dag,'terminal'),(replay,'terminal'),(image.Image,'cell')):
            guard.enter_context(patch.object(module,name,side_effect=AssertionError('host simulated transition or reconstruction')))
        window.evaluate(source,start,count,**kwargs)


@unittest.skipUnless(os.environ.get('FIXED_RULE_GPU_TESTS')=='1','explicit GPU test opt-in')
class Tiles(unittest.TestCase):
    def test_raw_tiles_match_every_bank_word(self):
        top=parents(15);wanted=dag.terminal(top)
        with gpu.Source.raw(raw(top)) as source,gpu.Window(5) as window:
            for committed in (False,True):
                for start in (0,5,10):
                    evaluate(window,source,start,5,committed=committed);bank,signals=window.read()
                    np.testing.assert_array_equal(bank,wanted['committed_bank' if committed else 'precommit_bank'][start:start+5])
                    np.testing.assert_array_equal(signals,wanted['signals'][start:start+5])
                with self.assertRaises(ValueError):window.freeze_image()

    def test_initial_encoding_and_full_device_decode(self):
        top=parents(3)
        with gpu.Source.raw(raw(top)) as source,gpu.Window(32) as window,source.initial_image() as encoded:
            positions=(0,p.layout().info[0]-3,p.layout().info[-1]-3,f.Q-3,f.Q+p.layout().info[0],2*f.Q+p.layout().info[-1])
            for start in positions:
                actual=window.cells(encoded,start,7)
                wanted=np.array([f.encode_cell(r.lift(initial.cell_at(top,1,start+i))) for i in range(7)],dtype=np.uint64)
                np.testing.assert_array_equal(actual,wanted)
            with window.decode(encoded) as decoded:np.testing.assert_array_equal(window.cells(decoded,0,3),raw(top))

    def test_complete_image_cell_reconstruction(self):
        top=parents(3);wanted=dag.terminal(top);g=p.layout()
        with gpu.Source.raw(raw(top)) as source,gpu.Window(32) as window:
            for committed in (False,True):
                evaluate(window,source,0,3,committed=committed)
                with window.freeze_image() as computed:
                    expected=image.Image(wanted,precommit=not committed)
                    for start in (0,g.info[0]-3,g.info[-1]-3,g.memory_count-3,g.computation_cells-3,f.Q-5,2*f.Q+g.info[0]-3):
                        np.testing.assert_array_equal(window.cells(computed,start,11),[f.encode_cell(r.lift(expected.cell(start+i))) for i in range(11)])

    def test_nested_tiles_include_full_halos(self):
        top=parents(1);first=dag.terminal(top);expected=image.Image(first,precommit=True);g=p.layout()
        with gpu.Source.raw(raw(top)) as source,gpu.Window(32) as window:
            evaluate(window,source,0,1)
            with window.freeze_image() as upper:
                for start,count in ((0,8),(g.info[0]-3,8),(g.info[-1]-3,8),(g.memory_count-3,8),(f.Q-4,4)):
                    inputs=tuple(expected.cell(start-7+i) for i in range(count+14));wanted=dag.terminal(inputs)
                    evaluate(window,upper,start,count,committed=True);bank,signals=window.read()
                    np.testing.assert_array_equal(bank,wanted['committed_bank'][7:7+count])
                    np.testing.assert_array_equal(signals,wanted['signals'][7:7+count])

    def test_collected_info_is_actual_retained_output(self):
        top=parents(15);following=diagnostic_step(top)
        with gpu.Source.raw(raw(top)) as source,gpu.Source.empty_raw(15) as collected,gpu.Window(5) as window:
            with self.assertRaises(ValueError):window.evaluate(collected,0,5)
            for start in (0,5,10):
                evaluate(window,source,start,5,committed=True);window.collect_info(collected)
                if start<10:
                    self.assertFalse(collected.ready)
                    with self.assertRaises(ValueError):window.cells(collected,0,1)
            np.testing.assert_array_equal(window.cells(collected,0,15),raw(following))
            wanted=dag.terminal(following)
            evaluate(window,collected,5,5,committed=True)
            np.testing.assert_array_equal(window.read()[0],wanted['committed_bank'][5:10])

    def test_guarded_bad_source_and_ordering(self):
        cells=raw(parents(15));cells[0,f.COL['s2_head']]=2
        with gpu.Source.raw(cells) as source,gpu.Source.empty_raw(15) as collected,gpu.Window(5) as window:
            with self.assertRaises(ValueError):window.evaluate(source,0,5)
            with self.assertRaises(ValueError):window.read()
            with self.assertRaises(ValueError):window.collect_info(collected)
            with self.assertRaises(ValueError):window.decode(source)
            with self.assertRaises(ValueError):window.evaluate(source,14,2)
        with self.assertRaises(ValueError):gpu.Window(128,device_budget=1)


if __name__=='__main__':unittest.main()
