"""Challenge the claimed macro-boundary relation with poisoned working memory."""
import unittest
import numpy as np
from gacsca.fixed_rule import regenerated as rule,regenerative as full,regenerative_block as block
from gacsca.fixed_rule.regenerated_native import library,run


class RegeneratedAdmissibilityTests(unittest.TestCase):
    def test_arbitrary_scratch_and_carried_operands_are_overwritten(self):
        g=block.layout()
        reference=(rule.Cell(address=0,head=1,phase=full.READ_LOAD,ra=0,rd=0x1234,value=1,bit=1),
                   rule.Cell(address=g.memory_count,head=1,phase=full.FETCH,pc=0),
                   rule.Cell(address=65535,bit=1,phase=7,pc=65535,lp_target=50000,
                             lp_bit=1,lp_valid=1,lp_cross=0,direction=1))
        state=rule.encode(reference)
        rng=np.random.default_rng(991)
        for base in range(0,len(state),g.colony_cells):
            info=state[base+g.info_start:base+g.info_start+full.WIDTH,rule.COL['bit']].copy()
            # Includes input mail banks, all gate wires, Hold, inverses and
            # unused instruction bit fields; only constants and Info are fixed.
            state[base:base+g.colony_cells,rule.COL['bit']]=rng.integers(0,2,g.colony_cells,dtype=np.uint32)
            state[base:base+2,rule.COL['bit']]=[0,1]
            state[base+g.info_start:base+g.info_start+full.WIDTH,rule.COL['bit']]=info
            for name in ('ra','rb','rd'):
                state[base,rule.COL[name]]=65535
            state[base,rule.COL['value']]=1
        self.assertEqual(rule.decode(state),reference)
        self.assertTrue(rule.check_boundary(state))
        # The host oracle receives only the old represented word and never
        # supplies any transition or encoded output to the physical execution.
        expected=rule.step_ring(reference)
        run(state,g.period_ticks,library())
        self.assertEqual(rule.decode(state),expected)
        self.assertTrue(rule.check_boundary(state))
        represented=tuple(full.decode_cell(state[base+g.info_start:base+g.info_start+full.WIDTH,
                                                rule.COL['bit']].tolist())
                          for base in range(0,len(state),g.colony_cells))
        self.assertEqual(represented,tuple(rule.lift(cell) for cell in expected))


if __name__=='__main__': unittest.main()
