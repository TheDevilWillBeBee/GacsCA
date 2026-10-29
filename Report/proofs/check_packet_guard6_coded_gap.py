#!/usr/bin/env python3
"""J95: exact coded-wave gap in the guard6 abstract birth interface.

This checks the unchanged J87 component circuit plus the explicitly
proposed guard6 birth override. Valid birth requests are prescribed;
their GF/Age/command reachability in a full CA is NOT established.
The receipt refutes unconditional coded coverage from packet protection
alone. It does not refute actual SP14 noisy repair or iid reliability.
"""
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca import machine
from gacsca.netlist import Net, Compiled, w_mux, const_word, w_ult_const, w_add_const
import proposed_framed_service as service
import proposed_packet_guard6 as guard6

WIDTHS = dict(wf2=1, packet_valid=1, packet_tag=4, packet_count=11,
              flag_valid=1, flag_position=9, flag_count=11)
ROWS = [(f, b) for f, width in WIDTHS.items() for b in range(width)]
INDEX = {key: i for i, key in enumerate(ROWS)}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def circuit():
    n = Net()
    cells = {j: {f: n.input(('x', j, f, 0)) if width == 1 else
        [n.input(('x', j, f, b)) for b in range(width)] for f, width in WIDTHS.items()}
        for j in range(-6, 7)}
    result = service.build(n, {j: cells[j] for j in range(-5, 6)})
    guard = guard6.build(n, cells)
    birth = n.AND(n.input(('request',)), n.NOT(guard))
    result['packet_tag'] = w_mux(n, birth, [n.input(('request_tag', b)) for b in range(4)], result['packet_tag'])
    result['packet_count'] = w_mux(n, birth, [0]*11, result['packet_count'])
    result['packet_valid'] = n.OR(result['packet_valid'], birth)
    result['wf2'] = result['packet_valid']
    for field in WIDTHS:
        values = result[field] if isinstance(result[field], list) else [result[field]]
        for b, node in enumerate(values):
            n.set_output(('y', field, b), node)
    n.set_output(('birth',), birth)
    n.set_output(('guard',), guard)
    return n, Compiled(n)


def fields(raw):
    return {f: sum(raw[INDEX[f, b]].astype(np.int64) << b for b in range(width))
            for f, width in WIDTHS.items()}


def set_field(raw, field, sites, values):
    for b in range(WIDTHS[field]):
        raw[INDEX[field, b], sites] = ((np.asarray(values) >> b) & 1).astype(bool)


def profile_cofactors():
    """Universal final flag profile with a common free young counter.

    For c<1791 the combined carriers of the actual final profile are
    exactly these flags: same-count foreign packets agree with them;
    the old origin0 packet loses the per-cell comparison because d>c.
    That comparison is J87's exhaustive unsigned comparator theorem.
    """
    cases = 0
    for x in range(-6, 893):
        n = Net()
        count = [n.input(('young_count', b)) for b in range(11)]
        cells = {}
        for off in range(-5, 6):
            y = x + off
            origin = -5 if -5 <= y <= 442 else 444 if 444 <= y <= 891 else None
            cells[off] = dict(packet_valid=0, wf2=0, packet_tag=const_word(0, 4),
                packet_count=const_word(0, 11), flag_valid=int(origin is not None),
                flag_position=const_word(y - origin if origin is not None else 0, 9),
                flag_count=count)
        output = service.build(n, cells)
        origin = -5 if -5 <= x <= 442 else 444 if 444 <= x <= 891 else None
        gate = w_ult_const(n, count, 1791) if origin is not None else 0
        assert output['flag_valid'] == gate, x
        for field in ('flag_valid', 'flag_position', 'flag_count'):
            val = output[field] if isinstance(output[field], list) else [output[field]]
            for b, node in enumerate(val):
                n.set_output((field, b), node)
        words = np.arange(2048, dtype=np.int64)
        result = Compiled(n).evaluate({('young_count', b): ((words >> b) & 1).astype(bool)
                                      for b in range(11)}, bool)
        usable = (words < 1791) if origin is not None else np.zeros_like(words, dtype=bool)
        assert np.array_equal(result['flag_valid', 0], usable), x
        positions = sum(result['flag_position', b].astype(np.int64) << b for b in range(9))
        counters = sum(result['flag_count', b].astype(np.int64) << b for b in range(11))
        assert np.array_equal(positions, np.where(usable, x - origin if origin is not None else 0, 0)), x
        assert np.array_equal(counters, np.where(usable, words + 1, 0)), x
        cases += 1
    return cases


def main():
    started = time.monotonic()
    n, comp = circuit()
    cells, center, updates = 2048, 512, 400
    coordinates = np.arange(cells) - center
    raw = np.zeros((len(ROWS), cells), dtype=bool)
    holders = center + np.arange(1, 6)
    set_field(raw, 'wf2', holders, 1)
    set_field(raw, 'packet_valid', holders, 1)
    set_field(raw, 'packet_tag', holders, np.arange(5))
    initial = raw.copy()
    packed = [machine.CKernel.pack(raw)]
    rows, actual_births = [], []
    for t in range(updates):
        request = np.zeros(cells, dtype=bool)
        tag = np.zeros(cells, dtype=np.int64)
        if t == 150:
            raw[:, center + np.array([1, 2])] = False
            for origin in (-5, 444):
                sites = center + origin + np.arange(1, 6)
                request[sites] = True
                tag[sites] = np.arange(5)
        values = {('x', j, f, b): np.roll(raw[INDEX[f, b]], -j)
                  for j in range(-6, 7) for f, width in WIDTHS.items() for b in range(width)}
        values[('request',)] = request
        values.update({('request_tag', b): ((tag >> b) & 1).astype(bool) for b in range(4)})
        output = comp.evaluate(values, bool)
        if request.any():
            actual_births = coordinates[np.flatnonzero(output['birth',])].tolist()
            assert actual_births == [-4, -3, -2, 445, 446, 447, 448, 449]
        raw = np.stack([output['y', f, b] for f, b in ROWS])
        f = fields(raw)
        live = (f['wf2'] & f['packet_valid'] & (f['packet_tag'] < 5)).astype(bool)
        origins = coordinates - f['packet_tag'] - 1
        old_packet = np.flatnonzero(live & (origins == 0))
        assert coordinates[old_packet].tolist() == [1, 2, 3, 4, 5], t
        assert f['packet_count'][old_packet].tolist() == [t + 1]*5, t
        assert not np.any(raw[:, (coordinates < -5) | (coordinates > 891)]), t
        zero = np.flatnonzero(f['flag_valid'][center:center + 448] == 0).tolist()
        row = dict(state=t + 1, coded_force_zero_sites_in_true_colony=zero,
            proper_origin_zero_packet_count=t + 1,
            coded_origin_at_sites_440_through_448=[int(x - f['flag_position'][center + x]) if f['flag_valid'][center + x] else None
                                                  for x in range(440, 449)])
        rows.append(row)
        packed.append(machine.CKernel.pack(raw))
        if t + 1 in (1, 148, 150, 151, 152, 295, 300, 310, 400):
            print(json.dumps(dict(state=row['state'], zero_coded_sites=len(zero),
                packet_count=t + 1, origins_near_gap=row['coded_origin_at_sites_440_through_448'])), flush=True)
    assert not rows[149]['coded_force_zero_sites_in_true_colony']
    assert rows[-1]['coded_force_zero_sites_in_true_colony'] == [443]
    profile_cases = profile_cofactors()
    final_fields = fields(raw)
    for origin, interval in ((-5, range(-5, 443)), (444, range(444, 892))):
        sites = center + np.array(list(interval))
        assert np.all(final_fields['flag_valid'][sites] == 1)
        assert np.array_equal(final_fields['flag_position'][sites], coordinates[sites] - origin)
        assert np.all(final_fields['flag_count'][sites] == 249)
    # Exact final neighborhood at443: foreign roots-5 and444 are outside
    # the accepted adjusted-position range; original root0 has no quorum.
    final = fields(raw)
    final_neighborhood = [{field: int(value[center + x]) for field, value in final.items()} | {'site': x}
                          for x in range(438, 449)]
    out = ROOT / 'figs/robustness'
    asset = out / 'packet_guard6_coded_gap_trace.npz'
    np.savez_compressed(asset, initial=initial, computed_states_packed=np.stack(packed),
        input_fault_ticks=[150], input_fault_sites=[[1, 2]],
        birth_request_tick=150, birth_request_origins=[-5, 444])
    receipt = dict(proposed_rule_change=True, unincorporated_module=True,
        active_G17_modified=False, SP14_modified=False,
        checker_sha256=digest(Path(__file__)),
        guard_proposal_source_sha256=digest(Path(guard6.__file__)),
        framed_service_proposal_source_sha256=digest(Path(service.__file__)),
        helpers_sha256=digest(ROOT / 'gacsca/netlist.py'),
        framed_service_certificate_sha256=digest(out / 'framed_service_certificate.json'),
        composition_netlist_sha256=comp.digest, composition_gates=n.gate_count(),
        trace_asset_sha256=digest(asset), exact_finite_component_updates=updates,
        initial_proper_origin_zero_source_count=0, every_other_initial_component_bit_zero=True,
        independent_later_birth_requests=True, birth_request_tick=150,
        requested_origins=[-5, 444], actual_newborn_sites=actual_births,
        input_fault_groups=[dict(tick=150, sites=[1, 2])], global_E0_separation_satisfied=True,
        proper_original_packet_verified_every_state=True,
        coded_coverage_already_complete_state=150,
        final_state=updates, final_coded_force_zero_sites=[443],
        last_hundred_states_with_same_single_gap=all(row['coded_force_zero_sites_in_true_colony'] == [443] for row in rows[-100:]),
        original_source_count_at_final_state=updates, final_gap_neighborhood=final_neighborhood,
        symbolic_flag_profile_cofactors=profile_cases, common_young_counter_bits_free=11,
        all_counter_word_profile_checks=profile_cases*2048,
        final_profile_counters=dict(young=249, old=400, difference=151),
        no_further_requests_after_tick_150=True,
        profile_gap_persists_through_state_1791_with_original_packet_alive=True,
        coded_coverage_by_442_refuted_in_arbitrary_birth_interface=True,
        component_support_verified_every_state=[-5, 891], rows=rows,
        full_CA_GF_Age_Info_birth_reachability_established=False,
        ordinary_NF2_or_GF_repair_failure_established=False,
        independent_noise_unreliability_established=False, global_reliability_established=False,
        elapsed_seconds=time.monotonic() - started,
        scope='exact finite counterexample in standalone guard6/J87 component interface with prescribed valid birth requests; ROBUSTNESS J95; actual full-rule reachability unproved')
    (out / 'packet_guard6_coded_gap_certificate.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(final_gap=[443], packet_alive=updates, seconds=receipt['elapsed_seconds'])), flush=True)


if __name__ == '__main__':
    main()
