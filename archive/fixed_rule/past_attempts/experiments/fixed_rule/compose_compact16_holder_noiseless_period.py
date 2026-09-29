"""Finite interfaces for the compact16 complete descriptor-period induction.

The companion report supplies the induction. These are proof checks, not a
physical backend or permission to replace evolving states with decoded steps.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import sys
import time
from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_core as c
from gacsca.fixed_rule import compact16_holder_program as p, compact16_holder_projected as r
from experiments.fixed_rule import certify_compact16_holder_period_foundations as foundations
from experiments.fixed_rule import certify_compact16_holder_composition as composition

SOURCES = {name: 'compact16_holder_'+suffix+'_v1.json' for name, suffix in (
    ('structural', 'structural'), ('semantic', 'semantic'), ('paths', 'paths'),
    ('barriers', 'barriers'), ('rom', 'rom'), ('mail', 'mail'), ('entry', 'period_entry'))}


def load_inputs(root=Path('figs/fixed_rule')):
    docs = {name: json.loads((root/file).read_text()) for name, file in SOURCES.items()}
    digest = f.self_description().digest()
    rom = hashlib.sha256(p.base_rom().tobytes()).hexdigest()
    for name, doc in docs.items():
        assert doc['passed'], name
        for key in ('descriptor_sha256', 'physical_descriptor_sha256'):
            if key in doc:
                assert doc[key] == digest, name
        if 'ROM_sha256' in doc:
            assert doc['ROM_sha256'] == rom, name
        for source, expected in {**doc['source_sha256'], **doc.get('input_sha256', {})}.items():
            assert foundations.sha(source) == expected, source
    replay, _ = foundations.load_schedule()
    assert json.loads(json.dumps(replay)) == docs['paths']['packet_schedule']
    composition.verify_clock_receipt()
    return docs


def interfaces(docs):
    assert (f.Q, f.U, f.FIELDS, f.WIDTH, len(r.SCHEMA), r.WIDTH, f.NEIGHBORHOOD) == (
        16384, 1073741824, 154, 4090, 105, 2704, tuple(range(-7, 8)))
    structural, semantic = docs['structural'], docs['semantic']
    assert structural['canonical_structural_domain_preserved']
    assert len(structural['cases']) == 9
    assert {row['phase'] for row in structural['cases']} == {None, *range(8)}
    for row in structural['cases']:
        for name in ('raw_mail', 'head', 'image'):
            case = row[name]
            assert case['passed'] and case['phase'] == row['phase'] and case['all_clock_ages'] == f.U
        assert row['raw_mail']['independent_raw_mail_replicas']
        assert row['head']['routing_destinations_disjoint'] and row['head']['active_head_survives_iff_not_halted']
        assert row['image']['checked_primaries'] == [-1, 0, 1] and row['image']['canonical_geometry_preserved']
    assert structural['geometry']['core_cells'] == len(p.base_rom())
    assert structural['geometry']['minimum_gap_to_next_colony_core'] >= 8
    assert structural['spatial_support']['static_fields_preserved'] == 49
    assert structural['spatial_support']['maximum_head_controller_logical_radius'] <= 1
    assert structural['context']['complete_raw_words'] == 154
    assert structural['context']['all_clock_ages'] == f.U
    assert semantic['typing']['raw_outputs_checked'] == 154
    assert len(semantic['typing']['guarded_decrements']) == 10
    assert semantic['layout']['all_fixed_ROM_fields_typed']
    assert semantic['layout']['history_words'] == 3*len(p.layout().gathered_inputs)
    assert semantic['layout']['histories_survive_both_late_resets']
    assert semantic['queries']['certified_query_bits'] == 14
    assert semantic['queries']['maximum_possible_query_mask'] < f.Q
    assert semantic['queries']['selectors'] == list(range(7))
    assert docs['rom']['equivalence']['complete_raw_outputs'] == 154
    assert docs['rom']['dataflow']['all_controller_outputs_checked']
    assert docs['rom']['dataflow']['own_metadata_regenerated_before_each_evaluation']
    assert docs['entry']['represented_raw_fields'] == 154 and docs['entry']['represented_projected_fields'] == 105
    assert docs['entry']['nonzero_initial_scratch'] and docs['entry']['nonzero_retained_Signals']
    assert docs['entry']['full_ring']['validated_sites'] == f.Q
    flow, opened = semantic['timed'], semantic['open']
    assert flow['commit_matches_normalized_complete_rule'] and flow['next_reset_clears_all_nonInfo_Data']
    assert opened['source_integer_offsets'] == list(range(-7, 8)) and not opened['periodic_destination_used']
    assert opened['center_commit_equals_normalized_full_descriptor'] and opened['all_late_packets_zero_hop']
    assert opened['source_access_disjointness_checks'] == 45
    barriers = docs['barriers']
    assert barriers['quiet_barriers']['procedure_word_identities'] == 90
    assert barriers['quiet_barriers']['all_clock_ages'] == f.U
    assert barriers['quiet_barriers']['simultaneous_reset_vote_age'] == c.RESET_AGES[4] == c.VOTE_AGES[1]
    boundary, capture = barriers['signal_flag_boundaries'], barriers['signal_schedule_join']
    assert boundary['formulas']['all_clock_ages'] == f.U and boundary['formulas']['arbitrary_raw_fields']
    assert boundary['clearing']['total_clearing_ticks'] == f.Q
    assert docs['mail']['case_count'] == 63 and len(docs['mail']['packet_flight_cases']) == 8
    assert docs['mail']['mail_support']['controller_outputs_independent_of_all_old_mail'] == 45
    assert len(docs['paths']['additional_leaves']) == 84

    schedule = docs['paths']['packet_schedule']
    phases = {row['name']: row for row in schedule['phases']}
    order = ('gather_0', 'gather_1', 'gather_2', 'third_evaluation', 'precommit_halt', 'final_evaluation')
    assert set(phases) == set(order)
    origins = (0, c.RESET_AGES[1], c.RESET_AGES[2], c.VOTE_AGES[0], c.RESET_AGES[3], c.RESET_AGES[4])
    boundaries = (*origins[1:], f.U-1)
    timed = {row['name']: row for row in flow['phases']}
    rows = []
    for name, origin, next_barrier in zip(order, origins, boundaries):
        row = phases[name]
        assert row['origin'] == origin
        assert row['head_stopped'] == timed[name]['head_stopped'] and timed[name]['no_pending_packets']
        last = max(row['head_stopped'], row['packet_summary']['last_arrival'])
        assert last < row['deadline'] <= next_barrier
        assert not any(last <= tick < next_barrier for tick in (*c.RESET_AGES, *c.VOTE_AGES, f.U-1))
        assert row['packet_summary']['same_track_collisions_excluded']
        rows.append(dict(phase=name, entry_old_age=origin, quiet_from_age=last,
                         next_barrier_old_age=next_barrier, quiet_margin=next_barrier-last))
    assert capture['latest_packet_delivery_age'] < c.CAPTURE_AGE-1 < c.WF_START
    assert capture['no_SEND_during_or_after_forcing']
    assert c.WF_END+f.Q < c.RESET_AGES[4] < f.U-1
    assert all(not phases[name]['packets'] for name in ('precommit_halt', 'final_evaluation'))
    return dict(passed=True, phase_interfaces=rows, final_quiet_before_commit=True,
                flags_zero_before_final_evaluation=True, mail_absent_during_flag_forcing=True,
                complete_entry_restored_at_commit=True,
                ring_aliasing_basis='Independent integer-offset dataflow with substitution for '
                                    'any upper ring; modulo-Q packet collision exclusion; '
                                    'equal-PC emissions stay Q-spaced and hops count every crossing.',
                permitted_upper_ring_sizes='Every positive integer; infinite lattice by translation.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    start = time.perf_counter()
    result = interfaces(load_inputs())
    # Replay finite layout/width obligations against current sources as well.
    result['layout'] = foundations.layout()
    result['typing'] = foundations.output_types()
    sources = {Path(__file__).resolve()}
    for module in tuple(sys.modules.values()):
        filename = getattr(module, '__file__', None)
        if filename and '/fixed_rule/' in str(Path(filename).resolve()):
            sources.add(Path(filename).resolve())
    result.update(descriptor_sha256=f.self_description().digest(),
                  ROM_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),
                  input_sha256={str(Path('figs/fixed_rule')/file): foundations.sha(Path('figs/fixed_rule')/file)
                                for file in SOURCES.values()},
                  source_sha256={str(path.relative_to(Path.cwd())): foundations.sha(path) for path in sorted(sources)},
                  seconds=time.perf_counter()-start,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  theorem_interface='For the companion descriptor-semantics induction, '
                      'F^U(E(y)) is contained in E(G(y)), G=pi F iota, for compact16 and its own ROM. '
                      'Green interface checks alone are not the inductive proof.',
                  new_physical_period_executed=False,
                  limitation='Not a new U-tick physical trace or universal backend equivalence proof. '
                             'No general noise theorem, practical complete depth-two run or robust cap follows.')
    with args.output.open('x') as stream:
        stream.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(passed=True, phase_interfaces=result['phase_interfaces'],
                          seconds=result['seconds'], host_max_rss_kib=result['host_max_rss_kib'])), flush=True)


if __name__ == '__main__':
    main()
