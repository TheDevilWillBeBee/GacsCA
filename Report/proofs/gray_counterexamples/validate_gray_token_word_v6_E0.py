#!/usr/bin/env python3
"""Read-only separate GMW6 current-row E0 component certificate validation."""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
import gray_token_word_v6 as k
import build_gray_token_word_v6 as builder
import check_gray_token_word_v6_E0 as check
from gacsca import gray_errors


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def quiet_native(cells,offset,clock):
    for x,c in cells.items():
        assert (c.addr,c.age,c.f1,c.f2,c.wf1,c.wf2)==((offset+x)%k.Q,clock,0,0,0,0)


def coherent_fields(cells):
    seen={}
    for x,c in cells.items():
        for name in ('heads','mem','out','info','scratch','program'):
            for q,s in enumerate(k.SLOTS):
                key=name,x+s;value=getattr(c,name)[q]
                assert key not in seen or seen[key]==value,(x,name,q)
                seen[key]=value


def validate(directory=None):
    directory=directory or ROOT/'figs/gray_counterexamples';source=Path(__file__).parent
    r=json.loads((directory/'GMW6_E0_component_certificate.json').read_text())
    for key,path in (('kernel_sha256',k.__file__),('builder_sha256',builder.__file__),
        ('checker_sha256',check.__file__),('proof_sha256',source/'GMW6_E0_COMPONENT_COUPLING.md'),
        ('classifier_sha256',gray_errors.__file__),
        ('frozen_prepared_receipt_sha256',directory/'GMW6_token_word_certificate.json')):
        assert digest(path)==r[key],(key,path)
    for name,value in r['dependencies_sha256'].items():assert digest(source/name)==value
    assert (r['Q'],r['U'],r['lambda_original'],r['c_original'])==(8192,1048576,24,104)
    assert not r['full_Gray_period_or_real1_or_iid_proved'] and not r['active_rule_modified']
    for key in ('all_GF_Age_payload_extension_is_algebraic_not_sampled',
        'quiet_coherent_current_row_coupling_proved_conditionally',
        'prepared_pure_E0_decoder_extension_proved_conditionally',
        'current_row_only_no_previous_error_wake','arbitrary_whole_cell_replacements',
        'immutable_ROM_is_rule_constant_explicit','constant_zero_Workspace_departure_explicit'):
        assert r[key]
    rom,_,_,errors=builder.programme().assemble();assert not errors
    native=check.native_cofactors();vote,groups=check.vote_cofactors()
    assert native==r['native_reduced_Boolean_cofactors']==156827 and vote==r['vote_cofactors']==3402
    assert {str(y):list(v) for y,v in groups.items()}==r['actual_holder_groups']
    path=directory/'GMW6_E0_full_cell_replays.json';assert digest(path)==r['full_cell_replay_sha256']
    rows=json.loads(path.read_text());count=0
    for row in rows:
        cells={j:k.cell_from_words([int(v,16) for v in row['clean_inputs'][j+5]]) for j in range(-5,6)}
        quiet_native(cells,row['address'],row['clock']);coherent_fields(cells)
        expected=k.local_transition(cells,rom)
        faults=[k.cell_from_words([int(v,16) for v in words]) for words in row['fault_payloads']]
        for support in check.SUPPORTS:
            changed=dict(cells)
            for i,x in enumerate(support):changed[x]=faults[i]
            assert k.local_transition(changed,rom)==expected;count+=1
    assert len(rows)==128 and count==r['full_cell_comparisons']['cases']==8576
    path=directory/'GMW6_E0_temporal_cone.json';assert digest(path)==r['temporal_cone_sha256']
    cone=json.loads(path.read_text())
    clean={x:k.cell_from_words([int(v,16) for v in words]) for x,words in cone['initial']}
    noisy=dict(clean);quiet_native(clean,cone['geometry_offset'],cone['native_clock_start']);coherent_fields(clean)
    faults={(row['x'],row['t']):k.cell_from_words([int(v,16) for v in row['raw_words']]) for row in cone['errors']}
    points=set(faults);assert points=={(0,1),(1,1),(30,3)} and gray_errors.level0_points(points)==points
    assert gray_errors.classify(points,points,Q=k.Q,U=k.U,sep=104)==cone['classifier']
    counts=[]
    for t in range(8):
        for (x,tick),value in faults.items():
            if tick==t:noisy[x]=value
        lo=min(clean)+5;hi=max(clean)-5
        next_clean={x:k.local_transition({j:clean[x+j] for j in range(-5,6)},rom) for x in range(lo,hi+1)}
        next_noisy={x:k.local_transition({j:noisy[x+j] for j in range(-5,6)},rom) for x in range(lo,hi+1)}
        assert next_noisy==next_clean
        quiet_native(next_clean,cone['geometry_offset'],(cone['native_clock_start']+t+1)%k.U)
        coherent_fields(next_clean);counts.append(len(next_clean));clean,noisy=next_clean,next_noisy
    assert counts==cone['per_row_counts']==[81,71,61,51,41,31,21,11] and sum(counts)==cone['updates']==368
    return dict(native_reduced_cofactors=native,bit_vote_cofactors=vote,
        full_cell_additional_measured_cases=count,finite_temporal_holder_updates=sum(counts),
        receipt_sha256=digest(directory/'GMW6_E0_component_certificate.json'),
        conditional_quiet_family_E0_coupling=True,full_Gray_real1_or_iid_proved=False)


if __name__=='__main__':
    start=time.monotonic();result=validate();result['elapsed_seconds']=time.monotonic()-start
    print(json.dumps(result))
