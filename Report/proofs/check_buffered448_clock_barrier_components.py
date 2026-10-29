#!/usr/bin/env python3
"""J113: actual SP16 components cross a correct positive clock barrier.

Compose J112's exact late endpoint with one error-free next update.
Projected intermediate outputs are literal constants; other second-row
fields stay free and therefore include their actual first-row values.
This is a local trajectory, not reachability from J111's initial seed.
"""
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,const_word
from check_buffered448_incorporation import full_net
import proposed_sparse_buffered448 as proposed

COMPONENT_FIELDS = ('wf2','packet_valid','packet_tag','packet_count',
                    'service_valid','service_position','service_count')
PROJECTED_FIELDS = ('addr','age','f1','f2','wf1',*COMPONENT_FIELDS)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def first_row(p,reader):
    class EndpointNet(Net):
        def input(self,key):
            if key[0] == 'x':
                _,off,field,bit=key
                y=reader+off
                if field == 'addr': return (((y if y >= 0 else y+4)%p.Q)>>bit)&1
                if field == 'age':
                    clock=p.T_wf if y < 0 or y in (1,2) else p.U-1
                    return (p.age_code(clock)>>bit)&1
                if field == 'f1': return int(y < 0)
                if field in ('f2','wf1','wf2','packet_valid','service_valid','pend'): return 0
                if field == 'info': return int(y+bit-2 in (-1,3))
                if field == 'hold': return 0
            return super().input(key)
    n,source=full_net(p,net_class=EndpointNet,observe=True)
    born=reader in (-3,-2,-1,1)
    gf=(reader+4 if reader < 0 else reader)%p.Q
    clock=p.T_wf+1 if reader < 0 else 0
    expected=dict(addr=const_word(gf,p.k),age=const_word(p.age_code(clock),p.m),
        f1=[int(reader < 0 and reader not in (-6,-5))],f2=[0],wf1=[0],wf2=[int(born)],
        packet_valid=[int(born)],packet_tag=const_word(gf-1 if born else 0,4),
        packet_count=[0]*11,service_valid=[0],service_position=[0]*9,service_count=[0]*11)
    outputs={field:[n.outputs['y',field,b] for b in range(width)]
             for field,width in proposed.schema(p) if field in PROJECTED_FIELDS}
    assert outputs == expected,(reader,{f:v for f,v in outputs.items() if v != expected[f]})
    assert n.outputs['proof','birth'] == int(born),reader
    return outputs,hashlib.sha256(source.encode()).hexdigest()


def next_row(p,reader,first):
    class FollowingNet(Net):
        def input(self,key):
            if key[0] == 'x':
                _,off,field,bit=key
                y=reader+off
                if field in PROJECTED_FIELDS:
                    value=first[y][field][bit]
                    # The isolated positive singleton may be absent or
                    # present. Its actual first-row value is1; all
                    # following identities are independent of its presence.
                    if y == 1 and field in ('wf2','packet_valid'):
                        return super().input(('positive_singleton_present',))
                    return value
            return super().input(key)
    n,source=full_net(p,net_class=FollowingNet,observe=True)
    packet=reader in (0,1)
    code=reader in (0,1,2)
    expected=dict(addr=const_word(reader,p.k),age=const_word(p.age_code(1),p.m),
        f1=[0],f2=[int(code)],wf1=[0],wf2=[int(packet)],packet_valid=[int(packet)],
        packet_tag=const_word(reader+3 if packet else 0,4),
        packet_count=const_word(1 if packet else 0,11),
        service_valid=[int(code)],service_position=const_word(reader+9 if code else 0,9),
        service_count=const_word(1 if code else 0,11))
    outputs={field:[n.outputs['y',field,b] for b in range(width)]
             for field,width in proposed.schema(p) if field in PROJECTED_FIELDS}
    assert outputs == expected,(reader,{f:v for f,v in outputs.items() if v != expected[f]})
    assert n.outputs['proof','birth'] == 0,reader
    return dict(reader=reader,new_GF=reader,new_clock=1,new_Flag1=0,
        new_Flag2=int(code),packet_valid=int(packet),
        packet_tag=reader+3 if packet else 0,packet_count=int(packet),
        packet_origin=-4 if packet else None,
        code_valid=int(code),code_position=reader+9 if code else 0,
        code_count=int(code),code_origin=-9 if code else None),hashlib.sha256(source.encode()).hexdigest()


def main():
    candidate=proposed.load_artifact()
    p=candidate.p
    first={}
    for reader in range(-12,20):
        first[reader],source=first_row(p,reader)
    rows=[]
    for reader in range(8):
        row,next_source=next_row(p,reader,first)
        assert source == next_source
        rows.append(row)
    assert 3 < p.Q-5 and 5 < (1<<4)-5
    # Exactly the three negative births are needed for these two cohorts.
    for reader in range(3):
        assert all(abs(y-reader) <= 5 for y in (-3,-2,-1))
        adjusted_tags={(y+3)-(y-reader) for y in (-3,-2,-1)}
        adjusted_positions={(y+9)-(y-reader) for y in (-3,-2,-1)}
        assert adjusted_tags == {reader+3}
        assert adjusted_positions == {reader+9}
        assert (reader+3 < 5) == (reader < 2)
        assert reader+9 < 453
    out=ROOT/'figs/robustness'
    receipt=dict(proposal='SP16',proposed_rule_change=False,active_G17_modified=False,SP15_modified=False,
        checker_sha256=digest(Path(__file__)),proposal_source_sha256=digest(Path(proposed.__file__)),
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
        full_rule_checker_sha256=digest(ROOT/'Report/proofs/check_buffered448_incorporation.py'),
        buffered_service_source_sha256=digest(Path(proposed.service.__file__)),
        proof_observation_generated_source_sha256=source,
        incorporation_receipt_sha256=digest(out/'SP16_buffered_incorporation_certificate.json'),
        period_barrier_receipt_sha256=digest(out/'SP16_period_barrier_certificate.json'),
        initial_input_clock=p.U-1,initial_current_E0_pair=[1,2],
        first_projected_readers_inclusive=[-12,19],first_projected_field_cofactors=32,
        first_projected_output_bits_per_reader=sum(width for field,width in proposed.schema(p) if field in PROJECTED_FIELDS),
        projected_fields=list(PROJECTED_FIELDS),following_full_rule_cofactors=len(rows),following_outputs=rows,
        no_errors_in_second_update=True,
        all_other_second_update_fields_free_including_actual_first_outputs=True,
        positive_singleton_presence_free_in_second_update=True,
        no_positive_birth_in_second_update=True,
        correct_positive_GF_Age_and_quiet_Flag1_WF1_preserved_in_displayed_outputs=True,
        incoming_negative_root_packet_and_code_accepted_at_positive_zero_clock=True,
        positive_birth_exclusion_alone_does_not_imply_component_reset=True,
        no_active_or_prototype_rule_or_ROM_modified=True,
        reachability_from_J111_initial_native_and_work_seed_established=False,
        full_boundary_reset_or_general_higher_error_map_established=False,
        global_reliability_established=False,
        scope='ROBUSTNESS J113: exact two-update local F16 witness from J112 endpoint; negative root-4 births cross positive clock0 without positive second-row births; pristine-seed reachability and iid failure unproved')
    (out/'SP16_clock_barrier_components_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(first_cofactors=32,following_cofactors=8,following_outputs=rows,
        global_reliability_established=False)),flush=True)


if __name__ == '__main__':
    main()
