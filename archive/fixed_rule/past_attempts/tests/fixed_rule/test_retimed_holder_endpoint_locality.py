"""Dependency-cone and complete raw-width contract for the endpoint backend."""
from dataclasses import replace
import unittest
import numpy as np
from gacsca.fixed_rule import retimed_holder_endpoint_gpu as gpu,retimed_holder_rule as f,retimed_holder_program as p,retimed_holder_projected as r


def bank_for(parents):
    bank=np.zeros((len(parents),p.layout().memory_count+5),dtype=np.uint64)
    bank[:,list(p.layout().info)]=[f.encode_cell(r.lift(x)) for x in parents]
    return bank


class Locality(unittest.TestCase):
    def test_macro_dependency_cone_and_wrapped_neighbor(self):
        parents=(r.Cell(),)*31;results=[]
        for at in (None,15,30):
            current=list(parents)
            if at is not None:current[at]=replace(current[at],s2_rb=123456)
            with gpu.World(bank_for(current),np.zeros((31,2),dtype=np.uint64)) as world:
                world.period();results.append(world.read()[0])
        np.testing.assert_array_equal(results[0][0],results[1][0])
        self.assertFalse(np.array_equal(results[0][15],results[1][15]))
        self.assertFalse(np.array_equal(results[0][0],results[2][0]))

    def test_every_narrow_raw_field_is_checked_atomically(self):
        for k,(name,width) in enumerate(f.SCHEMA):
            if width==64:continue
            bank=bank_for((r.Cell(),));bank[0,p.layout().info[k]]=1<<width
            with gpu.World(bank,np.zeros((1,2),dtype=np.uint64)) as world:
                with self.assertRaisesRegex(ValueError,'rejected atomically',msg=name):world.precommit()
                np.testing.assert_array_equal(world.read()[0],bank,err_msg=name)
                self.assertEqual(world.time,0)


if __name__=='__main__':unittest.main()
