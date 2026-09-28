"""CPU-only contract checks for the private retimed CUDA specialization."""
import hashlib
from pathlib import Path
import unittest
import numpy as np
from gacsca.fixed_rule import retimed_holder_core as c, retimed_holder_rule as f
from gacsca.fixed_rule import retimed_holder_program as p, retimed_holder_projected as r
from gacsca.fixed_rule import retimed_holder_quotient as q, retimed_holder_packed as packed
from gacsca.fixed_rule import retimed_holder_cpu_events as cpu, retimed_holder_native as native
from gacsca.fixed_rule import retimed_holder_prefix_description as prefix
from gacsca.fixed_rule import retimed_holder_resident_independent as gpu


def fixture(at, phase, *, age=1232000100, direction=0, **extra):
    data=np.zeros((1,f.Q),dtype=np.uint64)
    data[0,:p.layout().memory_count]=np.arange(p.layout().memory_count,dtype=np.uint64)*0x1234567
    fields=dict(head=1,phase=phase,pc=17,ra=73,rb=73,rd=73,value=0x123456789abcdef0,alu=c.NAND,direction=direction)
    fields.update(extra)
    return cpu.World(data,[[fields[n] for n in cpu.CONTROL]],[at],age=age)


def logical(raw):
    return c.Cell(**r.record(raw.address),**{n:getattr(raw,'s2_'+n) if 's2_'+n in f.COL else getattr(raw,'w2_'+n) if n in ('wf1','wf2') else getattr(raw,n) for n,_ in q.SCHEMA})


class CUDAContract(unittest.TestCase):
    def test_prefix_complete_dynamic_outputs_against_full_raw_rule(self):
        program=prefix.build()
        cases=[(73,phase,d,{}) for phase in (c.READ_A,c.READ_B,c.WRITE,c.READ_LOAD,c.WAIT_META) for d in (0,1)]
        cases += [(at,c.READ_B,d,{}) for at in (0,len(p.base_rom())-1) for d in (0,1)]
        cases += [(len(p.base_rom())-1,c.READ_META,0,dict(rb=k,rd=len(p.base_rom())-1,value=1)) for k in range(7)]
        cases += [(p.layout().memory_count+p.layout().entries[4],c.FETCH,0,dict(pc=p.layout().entries[4]))]
        for at,phase,d,extra in cases:
            w=fixture(at,phase,direction=d,**extra)
            for pos in (at-1,at,at+1):
                rows=[logical(w.cell(pos+j)) for j in range(-5,6)]
                actual=program.evaluate(tuple(getattr(x,n) for x in rows for n,_ in c.SCHEMA))
                wanted=logical(native.local_step(tuple(w.cell(pos+j) for j in f.NEIGHBORHOOD)))
                for name,_ in q.SCHEMA:
                    self.assertEqual(actual[c.COL[name]],getattr(wanted,name),(at,phase,d,pos,name))

    def test_retimed_clock_boundaries_with_zero_context(self):
        program=prefix.build()
        ages=sorted({*c.RESET_AGES,*c.VOTE_AGES,c.CAPTURE_AGE-1,c.WF_START-1,c.WF_END,f.U-1,*c.ACTIVE_ENDS})
        for age in ages:
            w=fixture(0,c.READ_A,age=age)
            # Zero signals/Wf is a valid suffix specialization; avoid capture
            # sites, whose arbitrary Data can create Signals for the next tick.
            for pos in (0,73,p.layout().info[0]):
                rows=[logical(w.cell(pos+j)) for j in range(-5,6)]
                actual=program.evaluate(tuple(getattr(x,n) for x in rows for n,_ in c.SCHEMA))
                wanted=logical(native.local_step(tuple(w.cell(pos+j) for j in f.NEIGHBORHOOD)))
                for name,_ in q.SCHEMA:
                    self.assertEqual(actual[c.COL[name]],getattr(wanted,name),(age,pos,name))

    def test_every_field_width_roundtrips(self):
        rng=np.random.default_rng(20260926)
        values=rng.integers(0,2**64,size=(101,len(q.SCHEMA)),dtype=np.uint64)
        for k,(_,width) in enumerate(q.SCHEMA):
            if width<64:values[:,k]&=np.uint64((1<<width)-1)
            values[0,k]=0;values[1,k]=(1<<width)-1
        np.testing.assert_array_equal(packed.unpack(packed.pack(values)),values)
        self.assertEqual(tuple(n for n,_ in q.SCHEMA if n in cpu.CONTROL),cpu.CONTROL)
        self.assertEqual(f.WIDTH,4090)

    def test_distance_function_is_exactly_the_cpu_certified_function(self):
        source=Path(gpu.__file__).with_suffix('.cu').read_text()
        start=source.index('__device__ uint64_t independent_distance(')
        body=source[start:source.index('\n}\n',start)+3]
        self.assertEqual(body,cpu.distance_source())
        self.assertEqual(hashlib.sha256(p.base_rom().tobytes()).hexdigest(),'4dc026b976c541001421dd214df9c9e33f6f851053d4ba5f53dbbec925ba5645')
        self.assertEqual(f.self_description().digest(),'6e2f29f61bf281ec5d346cd58e717cf7e5b0afea263d2c17a18a58de295d8d23')

if __name__=='__main__':unittest.main()
