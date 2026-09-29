"""Full raw own-ROM computation with dependency-directed physical retrieval.

Conditional symbolic instruction data flow, not an evolution backend. Every
encoded field remains present; only unused incoming operands lack histories.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import sys
import time
from types import FunctionType
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_core as c
from gacsca.fixed_rule import sparse_holder_program as p
from gacsca.fixed_rule import retimed_holder_program as reference
from experiments.fixed_rule.certify_lowmask_holder_rom import Checker as PreviousChecker, paths


def bind(function):
    namespace = dict(function.__globals__)
    namespace['p'] = p
    return FunctionType(function.__code__, namespace, function.__name__,
                        function.__defaults__, function.__closure__)


class Checker(PreviousChecker):
    __init__ = bind(PreviousChecker.__init__)

    def check(self):
        g = self.g
        assert len(g.info) == len(g.hold) == f.FIELDS
        histories_checked = 0
        for stage in range(3):
            self.reset(stage)
            runs = [self.execute(col, self.entries[stage]) for col in range(self.n)]
            deadline = (c.VOTE_AGES[0] if stage == 2 else c.ACTIVE_ENDS[stage]) - c.RESET_AGES[stage]
            last = self.deliver(runs, deadline=deadline, protected=True)
            assert max(x['ticks'] for x in runs) < deadline
            for col in range(self.n):
                # No input-metadata rewrite is needed: none is retrieved, and
                # each evaluation regenerates its own metadata from voted Addr.
                assert tuple(self.memory[col][at] for at in g.info) == self.inputs[col]
                for prior in range(stage+1):
                    for wire in g.gathered_inputs:
                        neighbor, field = divmod(wire, f.FIELDS)
                        got = self.memory[col][g.history(prior, neighbor-7, field)]
                        want = self.normal[(col+neighbor-7) % self.n][field]
                        assert got == want, ('gathered history mismatch', stage, col, wire)
                        histories_checked += 1
            self.phases.append(dict(kind='gather', stage=stage,
                                    head_stop=max(x['ticks'] for x in runs), last_delivery=last))
        self.vote()
        expected = tuple(tuple(self.t.normalize(self.t.expression(f.self_description(),
                         tuple(w for j in range(-7, 8) for w in self.normal[(col+j) % self.n]))))
                         for col in range(self.n))
        first = [self.execute(col, self.entries[4], third=True) for col in range(self.n)]
        last = self.deliver(first, deadline=c.CAPTURE_AGE-c.VOTE_AGES[0])
        assert max(x['ticks'] for x in first) < c.ACTIVE_ENDS[2]-c.VOTE_AGES[0]
        for col in range(self.n):
            for wire in g.required_inputs:
                neighbor, field = divmod(wire, f.FIELDS)
                assert self.memory[col][g.wires[wire]] == self.normal[(col+neighbor-7) % self.n][field]
            assert tuple(self.memory[col][at] for at in g.hold) == expected[col], 'first raw Hold mismatch'
            assert all(self.memory[col][at] == expected[col][f.COL['f2']] for at in range(1, 6))
            assert all(self.memory[col][at] == expected[col][f.COL['f1']] for at in range(f.Q-5, f.Q))
        self.phases.append(dict(kind='first_evaluation', head_stop=max(x['ticks'] for x in first), last_delivery=last))
        self.reset(3)
        idle = [self.execute(col, self.entries[3]) for col in range(self.n)]
        assert not any(x['messages'] or x['writes'] for x in idle)
        self.reset(4)
        self.vote()
        final = [self.execute(col, self.entries[4]) for col in range(self.n)]
        assert not any(x['messages'] for x in final)
        assert max(x['ticks'] for x in final) < c.ACTIVE_ENDS[4]-c.RESET_AGES[4]
        for col in range(self.n):
            assert tuple(self.memory[col][at] for at in g.hold) == expected[col], 'final raw Hold mismatch'
            for at in g.info:
                self.memory[col][at] = self.memory[col][at+1]
        self.reset(0)
        indices = {address: i for i, address in enumerate(g.info)}
        for col in range(self.n):
            for address, value in enumerate(self.memory[col]):
                want = expected[col][indices[address]] if address in indices else self.zero
                assert value == want, ('complete commit/reset mismatch', col, address)
        self.phases.append(dict(kind='final_evaluation', head_stop=max(x['ticks'] for x in final)))
        return dict(passed=True, colonies=self.n, complete_encoded_fields=f.FIELDS,
                    complete_raw_outputs_per_colony=f.FIELDS, histories_checked=histories_checked,
                    instructions_checked=self.instructions, metadata_queries=self.queries,
                    packets=self.packets, symbolic_terms=len(self.t.nodes), phases=self.phases,
                    arbitrary_typed_raw_inputs=True, all_controller_outputs_checked=True,
                    own_metadata_regenerated_before_each_evaluation=True,
                    scope='Full raw symbolic own-ROM computation, conditional on completed physical '
                          'instruction/packet abstractions; not a physical execution or noise theorem.')


def check():
    g = p.layout()
    flow = Checker().check()
    timing = g.timing_certificate()
    assert timing['fits']
    before, after = sum(paths(reference.layout())), sum(paths(g))
    return dict(passed=True, dataflow=flow, timing=timing,
                complete_Info_fields=len(g.info), complete_Hold_fields=len(g.hold),
                used_inputs=len(g.required_inputs), gathered_inputs=len(g.gathered_inputs),
                regenerated_metadata_inputs=len(g.regenerated_inputs),
                history_cells=3*len(g.gathered_inputs), vote_cells=len(g.votes),
                memory_cells=g.memory_count, stored_instructions=len(g.instructions),
                core_cells=g.computation_cells, Q=f.Q, U=f.U,
                controller_path_ticks=after, reference_controller_path_ticks=before,
                controller_ticks_saved=before-after,
                prospective_power_two_Q=1 << (g.computation_cells+4).bit_length(),
                prospective_power_two_U_from_paths=1 << (after-1).bit_length(),
                parameters_actually_changed=False,
                physical_descriptor_sha256=f.self_description().digest(),
                ROM_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),
                reference_ROM_sha256=hashlib.sha256(reference.base_rom().tobytes()).hexdigest())


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
    print(json.dumps({k: v for k, v in result.items() if k != 'source_sha256'}, indent=2))


if __name__ == '__main__':
    main()
