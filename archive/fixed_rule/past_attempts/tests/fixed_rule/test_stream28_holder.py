"""Fixed-rule closure and local stream events for the integrated candidate."""
from dataclasses import replace
import hashlib
import random
import unittest

from gacsca.fixed_rule import stream28_holder_core as c
from gacsca.fixed_rule import stream28_holder_core_clock_description as core_description
from gacsca.fixed_rule import stream28_holder_initial as initial
from gacsca.fixed_rule import stream28_holder_program as p
from gacsca.fixed_rule import stream28_holder_projected as r
from gacsca.fixed_rule import stream28_holder_rule as f
from experiments.fixed_rule.certify_stream28_holder_rom import Checker,equivalence


class Stream28Holder(unittest.TestCase):
    def test_fixed_depth_independent_rule_and_own_rom(self):
        g=p.layout();rom=p.base_rom();identity=r.identity()
        self.assertEqual((f.Q,f.U,f.FIELDS,f.WIDTH),(8192,1<<28,154,4090))
        self.assertEqual(f.NEIGHBORHOOD,tuple(range(-7,8)))
        self.assertEqual(f.self_description().inputs,15*f.FIELDS)
        self.assertEqual(g.packed.decode(),g.instructions)
        self.assertLess(g.computation_cells+5,f.Q)
        self.assertEqual(len(rom),g.computation_cells)
        self.assertEqual(sum(bool(int(rom[a,4])&c.STREAM_TAG_MARK)
                             for a in range(g.memory_count)),
                         3*len(g.gathered_inputs))
        digest=f.self_description().digest();rom_digest=hashlib.sha256(rom.tobytes()).hexdigest()
        for depth in (1,2,3):
            self.assertEqual(initial.physical_cells(1,depth),f.Q**depth)
            self.assertEqual(r.identity(),identity)
            self.assertEqual(f.self_description().digest(),digest)
            self.assertEqual(hashlib.sha256(p.base_rom().tobytes()).hexdigest(),rom_digest)

    def test_local_radius_and_all_raw_controller_outputs(self):
        rng=random.Random(2026092819)
        for _ in range(3):
            cells=tuple(f.Cell(**{name:rng.getrandbits(width) for name,width in f.SCHEMA})
                        for _ in f.NEIGHBORHOOD)
            words=tuple(word for cell in cells for word in f.encode_cell(cell))
            actual=f.encode_cell(f.local_step(cells))
            self.assertEqual(f.self_description().evaluate(words),actual)
            self.assertEqual(p.compiled_description().evaluate(words),actual)
            self.assertEqual(f.decode_cell(f.encode_cell(cells[7])),cells[7])
        for count in (14,16):
            with self.assertRaises(ValueError):f.local_step(tuple(f.Cell() for _ in range(count)))
        with self.assertRaises(ValueError):f.decode_cell((0,)*(f.FIELDS-1))

    def test_described_stream_logic_on_arbitrary_typed_neighborhoods(self):
        rng=random.Random(9304);description=core_description.build()
        for case in range(80):
            stage=case%3;age=c.RESET_AGES[stage]+rng.randrange(c.STREAM_FRAME)
            cells=[c.Cell(**{name:rng.getrandbits(width) for name,width in c.SCHEMA})
                   for _ in range(11)]
            cells=[replace(cell,age=age,address=(rng.randrange(c.Q)+j-5)%c.Q)
                   for j,cell in enumerate(cells)]
            field=rng.randrange(c.STREAM_FIELDS)
            cells[5]=replace(cells[5],kind=c.MEM,
                             b=((field+1)<<15)|rng.randrange(1<<15),
                             d=c.STREAM_TAG_MARK+(stage<<12)+rng.randrange(15*c.STREAM_FIELDS))
            words=tuple(v for cell in cells for v in c.encode_cell(cell))
            self.assertEqual(description.evaluate(words),
                             c.encode_cell(c._clock_step(tuple(cells))))

    def test_stream_emission_and_acceptance_are_full_rule_dynamics(self):
        g=p.layout();wire=next(w for w in g.gathered_inputs if w//f.FIELDS==6)
        neighbor,field=divmod(wire,f.FIELDS);offset=neighbor-7
        source=g.info[field];target=g.history(0,offset,field)
        launch=2+(source-wire)%f.Q;value=0x123456789abc
        def step(center,age,changing):
            def logical(position):
                address=position%f.Q
                fields=dict(r.record(address),address=address,age=age)
                fields.update(changing(address))
                return c.Cell(**fields)
            raw=tuple(r.lift(initial.coherent_cell(logical,center+j))
                      for j in f.NEIGHBORHOOD)
            actual=f.local_step(raw)
            words=tuple(word for cell in raw for word in f.encode_cell(cell))
            self.assertEqual(f.self_description().evaluate(words),f.encode_cell(actual))
            return actual
        emitted=step(source,launch-1,lambda address:{'data':value} if address==source else {})
        self.assertEqual((emitted.s2_rp_valid,emitted.s2_rp_target,
                          emitted.s2_rp_remaining,emitted.s2_rp_data),(1,wire,1,value))
        received=step(target,launch+10,
                      lambda address:dict(rp_target=wire,rp_data=value,rp_valid=1)
                      if address==(target-1)%f.Q else {})
        self.assertEqual((received.s2_data,received.s2_rp_valid),(value,0))

    def test_self_recompiled_stream_schedule_fits_fixed_period(self):
        g=p.layout();timing=g.timing_certificate()
        self.assertEqual(len(g.gathered_inputs),689)
        self.assertEqual([row['last_arrival'] for row in timing['gathers']],
                         [65097,65095,65094])
        self.assertTrue(timing['fits'])
        self.assertGreater(timing['evaluation_margin'],0)
        self.assertGreater(timing['stage3_stop_margin'],0)
        self.assertGreater(timing['capture_margin'],0)

    def test_own_rom_rejects_changed_instruction(self):
        g=p.layout();rom=p.base_rom().copy()
        row=next(row for row in g.packed.rows if row.kind==c.PACK3 and row.count==3)
        rom[g.physical_position(row.micro_pc),2]^=1<<28
        with self.assertRaises(AssertionError):Checker(rom).check()

    def test_all_original_and_compiled_raw_outputs_equal_symbolically(self):
        result=equivalence()
        self.assertEqual(result['structurally_equal_outputs'],f.FIELDS)
        self.assertEqual(result['structurally_unresolved_outputs'],[])


if __name__=='__main__':unittest.main()
