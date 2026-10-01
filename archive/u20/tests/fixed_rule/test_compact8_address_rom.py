"""Distinguish a physical own-address table from arbitrary static fixtures."""
import random
import unittest

from gacsca.fixed_rule import spatial_codec8
from gacsca.fixed_rule import spatial_epoch8 as spatial
from gacsca.fixed_rule import stream28_compact_vote8 as combined
from gacsca.fixed_rule import stream28_compact_vote_optimized8 as optimized
from gacsca.fixed_rule import stream28_holder_rule as holder
from experiments.fixed_rule.build_compact8_circuit import initial_cells,static_plan
from experiments.fixed_rule.compact8_address_rom import (
    project_spatial_static,source_data_at_address,spatial_input_wires,template)


class Compact8AddressROMTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        rng=random.Random(2026092811)
        cls.words=tuple(rng.getrandbits(width) for width in optimized.WIDTHS)

    def test_spatial_static_words_are_own_immutable_rom_by_address(self):
        self.assertEqual(len(spatial_input_wires()),341)
        immutable=template()
        static=set(spatial_input_wires())
        for address in (0,1,2826,2827,3216,3217,8191):
            words=project_spatial_static(address,self.words)
            for wire in static:
                neighbor,field=divmod(wire,combined.FIELDS)
                site=(address+neighbor-7)%spatial.Q
                expected=spatial_codec8.encode_cell(immutable[site])[
                    field-holder.FIELDS]
                self.assertEqual(words[wire],expected)
            self.assertTrue(all(words[wire]==self.words[wire]
                                for wire in range(len(words)) if wire not in static))
            rows=initial_cells(words)
            for site,wire in static_plan()['raw_sources'].items():
                if wire in static:self.assertEqual(rows[site].source_value,words[wire])
        self.assertNotEqual(project_spatial_static(0,self.words),
                            project_spatial_static(1,self.words))

    def test_holder_data_capture_reloads_projected_source(self):
        address=3217
        words=project_spatial_static(address,self.words)
        static=set(spatial_input_wires())
        site,wire=next((s,w) for s,w in static_plan()['raw_sources'].items()
                       if w in static)
        value=source_data_at_address(address,self.words)[site]
        self.assertEqual(value,words[wire])
        rows=initial_cells(words)
        self.assertEqual(rows[site].kind,spatial.SOURCE)
        neighbors=[]
        for offset in combined.NEIGHBORHOOD:
            h=holder.Cell(address=(site+offset)%spatial.Q,
                          age=combined.CAPTURE_AGE,
                          **{f's{k}_data':value for k in range(5)})
            neighbors.append(combined.Cell(h,rows[(site+offset)%spatial.Q]))
        next_cell=combined.local_step(tuple(neighbors))
        self.assertEqual(next_cell.evaluator.source_value,value)
        self.assertEqual(next_cell.evaluator.address,site)
        self.assertEqual(next_cell.evaluator.age,0)

    def test_neighborhood_and_address_validation(self):
        with self.assertRaises(ValueError):
            project_spatial_static(-1,self.words)
        with self.assertRaises(ValueError):
            project_spatial_static(8192,self.words)
        with self.assertRaises(ValueError):
            project_spatial_static(0,self.words[:-1])

    def test_changed_dual_rule_uses_its_own_addressed_spatial_rom(self):
        own=template(True)
        wires=spatial_input_wires()
        for address in (0,3218,8191):
            words=project_spatial_static(address,self.words,True)
            for wire in wires:
                neighbor,field=divmod(wire,combined.FIELDS)
                site=(address+neighbor-7)%spatial.Q
                self.assertEqual(words[wire],
                    spatial_codec8.encode_cell(own[site])[field-holder.FIELDS])
            encoded=initial_cells(words,True)
            for site,wire in static_plan(True)['raw_sources'].items():
                if wire in wires:self.assertEqual(encoded[site].source_value,
                                                   words[wire])


if __name__=='__main__':unittest.main()
