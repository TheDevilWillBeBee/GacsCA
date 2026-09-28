"""Fresh structural and timed/open semantic foundations for compact16.

All functions are proof diagnostics, never physical evolution backends.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import sys
import time
from types import FunctionType
from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_core as c
from gacsca.fixed_rule import compact16_holder_program as p, compact16_holder_projected as r
from gacsca.fixed_rule import compact16_holder_period_relation as relation
from experiments.fixed_rule import certify_compact16_holder_raw_mail_factorization as raw_mail
from experiments.fixed_rule import certify_compact16_holder_head_invariant as head
from experiments.fixed_rule import certify_compact16_holder_procedure_image as image
from experiments.fixed_rule import join_compact16_holder_structural_invariant as structure
from experiments.fixed_rule import certify_compact16_holder_procedure_context as context
from experiments.fixed_rule import certify_compact16_holder_timed_dataflow as timed
from experiments.fixed_rule import certify_compact16_holder_open_dataflow as opened
from experiments.fixed_rule import certify_compact16_holder_rom as batch
from experiments.fixed_rule import certify_compact16_holder_composition as composition
from experiments.fixed_rule.certify_small_holder_rom_dataflow import Terms
from experiments.fixed_rule.small_holder_guarded_bounds import GuardedBounds


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load_schedule():
    path = Path('figs/fixed_rule/compact16_holder_paths_v1.json')
    doc = json.loads(path.read_text())
    assert doc['passed'] and doc['descriptor_sha256'] == f.self_description().digest()
    assert doc['ROM_sha256'] == hashlib.sha256(p.base_rom().tobytes()).hexdigest()
    for source, digest in {**doc['source_sha256'], **doc['input_sha256']}.items():
        assert sha(source) == digest, source
    loaded = {'ordinary': {'rows': doc['ordinary_rows']},
              'meta': {'paths': doc['metadata_paths']},
              'dispatch': {'rows': doc['dispatch_rows']}}
    replay = composition.schedule(loaded)
    assert json.loads(json.dumps(replay)) == doc['packet_schedule']
    return replay, {str(path): sha(path)}


def structural():
    cases = []
    for phase in (None, *range(8)):
        cases.append(dict(phase=phase, raw_mail=raw_mail.certify_case(phase),
                          head=head.certify_case(phase), image=image.certify_case(phase)))
        print(json.dumps(dict(structural_phase=phase, passed=True)), flush=True)
    geometry, support = head.geometry(), structure.support()
    assert geometry['minimum_gap_to_next_colony_core'] >= 8
    assert support['maximum_head_controller_logical_radius'] <= 1
    return dict(passed=True, cases=cases, geometry=geometry, spatial_support=support,
                context=context.certify(), masked_replica_majority=image.mask_majority(),
                canonical_structural_domain_preserved=True,
                scope='Fresh compact-descriptor identities over every normalized Age. '
                      'Canonical geometry, actual coherent static/Data/controllers, '
                      'zero inactive controllers and at most one head per core. '
                      'Raw mail, flags, Signals and Wf are unrestricted. Unique endpoints '
                      'and core separation compose local routing/image identities into '
                      'preservation of this domain by each synchronous physical step.')


class QueryTerms(batch.Terms):
    def __init__(self, rom):
        super().__init__(rom)
        self.query_calls = 0
        self.query_mask = 0
        self.query_selectors = set()

    def lookup(self, address, selector):
        mask = (1 << self.width(address))-1
        assert mask < f.Q, ('META query exceeds certified Address domain', mask)
        self.query_calls += 1
        self.query_mask = max(self.query_mask, mask)
        self.query_selectors.add(selector)
        return super().lookup(address, selector)


def query_checker():
    # Private constructor binding, without patching any shared module globals.
    constructor = batch.Checker.__init__
    namespace = dict(constructor.__globals__, Terms=QueryTerms)
    init = FunctionType(constructor.__code__, namespace, constructor.__name__,
                        constructor.__defaults__, constructor.__closure__)
    checker = batch.Checker.__new__(batch.Checker)
    init(checker)
    return checker


def output_types(description=None):
    desc = f.self_description() if description is None else description
    t = Terms(p.base_rom())
    inputs = tuple(t.intern(('input', col, name, width))
                   for col in range(15) for name, width in f.SCHEMA)
    outputs = t.expression(desc, inputs)
    assert len(outputs) == f.FIELDS
    bounds, masks = GuardedBounds(t), {}
    for (name, width), term in zip(f.SCHEMA, outputs):
        ones, _ = bounds.at(term)
        assert ones < 1 << width, ('output exceeds fixed alphabet', name, width, ones)
        masks[name] = ones
    return dict(passed=True, raw_outputs_checked=len(masks), raw_width=f.WIDTH,
                projected_width=r.WIDTH, all_output_possible_one_masks=masks,
                guarded_decrements=bounds.refinements)


def layout():
    result = relation.layout_obligations()
    g = p.layout()
    info, hold = set(g.info), set(g.hold)
    assert not info & hold and len(info) == len(hold) == f.FIELDS
    histories = {g.history(stage, wire//f.FIELDS-7, wire%f.FIELDS)
                 for stage in range(3) for wire in g.gathered_inputs}
    assert len(histories) == 3*len(g.gathered_inputs)
    for at in histories:
        row = r.record(at)
        assert row['kind'] == c.MEM and not row['first']
        assert not row['a'] & ((1 << 3) | (1 << 4)), ('late reset erases a vote operand', at)
    for at in g.votes:
        assert {at-1, at+1, at+2} <= histories and 0 <= at-1 < at+2 < f.Q
    widths = dict(c.SCHEMA)
    for address in range(f.Q):
        row = r.record(address)
        assert all(0 <= value < 1 << widths[name] for name, value in row.items())
        if row['kind'] == c.MEM and not row['first'] and row['a'] & c.VOTE:
            assert address in g.votes
        if row['kind'] == c.MEM and not row['first'] and row['a'] & c.INFO:
            assert address in info
    assert r.record(0)['kind'] == c.MEM and r.record(0)['first'] == 1
    return dict(result, histories_survive_both_late_resets=True, history_words=len(histories),
                gathered_inputs=len(g.gathered_inputs), regenerated_inputs=len(g.regenerated_inputs),
                all_vote_operands_inside_colony=True, Info_Hold_disjoint=True,
                vote_and_Info_marks_have_exact_layout=True, all_fixed_ROM_fields_typed=True)


def semantic():
    schedule, inputs = load_schedule()
    ref = query_checker()
    flow = timed.prove(schedule, checker=ref)
    assert ref.t.query_selectors == set(range(7))
    queries = dict(passed=True, checked_lookup_calls=ref.t.query_calls,
                   maximum_possible_query_mask=ref.t.query_mask,
                   certified_query_bits=(f.Q-1).bit_length(),
                   selectors=sorted(ref.t.query_selectors),
                   scope='Every symbolic normalization and executed META lookup in the timed proof; '
                         'query values are observed, never truncated by the checker.')
    print(json.dumps(dict(timed_dataflow=True, query_bounds=True)), flush=True)
    open_result = opened.certify(schedule)
    return dict(passed=True, timed=flow, open=open_result, queries=queries,
                layout=layout(), typing=output_types(), input_sha256=inputs,
                scope='Timed physical-event read/write ordering agrees with complete symbolic '
                      'own-ROM computation, sparse histories and both evaluations. Open integer '
                      'source labels avoid assuming a 15-colony ring. Physical refinements and '
                      'the period induction remain required; this is not an execution backend.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--part', required=True, choices=('structural', 'semantic'))
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    start = time.perf_counter()
    result = structural() if args.part == 'structural' else semantic()
    sources = {Path(__file__).resolve()}
    for module in tuple(sys.modules.values()):
        filename = getattr(module, '__file__', None)
        if filename and '/fixed_rule/' in str(Path(filename).resolve()):
            sources.add(Path(filename).resolve())
    result.update(descriptor_sha256=f.self_description().digest(),
                  ROM_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),
                  source_sha256={str(path.relative_to(Path.cwd())): sha(path) for path in sorted(sources)},
                  seconds=time.perf_counter()-start,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    with args.output.open('x') as stream:
        stream.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(passed=True, part=args.part, seconds=result['seconds'],
                          host_max_rss_kib=result['host_max_rss_kib'])), flush=True)


if __name__ == '__main__':
    main()
