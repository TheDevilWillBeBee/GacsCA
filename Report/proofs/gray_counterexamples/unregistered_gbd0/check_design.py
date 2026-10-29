"""Exact GBD0 listing/layout/locality audit; no whole-rule fit claim."""
import argparse
import bz2
import collections
import hashlib
import json
import lzma
from pathlib import Path
import random
import zlib

import packed_window as w

ROOT = Path(__file__).resolve().parents[4]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def primary_requirements():
    p=ROOT/'papers_txt/gray_readers_guide.txt'
    text=p.read_text()
    assert 'fact, that Q\x1e2K' in text
    assert 'program for that transition function has no more than Q bits' in text
    assert 'our enhanced\nversion of M0 can simulate itself if Q is sufficiently large' in text
    return dict(text_source=str(p.relative_to(ROOT)),sha256=sha(p),
                binary_capacity_location='printed page33/text1497-1501',
                sufficiently_large_programme_location='printed pages30-31/text1347-1406',
                displayed_lower_bound_is_not_a_numeric_beta_fit=True)


def listing_accounting():
    p = ROOT / 'figs/gray_counterexamples/unregistered_gbc6/GBC6_complete_register_attempt01.json'
    r = json.loads(p.read_text())
    boundaries = [
        ('native_context_and_raw_wipe', 0, 'no_wipe'),
        ('gather_reset_and_hold', 'no_wipe', 'complete_after_history'),
        ('head_selection_and_control', 'complete_after_history', 'cpu_wordout'),
        ('data_modes', 'cpu_wordout', 'cpu_run'),
        ('run_opcode_simulation', 'cpu_run', 'head_birth'),
        ('birth_and_collection', 'head_birth', 'head_stage_done'),
        ('flag_couriers', 'head_stage_done', 'courier_next'),
        ('final_computed_source', 'courier_next', 'copy_group'),
        ('software_helpers', 'copy_group', r['programme_bits']),
    ]
    listing = r['listing']
    labels = r['labels']
    def resolve(x):
        return labels[x] if isinstance(x, str) else x
    groups = []
    for name, lo, hi in boundaries:
        lo, hi = resolve(lo), resolve(hi)
        rows = [x for x in listing if lo <= x[0] < hi]
        bits = collections.Counter()
        for _, opcode, _, length in rows:
            bits[opcode] += length
        assert sum(bits.values()) == hi - lo
        groups.append(dict(name=name, start=lo, end=hi, bits=hi-lo,
                           instructions=len(rows), opcode_bits=dict(bits)))
    assert sum(x['bits'] for x in groups) == 42716
    assert sum(x['instructions'] for x in groups) == 3140
    allbits = collections.Counter()
    for x in groups:
        allbits.update(x['opcode_bits'])
    # A byte-packing diagnostic of exactly the old WRAPPED rejection.
    beta = r['wrapped_diagnostic_bits']
    assert len(beta) == 42716
    blob = bytes(sum(beta[k+i] << i for i in range(min(8, len(beta)-k)))
                 for k in range(0, len(beta), 8))
    compressed = dict(zlib9=8*len(zlib.compress(blob, 9)),
                      xz9=8*len(lzma.compress(blob, preset=9)),
                      bz2=8*len(bz2.compress(blob)))
    assert all(v > w.Q for v in compressed.values())
    cpu_groups = ('head_selection_and_control', 'data_modes',
                  'run_opcode_simulation', 'birth_and_collection')
    eliminated = sum(x['bits'] for x in groups if x['name'] in cpu_groups)
    retained = 42716 - eliminated
    assert retained == 13523 > w.Q
    return dict(source=str(p.relative_to(ROOT)), sha256=sha(p),
                groups=groups, opcode_bits=dict(allbits),
                total_bits=42716, instructions=3140,
                invalid_references=len(r['invalid_references']),
                cpu_oracle_eliminated_bits=eliminated,
                non_cpu_remainder_bits=retained,
                required_reduction_bits=42716-w.Q,
                compression_of_wrapped_rejection_bits=compressed,
                diagnostic_compression_is_issued_beta=False)


def layout_accounting():
    native = 37
    table = []
    for radius in (5, 8):
        for word in (8, 11, 15, 16, 20, 100):
            h = native + 15 * (2*radius+1) * word
            hv = native + 20 * (2*radius+1) * word
            table.append(dict(radius=radius, word_bits=word,
                              retained_history_only_K=h,
                              plus_voted_bank_K=hv,
                              history_fits_Q_at_least_2K=2*h<=w.Q,
                              history_and_vote_fit=2*hv<=w.Q))
    assert native + 15*17*20 == 5137
    assert native + 20*17*20 == 6837
    whole_word_layout = dict(
        info_out_scratch_program_words=4, mail_words=2,
        courier_words=2, retained_history_words=3*17,
        voted_words=17, head_words=22)
    count = sum(whole_word_layout.values())
    assert count == 98
    K = native + 5*count*20
    assert K == 9837
    assert max(v for v in range(1,100) if 2*(native+5*count*v)<=w.Q)==8
    minimum_power_two_Q = 1 << (2*K - 1).bit_length()
    assert minimum_power_two_Q == 32768
    # Proposed layout only: no rule/ISA/emission or period is asserted.
    head = dict(p=1, move=2, mode=2, pc=13, ret=13, target=13,
                remaining=5, lane=5, kind=3, index=5, dst=2,
                four_word_registers=4*20, native_result=35)
    assert sum(head.values()) == 179
    fields = dict(info=1, valid_payload_mail=4, binary_history=3*17,
                  packed_voted_words=17*20,
                  input_packet_tag_valid=14, word_output=20,
                  output_packet_tag_valid=14, scratch_word=20,
                  flag_couriers=2, head=sum(head.values()))
    assert sum(fields.values()) == 645
    packed_K = native + 5*sum(fields.values())
    assert packed_K == 3262 and 2*packed_K == 6524 < w.Q
    return dict(native_bits=native, Q=w.Q, radius_word_table=table,
                history_r8_word20_2K=10274,
                word_parallel_field_words=whole_word_layout,
                word_parallel_total_words=count,
                word20_full_K=K, word20_full_2K=2*K,
                necessary_power_two_Q_for_full_word20_layout=minimum_power_two_Q,
                full_layout_max_word_bits_at_Q_2K=8,
                proposed_hybrid_head_bits=head,
                proposed_hybrid_fields=fields,
                proposed_hybrid_K=packed_K,
                proposed_hybrid_2K=2*packed_K,
                proposed_hybrid_slack_at_2K=w.Q-2*packed_K,
                proposed_packed_chunks=(packed_K+19)//20,
                proposed_descriptor_bits=dict(SF=10*23,Head=13*17,
                    loop_counts=8,native=6*12),
                proposed_descriptor_total_bits=531,
                proposed_candidate_encoding_bits=dict(HALT=3,ALU=13,
                    BR=20,READ=14,WRITE=16,CODE=7,MOVE=5,
                    LIT_min=6,LIT_max=46),
                sufficient_rows_at_all46bit_worst_case=(w.Q-531)//46,
                instruction_class_counts=None,
                prototype_exists=False, own_beta_exists=False,
                universal_execution_bound_exists=False)


def window_certificate():
    coordinate_cases = 0
    bit_targets = 0
    used = set()
    endpoints = None
    for q in range(5):
        for c in (-1,0,1):
            for phase in range(20):
                for stride in (1,5):
                    for count in range(21):
                        t = w.targets(q,c,phase,stride,count)
                        coordinate_cases += 1
                        assert len(t) == count
                        for cells in t:
                            assert len(cells) == 5
                            assert len({d for d,_ in cells}) == 5
                            bit_targets += len(cells)
                            for d,bit in cells:
                                assert -8 <= d <= 8 and 0 <= bit < 20
                                used.add(d)
                                if d == 8:
                                    endpoints = dict(q=q,centre=c,phase=phase,
                                                     stride=stride,count=count)
    assert used == set(range(-7,9)) and endpoints is not None
    # Exact bitwise vote proof has only these 32 cases; each physical
    # source bit is distinct. High raw lane bits and other lanes don't enter.
    for value in range(32):
        copies = [(value>>i)&1 for i in range(5)]
        assert w.majority_word(copies) == int(sum(copies)>=3)
    # Packing map is checked for every control/index: no approximate lane
    # or head-centre substitutions. A source raw bit index is phase+stride*i.
    packing_identities = 0
    for phase in range(20):
        for stride in (1,5):
            for i in range(20):
                chunk, bit = divmod(phase+stride*i,20)
                assert 20*chunk+bit == phase+stride*i
                assert 0<=chunk<=5
                packing_identities += 1
    # Selected arbitrary full words compare two literal formulations.
    # The universal conclusion follows from the preceding bit truth table
    # and indexing proof; random comparisons are separately measured.
    rng = random.Random(8192104)
    comparisons = 0
    for _ in range(240):
        raw = {d:rng.getrandbits(17*20) for d in range(-8,9)}
        q,c,lane,phase,stride,count = (rng.randrange(5),rng.choice((-1,0,1)),
            rng.randrange(17),rng.randrange(20),rng.choice((1,5)),rng.randrange(21))
        assert w.read_window(raw,q,c,lane,phase,stride,count) == \
               w.composed_window(raw,q,c,lane,phase,stride,count)
        comparisons += 1
    # A true endpoint cofactor: some permitted controls read d=8 and a
    # two-vs-three holder vote makes the component depend on that raw bit.
    t = w.targets(**endpoints)
    i,cells = next((i,cells) for i,cells in enumerate(t) if any(d==8 for d,_ in cells))
    bit = next(bit for d,bit in cells if d==8)
    others = [d for d,_ in cells if d!=8]
    raw = {d:0 for d in range(-8,9)}
    for d in others[:2]: raw[d] |= 1<<bit
    before = w.read_window(raw,lane=0,**endpoints)
    raw[8] |= 1<<bit
    after = w.read_window(raw,lane=0,**endpoints)
    assert (before ^ after) & (1<<i)
    invalid = [(5,0,0,0,1,1),(0,2,0,0,1,1),(0,0,17,0,1,1),
               (0,0,0,20,1,1),(0,0,0,0,2,1),(0,0,0,0,1,21)]
    raw = {d:(1<<340)-1 for d in range(-8,9)}
    assert all(w.read_window(raw,*x)==0 for x in invalid)
    return dict(coordinate_control_cases=coordinate_cases,
                source_bit_coordinates_checked=bit_targets,
                lane_selection_cases=17, vote_truth_table_cases=32,
                packing_identities=packing_identities,
                selected_full_value_comparisons=comparisons,
                malformed_control_checks=len(invalid),
                exact_radius=8, physical_stencil=[-7,8], attained_endpoint=endpoints,
                endpoint_output_bit=i, universal_raw_component=True,
                bitwise_not_whole_word_vote=True,
                six_containers_required_for_all_phases=True,
                gate_upper_bound=w.circuit_upper_bound(),
                own_software_branch_proved=False,
                actual_gather_pack_implementation=False)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    a = parser.parse_args()
    proof = Path(__file__).with_name('GBD0_WHOLE_PROGRAMME_AND_PACKED_LAYOUT.md')
    r = dict(schema='GBD0-design-1', baseline=dict(Q=w.Q,U=w.U,lambda_=24,c=104),
             primary=primary_requirements(),
             listing=listing_accounting(), layout=layout_accounting(),
             packed_window=window_certificate(),
             source_hashes={str(p.relative_to(ROOT)):sha(p) for p in
                 (Path(__file__),Path(w.__file__),proof)},
             complete_rule=False, complete_own_emitter=False,
             Q_bit_own_beta=False, whole_period=False,
             faithful_Gray=False, noise_theorem=False,
             Gray_refutation=False, iid_failure=False, shorter_U=False,
             passed=True)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r,indent=2))


if __name__=='__main__':
    main()
