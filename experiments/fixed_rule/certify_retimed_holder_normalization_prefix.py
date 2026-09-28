"""Physical-refinement premises for the fixed metadata normalization prefix.

Diagnostic proof composition only. No represented or physical transition is
executed here. Initial encoded metadata may differ; all other physical words
of the paired post-reset entries agree.
"""
import argparse
from dataclasses import replace
import json
from pathlib import Path
import resource
import time

from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_core as c
from gacsca.fixed_rule import retimed_holder_program as p
from experiments.fixed_rule import compose_retimed_holder_noiseless_period as composition
from experiments.fixed_rule.certify_retimed_holder_late_confinement import cut, tail_edges
from experiments.fixed_rule.certify_retimed_holder_late_procedure_image import certify as image
from experiments.fixed_rule.audit_retimed_holder_prefix_embedding import sha


def analyze(*, layout=None):
    g = p.layout() if layout is None else layout
    start, end = g.stage_ranges[0]
    assert start == 0
    meta = [i for i in range(start, end) if g.instructions[i].kind == c.META]
    assert len(meta) == len(f.STATIC) == 49
    stop = max(meta)+1
    assert stop == 128
    first_send = next(i for i in range(start, end) if g.instructions[i].kind == c.SEND)
    assert first_send > stop and g.instructions[stop].kind == c.LIT
    normalization_age = g.schedule(0, stop)[0]+2
    first_send_birth = g.schedule(0, first_send+1)[0]
    assert normalization_age < first_send_birth
    targets = set(g.info[:len(f.STATIC)])
    mutable = set(g.info[len(f.STATIC):])
    different = set(targets)
    overwritten = set()
    reads = 0
    query_equal = False
    for pc, op in enumerate(g.instructions[:stop]):
        assert op.kind != c.SEND, 'communication precedes normalization'
        if op.kind in c.ALU_KINDS:
            sources, destination = (op.a, op.b), op.d
        elif op.kind == c.LIT:
            sources, destination = (), op.d
        elif op.kind == c.LOAD:
            sources, destination = (op.a,), None
        elif op.kind == c.META:
            sources, destination = (), op.a
            assert query_equal, 'META query may differ between the two trajectories'
            assert destination in targets
            overwritten.add(destination)
        else:
            raise AssertionError(('unreviewed prefix instruction', pc, op))
        assert not (set(sources) & different), ('reads unnormalized metadata', pc, sources)
        reads += len(sources)
        if op.kind == c.LOAD:
            query_equal = True
        if destination is not None:
            assert destination not in mutable, ('normalizer changes mutable Info', pc, destination)
            different.discard(destination)
    assert overwritten == targets and not different, 'metadata not completely overwritten'
    return dict(passed=True, prefix_instruction_count=stop, metadata_words_overwritten=len(overwritten),
                equal_operand_reads_checked=reads, first_SEND_pc=first_send,
                first_SEND_birth_age=first_send_birth, normalization_age=normalization_age,
                first_SEND_margin=first_send_birth-normalization_age,
                all_mutable_Info_preserved=True, no_initial_metadata_read_before_overwrite=True,
                paired_controller_operands_and_META_queries_equal=True,
                initial_encoded_metadata_Data_may_differ_in_all_49_words=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    out = Path(parser.parse_args().output)
    if out.exists():
        raise FileExistsError(out)
    start = time.perf_counter()
    loaded = composition.load_inputs()
    composition.interfaces(loaded)
    result = analyze()
    gather = next(row for row in loaded['schedule']['phases'] if row['name'] == 'gather_0')
    assert min(row[1] for row in gather['packets']) == result['first_SEND_birth_age']
    intervals = ((0, 0), (1, result['normalization_age']-1))
    result.update(early_cut_cases=[cut(interval) for interval in intervals],
                  early_image_cases=[image(interval) for interval in intervals],
                  early_tail_edge_cases=[tail_edges(interval) for interval in intervals],
                  descriptor_sha256=f.self_description().digest(),
                  source_sha256={str(path): sha(path) for path in (
                      Path(__file__), Path(f.__file__), Path(c.__file__), Path(p.__file__),
                      Path(composition.__file__),
                      Path('experiments/fixed_rule/certify_retimed_holder_late_confinement.py'),
                      Path('experiments/fixed_rule/certify_retimed_holder_late_procedure_image.py'))},
                  input_sha256={str(Path('figs/fixed_rule')/name): sha(Path('figs/fixed_rule')/name)
                                for name in composition.SOURCES.values()},
                  seconds=time.perf_counter()-start,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  scope='Given canonical paired post-reset states, identical nonmetadata '
                        'Data/controllers/Signals, typed represented Address, fixed ROM, '
                        'zero flags/Wf/mail and the existing instruction refinements, '
                        'the 49 encoded metadata differences are physically overwritten '
                        'before any differing value is read or any packet is emitted. '
                        'All controller operands/queries remain paired. Early separation '
                        'and complete nonmail images hold for reset and the whole prefix. '
                        'No fresh fault during normalization is covered.')
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
