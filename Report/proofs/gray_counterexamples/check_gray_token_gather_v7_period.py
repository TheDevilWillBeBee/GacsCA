#!/usr/bin/env python3
"""GMW7 actual raw-holder gather and changed encoded-period cofactors.

The universal route, code and period arguments are in the linked proof.
Finite full-kernel comparisons supplement them; no whole-period simulation
or faithfully reconstructed Gray programme is asserted by this checker.
"""
from pathlib import Path
import hashlib,itertools,json,random,sys,time
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
import gray_token_gather_v7 as k
import build_gray_token_gather_v7 as builder
import check_gray_token_word_v6_E0 as ancestor


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def lane_shift(lane,delta):
    d=lane-5
    return (1 if d>0 else -1 if d<0 else 0)*min(max(delta,0),abs(d)*k.Q)


def word(x):
    # A deterministic legal Word100 injection on this finite source domain.
    return (x+10*k.Q+17)*0x123456789abcdef


def gather_slice(address,delta):
    """A quiet current row with the exact previous gather route values."""
    clock=(32*k.Q+delta-1)%k.U
    data={}
    for y in range(address-7,address+8):
        data[y]=dict(heads=0,mem=sum(word(y+lane_shift(lane,delta-1))<<(lane*k.WORD)
            for lane in range(11)),out=word(y+5),info=word(y),scratch=word(y-5),program=0)
    cells={j:k.Cell(addr=(address+j)%k.Q,age=clock,
        **{name:tuple(data[address+j+s][name] for s in k.SLOTS) for name in data[address]})
        for j in range(-5,6)}
    return cells


def route_arithmetic():
    identities=0;maximum_distance=0
    # Every gather tick/lane, including the first stationary row past freeze.
    for delta in range(1,5*k.Q+2):
        for lane in range(11):
            d=lane-5;step=(1 if d>0 else -1) if d and delta<=abs(d)*k.Q else 0
            assert step+lane_shift(lane,delta-1)==lane_shift(lane,delta)
            identities+=1
    holders=[]
    for delta_source in (-1,0,1):
        for s,t in itertools.product(k.SLOTS,repeat=2):
            offset=s+delta_source-t
            assert -5<=offset<=5
            maximum_distance=max(maximum_distance,abs(offset))
            holders.append(dict(output_slot=s,old_source_step=delta_source,input_slot=t,
                actual_raw_offset=offset))
    # Each represented word has the same colony offset after capture.
    captures=[]
    for w in range(k.FRAME_WORDS):
        primary=k.PRIMARY_START+w
        for lane in range(11):
            d=lane-5;source=primary+d*k.Q
            assert source//k.Q==d and source%k.Q==primary
            for s in k.SLOTS:
                holder=primary-s
                assert 0<=holder<k.Q
            captures.append(dict(word=w,primary=primary,lane=lane,source_colony=d,
                source_primary=source%k.Q,capture_age=32*k.Q+abs(d)*k.Q))
    assert identities==450571 and len(holders)==75 and len(captures)==2101
    return dict(all_delta_lane_identities=identities,raw_holder_routes=holders,
        maximum_raw_radius=maximum_distance,represented_capture_routes=captures,
        final_capture_age=37*k.Q)


def actual_gather_checks(rom):
    deltas=sorted({0,1,5*k.Q+1}|{d*k.Q+e for d in range(1,6) for e in (-1,0,1)})
    addresses=sorted(set(ancestor.GF_CLASSES+[k.PRIMARY_START,k.PRIMARY_START+k.FRAME_WORDS-1]))
    rng=random.Random(0x7E0);count=0;row_count=0;rows=[]
    for address in addresses:
        for delta in deltas:
            clean=gather_slice(address,delta);expected=k.local_transition(clean,rom)
            for i,s in enumerate(k.SLOTS):
                words=[(expected.mem[i]>>(lane*k.WORD))&k.MASK for lane in range(11)]
                assert words==[word(address+s+lane_shift(lane,delta)) for lane in range(11)]
                assert expected.info[i]==word(address+s)
            assert expected.addr==address%k.Q and expected.age==32*k.Q+delta
            assert not any(getattr(expected,n) for n in ('f1','f2','wf1','wf2'))
            # Replace *whole raw cells*, including clocks, controls and all
            # packet metadata. These finite payloads are implementation checks;
            # the all-payload extension uses the row-bound vote proof.
            payloads=[ancestor.arbitrary_cell(rng,maximum=True),ancestor.arbitrary_cell(rng)]
            payloads=[k.cell_from_words(ancestor.k.cell_words(c)) for c in payloads]
            for support in ancestor.SUPPORTS:
                noisy=dict(clean)
                for i,j in enumerate(support):noisy[j]=payloads[i]
                assert k.local_transition(noisy,rom)==expected
                count+=1
            rows.append(dict(address=address,delta=delta,
                clean_inputs=[[hex(v) for v in k.cell_words(clean[j])] for j in range(-5,6)],
                fault_payloads=[[hex(v) for v in k.cell_words(c)] for c in payloads],
                clean_output=[hex(v) for v in k.cell_words(expected)]))
            row_count+=1
    assert row_count==len(addresses)*len(deltas) and count==67*row_count
    return dict(rows=row_count,whole_cell_support_comparisons=count,
        addresses=addresses,deltas=deltas,finite_payloads_measured_only=True),rows


def main():
    started=time.monotonic();directory=ROOT/'figs/gray_counterexamples';source=Path(__file__).parent
    rom,_,_,errors=builder.programme().assemble();assert not errors
    routes=route_arithmetic();checks,replays=actual_gather_checks(rom)
    paths={}
    for key,name,data in (('routes','GMW7_gather_routes.json',routes),
        ('replays','GMW7_gather_full_cell_replays.json',replays)):
        path=directory/name;path.write_text(json.dumps(data,separators=(',',':'))+'\n');paths[key]=digest(path)
    receipt=dict(name='GMW7 changed physical single-gather and encoded-period component',
        Q=k.Q,U=k.U,lambda_original=24,c_original=104,
        kernel_sha256=digest(k.__file__),builder_sha256=digest(builder.__file__),checker_sha256=digest(__file__),
        proof_sha256=digest(source/'GMW7_SINGLE_GATHER_PERIOD.md'),
        prepared_receipt_sha256=digest(directory/'GMW7_prepared_execution_certificate.json'),
        bound_receipt_sha256=digest(directory/'GMW7_execution_bound.json'),
        ancestor_E0_proof_sha256=digest(source/'GMW6_E0_COMPONENT_COUPLING.md'),
        ancestor_E0_checker_sha256=digest(ancestor.__file__),asset_sha256=paths,
        all_lane_tick_route_identities=routes['all_delta_lane_identities'],
        represented_capture_routes=len(routes['represented_capture_routes']),
        actual_holder_source_radius=routes['maximum_raw_radius'],
        final_capture_age=37*k.Q,reset_age=112*k.Q,birth_age=112*k.Q+1,
        active_first_output_age=112*k.Q+2,active_last_output_age=120*k.Q,
        active_updates=65535,universal_execution_bound=49068,finite_gather_checks=checks,
        own_beta_semantics_proved_by_register_contracts=True,
        broad_Info_encoded_period_proved_for_changed_rule=True,
        pure_E0_majority_decoder_period_proved_for_changed_rule=True,
        single_gather_fixed_zero_Workspace_word_IO_extra_dictionary_changes_explicit=True,
        total_immutable_capacity_bits=59392,
        literal_Gray_three_gathers_early_flags_or_flag_repair_proved=False,
        real1_higher_or_iid_or_shorter_U_proved=False,active_rule_modified=False,
        elapsed_seconds=time.monotonic()-started)
    (directory/'GMW7_single_gather_period_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(route_identities=receipt['all_lane_tick_route_identities'],
        capture_routes=receipt['represented_capture_routes'],checks=checks,
        elapsed_seconds=receipt['elapsed_seconds'])))


if __name__=='__main__':main()
