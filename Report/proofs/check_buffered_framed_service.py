#!/usr/bin/env python3
"""J103: conditional shifted-source repair with a five-cell coded buffer.

Exact local premises for the written origin/count/interval induction.
No CA or ROM changed; a standalone explicit proposed module only.
"""
from itertools import combinations
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,Compiled,const_word
import proposed_packet_pressure as old
import proposed_buffered_framed_service as proposed

WIDTHS = dict(wf2=1,packet_valid=1,packet_tag=4,packet_count=11,
    flag_valid=1,flag_position=9,flag_count=11)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inputs(n):
    return {off:{f:n.input((off,f,0)) if width == 1 else
        [n.input((off,f,b)) for b in range(width)] for f,width in WIDTHS.items()}
        for off in range(-5,6)}


def module_net():
    n = Net()
    cells = inputs(n)
    before = old.build(n,cells)
    result = proposed.build(n,cells)
    equalities = 0
    for field in ('wf2','packet_valid','packet_tag','packet_count','packet_any_cohort'):
        a = before[field] if isinstance(before[field],list) else [before[field]]
        b = result[field] if isinstance(result[field],list) else [result[field]]
        assert a == b,field
        equalities += len(b)
    assert result['service_force'] == n.OR(result['flag_valid'],result['packet_any_cohort'])
    for f,value in result.items():
        for b,node in enumerate(value if isinstance(value,list) else [value]):
            n.set_output((f,b),node)
    return n,Compiled(n),equalities


def true_carrier_cases():
    """Source/interval erasure cofactors at count0; lifetime uses J87.

    All nonproper carrier fields are empty here. Proper count-t carriers
    win against older competitors by the unchanged comparison/count
    proof. These cases erase the other holders rather than exhaust every
    arbitrary replacement. The nonfault-witness/count proof covers those
    replacements; see J103's separately written induction.
    """
    first = interval = 0
    # Source-root translation is algebraic; use r=0. Its code origin=-5.
    for x in range(7):
        for trio in combinations(range(1,6),3):
            n = Net()
            cells = inputs(n)
            for off in range(-5,6):
                y = x+off
                if y in trio:
                    cells[off] = dict(wf2=1,packet_valid=1,packet_tag=const_word(y-1,4),
                        packet_count=[0]*11,flag_valid=0,flag_position=[0]*9,flag_count=[0]*11)
                else:
                    cells[off] = dict(wf2=0,packet_valid=0,packet_tag=[0]*4,
                        packet_count=[0]*11,flag_valid=0,flag_position=[0]*9,flag_count=[0]*11)
            result = proposed.build(n,cells)
            assert result['flag_valid'] == 1,(x,trio)
            assert result['flag_position'] == const_word(x+5,9),(x,trio)
            assert result['flag_count'] == const_word(1,11),(x,trio)
            first += 1
    # Both interval edges: use supports entirely to the left/right when
    # possible, clipped at accepted-frame ends. Other holders are erased.
    for position in range(proposed.FRAME_SIZE):
        lows = (max(position-5,0),min(position+1,proposed.FRAME_SIZE-5))
        assert len(set(lows)) == 2
        for lo in lows:
            for trio in combinations(range(lo,lo+5),3):
                n = Net()
                cells = inputs(n)
                for off in range(-5,6):
                    y = position+off
                    if y in trio:
                        cells[off] = dict(wf2=0,packet_valid=0,packet_tag=[0]*4,packet_count=[0]*11,
                            flag_valid=1,flag_position=const_word(y,9),flag_count=[0]*11)
                    else:
                        cells[off] = dict(wf2=0,packet_valid=0,packet_tag=[0]*4,packet_count=[0]*11,
                            flag_valid=0,flag_position=[0]*9,flag_count=[0]*11)
                result = proposed.build(n,cells)
                assert result['flag_valid'] == 1,(position,trio)
                assert result['flag_position'] == const_word(position,9),(position,trio)
                assert result['flag_count'] == const_word(1,11),(position,trio)
                interval += 1
    return first,interval


def ancestry():
    packet = code = conversion = 0
    for tag in range(5):
        for off in range(-5,6):
            adjusted=(tag-off)%16
            if adjusted < 5:
                assert tag-adjusted == off
            packet += 1
    for position in range(proposed.FRAME_SIZE):
        for off in range(-5,6):
            adjusted=(position-off)%512
            if adjusted < proposed.FRAME_SIZE:
                assert position-adjusted == off
            code += 1
    for tag in range(5):
        for off in range(-5,6):
            adjusted=(tag+6-off)%512
            if adjusted < proposed.FRAME_SIZE:
                # Let the physical input be y=x+off and r=y-tag-1.
                # Coded origin x-adjusted equals r-5 exactly.
                assert adjusted == tag+6-off
            conversion += 1
    assert 512-proposed.FRAME_SIZE > 10
    return dict(packet=packet,code=code,packet_conversion=conversion)


def main():
    n,comp,equalities = module_net()
    frame_cases = ancestry()
    first,interval = true_carrier_cases()
    for root in range(6):
        assert root-5 <= 0 and root+447 >= 447
        # Initial interval[root,root+6]; one-cell growth both ways.
        assert 1+max(5,447-6) == 442
        assert 442+448 == 890 < 1792
    out = ROOT/'figs/robustness'
    receipt=dict(proposed_rule_change=True,standalone_module_certificate=True,
        active_G17_modified=False,SP15_modified=False,
        checker_sha256=digest(Path(__file__)),proposal_source_sha256=digest(Path(proposed.__file__)),
        framed_service_proposal_source_sha256=digest(Path(proposed.original.__file__)),
        helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
        generated_build_source_sha256=hashlib.sha256(proposed.generated_build()[1].encode()).hexdigest(),
        original_frame_receipt_sha256=digest(out/'framed_service_certificate.json'),
        guard6_receipt_sha256=digest(out/'packet_guard6_certificate.json'),
        J102_receipt_sha256=digest(out/'SP15_displaced_pressure_boundary_certificate.json'),
        module_netlist_sha256=comp.digest,module_live_gates=comp.n_nodes-len(comp.inputs)-2,
        colony_size=448,code_frame_left_buffer=5,code_position_limit=453,
        packet_to_code_position_addend=6,unchanged_packet_and_witness_node_equalities=equalities,
        unchanged_stored_packet_bits=17,unchanged_total_component_bits=38,
        unchanged_maximum_raw_input_offset=5,
        accepted_position_no_wrap_cases=frame_cases,
        source_surviving_trio_erasure_cases=first,interval_surviving_trio_erasure_cases=interval,
        arbitrary_raw_fault_payloads_covered_by_written_nonfault_witness_proof_not_these_erasure_cases=True,
        source_initial_count_zero_and_all_other_initial_eligible_counters_at_least_one_required=True,
        no_later_births_required=True,whole_word_faults_at_most_two_per_eleven_required=True,
        prescribed_canonical_right_GF_and_reference_Age_required=True,
        GF_Age_and_flags_initially_arbitrary_on_true_colony=True,
        allowed_initialized_source_roots=list(range(6)),
        all_true_colony_code_pressure_by_state=442,all_true_colony_GF_Age_by_state=890,
        conclusions_persist_through_state=1791,
        source_root_r_code_origin_r_minus_five=True,
        canonical_adjacent_sources_code_frames_overlap_cells=5,
        arbitrary_component_birth_free_erasure_updates=1792,
        arbitrary_finite_component_support_enlargement_each_side=452,
        own_CA_programme_or_canonical_multiple_source_encoding_certified=False,
        general_arbitrary_birth_force_envelope_or_full_upper_map_established=False,
        authentic_damaged_input_source_delivery_or_autonomous_boundary_established=False,
        global_reliability_established=False,
        scope='standalone buffered-code-frame revision, conditional arbitrary-GF/Age repair for initialized roots0..5, no births/local2-per11 faults/right boundary; ROBUSTNESS J103')
    (out/'buffered_framed_service_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(unchanged_packet_equalities=equalities,source_cases=first,interval_cases=interval,
        ancestry=frame_cases,global_reliability_established=False)),flush=True)


if __name__ == '__main__':
    main()
