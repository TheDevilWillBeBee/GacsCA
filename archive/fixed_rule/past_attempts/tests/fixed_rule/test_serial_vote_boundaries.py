from dataclasses import replace
import random
import unittest
from gacsca.fixed_rule import serial_vote_rule as f,serial_vote_projected as r,serial_vote_program as p,serial_vote_native as native

class SerialBoundaries(unittest.TestCase):
    def test_complete_state_at_clock_and_colony_boundaries(self):
        rng=random.Random(562);g=p.layout();lib=native.library()
        ages={0,1,f.U-1,*f.RESET_AGES,*f.ACTIVE_ENDS,*f.VOTE_AGES,f.CAPTURE_AGE-1,96*f.Q-1,98*f.Q-1}
        for age in sorted(ages):
            for address in (0,g.info[5],g.votes[5*f.FIELDS],g.memory_count,g.computation_cells-1,f.Q-3,f.Q-1):
                cells=[]
                for j in range(-5,6):
                    values={name:rng.getrandbits(width) for name,width in r.SCHEMA};values.update(address=(address+j)%f.Q,age=age)
                    cells.append(r.lift(r.Cell(**values)))
                cells=tuple(cells);want=f.local_step(cells)
                self.assertEqual(want,native.local_step(cells,lib),(age,address))
                self.assertEqual(want,f.decode_cell(f.self_description().evaluate(tuple(v for c in cells for v in f.encode_cell(c)))),(age,address))
        self.assertEqual(f.U,1<<32)

if __name__=='__main__':unittest.main()
