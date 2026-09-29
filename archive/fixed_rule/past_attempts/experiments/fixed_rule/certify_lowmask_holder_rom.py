"""Complete conditional self-ROM data flow and measured physical schedule cost."""
import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import resource
import sys
import time
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_core as c
from gacsca.fixed_rule import retimed_holder_program as old
from gacsca.fixed_rule import lowmask_holder_program as p, lowmask_holder_projected as r
from gacsca.fixed_rule.wordcode import NAND, LIT, MASK
from gacsca.fixed_rule.word_program import Instruction
from experiments.fixed_rule.certify_retimed_holder_rom import Checker as BaseChecker, Terms


class Checker(BaseChecker):
    def __init__(self, rom=None):
        self.g = p.layout()
        self.rom = p.base_rom() if rom is None else np.asarray(rom, dtype=np.uint64)
        assert self.rom.shape == p.base_rom().shape
        self.n, self.t = 15, Terms(self.rom)
        self.zero = self.t.const(0)
        self.memory = [[self.zero] * f.Q for _ in range(self.n)]
        self.inputs = tuple(tuple(self.t.variable(f'raw_{col}_{name}', width)
                                  for name, width in f.SCHEMA) for col in range(self.n))
        self.normal = tuple(tuple(self.t.normalize(row)) for row in self.inputs)
        for col in range(self.n):
            for address, value in zip(self.g.info, self.inputs[col]):
                self.memory[col][address] = value
        header = self.rom[0]
        self.entries = tuple(int((int(header[2 if stage < 2 else 3]) >>
                                  (32 * (stage % 2))) & 0xFFFFFFFF)
                             if stage < 4 else int(header[4]) for stage in range(5))
        assert self.entries == self.g.entries
        self.instructions = self.queries = self.packets = 0
        self.phases = []


def paths(layout):
    return [layout.schedule(*phase)[0] for phase in layout.stage_ranges] + [
        layout.schedule(*layout.delivery_range)[0]]


def rejected_high_address_cost():
    """Reproduce the failed placement, restricted to initialized phases."""
    g = old.layout()
    start, address = g.description_instruction, g.memory_count
    ops = [replace(op, b=address) if pc >= start and op.kind == NAND and op.a == op.b
           else op for pc, op in enumerate(g.instructions)]
    ops.insert(start, Instruction(LIT, MASK, 0, address))
    shift = lambda x: x + int(x > start)
    candidate = replace(g, memory_count=g.memory_count + 1, instructions=tuple(ops),
                        stage_ranges=tuple((shift(a), shift(b)) for a, b in g.stage_ranges),
                        delivery_range=tuple(shift(x) for x in g.delivery_range))
    return sum(paths(candidate))


def check():
    g, reference = p.layout(), old.layout()
    flow = Checker().check()
    timing = g.timing_certificate()
    assert timing['fits']
    changed = []
    start = reference.description_instruction
    for pc, instruction in enumerate(reference.instructions):
        actual = g.instructions[pc + int(pc >= start)]
        if actual != instruction:
            assert pc >= start and instruction.kind == NAND and instruction.a == instruction.b
            assert actual == replace(instruction, a=p.MASK_ADDRESS, b=instruction.a)
            changed.append(pc)
    assert len(changed) > 0
    assert g.instructions[start] == Instruction(LIT, MASK, 0, p.MASK_ADDRESS)
    for address in range(f.Q):
        assert all(0 <= value < 1 << dict(c.SCHEMA)[name]
                   for name, value in r.record(address).items())
    before, after = sum(paths(reference)), sum(paths(g))
    assert after < before
    return dict(passed=True, dataflow=flow, timing=timing,
                controller_path_ticks_before=before, controller_path_ticks_after=after,
                controller_ticks_saved=before-after, saved_fraction=(before-after)/before,
                transformed_NAND_instructions=len(changed), transformed_PCs=changed,
                rejected_high_address_controller_ticks=rejected_high_address_cost(),
                original_core_cells=reference.computation_cells, core_cells=g.computation_cells,
                minimum_power_two_U_from_controller_paths=1 << (after-1).bit_length(),
                minimum_power_two_Q_for_core_tail=1 << (g.computation_cells+4).bit_length(),
                physical_descriptor_sha256=f.self_description().digest(),
                ROM_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),
                reference_ROM_sha256=hashlib.sha256(old.base_rom().tobytes()).hexdigest(),
                physical_width=r.WIDTH, raw_width=f.WIDTH, Q=f.Q, U=f.U,
                scope='Complete conditional symbolic own-ROM data flow and controller travel '
                      'cost for a fixed candidate. New local path, packet timing and full-period '
                      'physical execution certificates are still required; no GPU speedup claimed.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    start = time.perf_counter()
    result = check()
    result.update(seconds=time.perf_counter()-start,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    sources = {Path(__file__).resolve()}
    for module in tuple(sys.modules.values()):
        filename = getattr(module, '__file__', None)
        if filename and '/fixed_rule/' in str(Path(filename).resolve()):
            sources.add(Path(filename).resolve())
    result['source_sha256'] = {str(path.relative_to(Path.cwd())):
                              hashlib.sha256(path.read_bytes()).hexdigest()
                              for path in sorted(sources)}
    with args.output.open('x') as stream:
        stream.write(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items()
                      if k not in ('source_sha256', 'transformed_PCs')}, indent=2))


if __name__ == '__main__':
    main()
