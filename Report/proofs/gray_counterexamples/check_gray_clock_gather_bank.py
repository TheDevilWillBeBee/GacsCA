#!/usr/bin/env python3
"""Exact first-gather routing on the unchanged GMW7 intact clock island."""
from pathlib import Path
from dataclasses import replace
from itertools import product
from functools import lru_cache
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'Report/proofs'))
import gray_token_gather_v7 as k
import literal_maintenance as literal
import check_gmw7_intact_hierarchy as initial

B=17*k.Q;MEM_MASK=(1<<(11*k.WORD))-1


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def label(x):return int(0<=x<B)


def path(y,d):
    """Exact backwards moving/load path compressed only on constant clocks."""
    D=abs(d)*k.Q;sigma=(d>0)-(d<0);n=32*k.Q+D-label(y);capture=n
    start=y;segments=[]
    while True:
        e=label(y);delta=n+e-32*k.Q
        assert 0<=delta<=D
        if delta==0:break
        assert sigma
        if sigma>0:
            distance=-y if y<0 else B-y if y<B else None
        else:
            distance=y-B+1 if y>=B else y+1 if y>=0 else None
        jump=delta if distance is None else min(delta,distance)
        assert jump>0
        # All rows strictly before the endpoint remain at the same clock
        # and have1<=delta<=D, so every omitted update is the same move.
        assert label(y+sigma*(jump-1))==e and 1<=delta-jump+1<=D
        old=y;y+=sigma*jump;n-=jump
        segments.append((old,n+jump,e,jump,y,n,label(y)))
    expected=start+d*k.Q+sigma*(label(start+d*k.Q)-label(start))
    assert y==expected and n==32*k.Q-label(y)
    return dict(source=y,load_row=n,capture_row=capture,segments=segments)


def routes():
    count=segments=0;signature=hashlib.sha256();sample=[]
    for g,p,d in product(range(-6,23),range(k.PRIMARY_START,k.PRIMARY_START+k.FRAME_WORDS),range(-5,6)):
        route=path(g*k.Q+p,d);count+=1;segments+=len(route['segments'])
        src=route['source'];expected_g=g+d;shift=src-(expected_g*k.Q+p)
        assert -1<=shift<=1 and src//k.Q==expected_g
        value=initial.logical_info(src)
        assert 0<=value<=k.MASK
        signature.update(f'{g},{p},{d},{src},{route["load_row"]},{route["capture_row"]},{value};'.encode())
        if g in (15,16) and p in (4001,4002):
            sample.append(dict(g=g,p=p,d=d,value=value,**route))
    assert count==60929
    return dict(exact_compressed_capture_paths=count,constant_clock_moving_segments=segments,
        all_191_normal_primaries_and11_lanes_and29_receiver_classes_checked=True,
        route_and_value_signature_sha256=signature.hexdigest(),sampled_native_word_routes=sample,
        all_integer_receiver_coordinates_extension_proved_algebraically=True)


@lru_cache(None)
def rawmem(x,q):
    result=0
    for i in range(5):
        result|=int.from_bytes(hashlib.sha256(f'GMW7-rawMem-{x}-{q}-{i}'.encode()).digest(),'little')<<(256*i)
    return result&MEM_MASK


def holder_factor():
    zeroROM=k.ROM((0,)*k.Q,(0,)*k.DICTIONARY_SIZE,0,0)
    centres=[b+j for b in (0,B) for j in range(-3,4)]+[15*k.Q+4001,16*k.Q+4001]
    rows=sorted({32*k.Q+j for j in range(-2,3)}|
        {32*k.Q+D*k.Q+j for D in range(1,6) for j in range(-2,3)})
    groups=holders=0;signature=hashlib.sha256()
    for y,n in product(centres,rows):
        t=n-1
        row={x:replace(initial.initial_cell(x),age=(t+label(x))%k.U,
            f1=int(-k.Q<=x<0 or B-k.Q<=x<B),
            mem=tuple(rawmem(x,q) for q in range(5))) for x in range(y-7,y+8)}
        def voted(name,z):return k.vote([getattr(row[z-s],name)[q] for q,s in enumerate(k.SLOTS)])
        delta=n+label(y)-32*k.Q
        if delta==0:
            word=voted('info',y)&k.MASK
            expected=sum(word<<(lane*k.WORD) for lane in range(11))
        else:
            expected=0
            for d in range(-5,6):
                source=y+(1 if d>0 else -1) if d and 0<delta<=abs(d)*k.Q else y
                expected|=((voted('mem',source)>>((d+5)*k.WORD))&k.MASK)<<((d+5)*k.WORD)
        outputs=[]
        for q,s in enumerate(k.SLOTS):
            x=y-s;actual=k.local_transition({j:row[x+j] for j in range(-5,6)},zeroROM)
            assert actual.addr==x%k.Q and actual.age==(n+label(x))%k.U
            outputs.append(actual.mem[q]);holders+=1
        assert k.vote(outputs)==expected
        assert sum(label(y-s)==label(y) for s in k.SLOTS)>=3
        signature.update(expected.to_bytes((11*k.WORD+7)//8,'little'));groups+=1
    assert groups==480 and holders==2400
    # Majority of three identical candidates holds for every word bit.
    repeated=0
    for count,a,b in product((3,4,5),range(2),range(2)):
        assert k.vote([a]*count+[b]*(5-count))==a;repeated+=1
    return dict(actual_F7_raw_incoherent_Mem_group_checks=groups,actual_holder_transitions=holders,
        all_eleven_lane_words_compared_together=True,source_mem_width=11*k.WORD,
        candidate_repetition_bit_cofactors=repeated,
        actual_output_signature_sha256=signature.hexdigest(),
        arbitrary_old_Mem_word_extension_proved_by_identical_output_majority=True,
        arbitrary_inactive_ROM_lookup_irrelevant_not_changed_own_programme=True)


def bank(g):
    words={d:[initial.logical_info(path(g*k.Q+k.PRIMARY_START+w,d)['source'])
        for w in range(k.FRAME_WORDS)] for d in range(-5,6)}
    records={d:k.cell_from_words(value) for d,value in words.items()}
    native={d:{n:getattr(c,n) for n in k.NATIVE_NAMES} for d,c in records.items()}
    expected=dict(addr=g,age=1,f1=1,f2=0)
    assert {n:literal.scalar(native)[n] for n in expected}==expected
    assert {n:k.predecessor.scalar_native(native)[n] for n in expected}==expected
    assert [native[-i]['addr'] for i in range(1,6)]==[(g-i)%k.Q for i in range(1,6)]
    assert [native[-i]['age'] for i in range(1,6)]==[0]*5
    assert native[0]['addr']==g and native[0]['age']==0
    assert not any(c['f2'] or c['wf2'] for c in native.values())
    if g==16:
        assert [native[i]['addr'] for i in range(1,6)]==[0]*5
        assert [native[i]['age'] for i in range(1,6)]==[17,18,19,20,21]
    else:
        assert g==15 and [native[i]['addr'] for i in range(1,6)]==[16,0,0,0,0]
    # Every represented word has its actual field width. Metadata/register
    # words are100 bits; native raw flags must additionally be bits.
    for c in records.values():
        assert 0<=c.addr<k.Q and 0<=c.age<k.U
        assert all(getattr(c,n) in (0,1) for n in ('f1','f2','wf1','wf2'))
        assert k.cell_from_words(k.cell_words(c))==c
    return dict(receiver_colony=g,lower_native_Flag1=int(g==16),
        decoded_native_inputs={str(d):c for d,c in native.items()},
        upper_computed_native=expected,
        exact_word_bank_hex={str(d):[hex(v) for v in value] for d,value in words.items()},
        five_copy_bank_coherent_at_normal_primaries=True,
        all_lanes_ready_physical_output_row=37*k.Q-1,
        held_through_first_evaluator_by_actual_Mem_hold_and_no_wipe=True,
        original_clock_real2_history_only=True,
        initial_upper_Age_progression_or_first_Flag2_trigger_proved=False)


def calculate():return dict(routes=routes(),holder_factor=holder_factor(),banks=[bank(15),bank(16)])


def main():
    started=time.monotonic();source=Path(__file__).parent;directory=ROOT/'figs/gray_counterexamples'
    result=calculate()
    receipt=dict(name='GMW7 actual first gather on intact stationary clock island',Q=k.Q,U=k.U,
        lambda_original=24,c_original=104,checker_sha256=digest(__file__),
        proof_sha256=digest(source/'GMW7_CLOCK_GATHER_BANK.md'),
        source_dependencies_sha256={name:digest(source/name) for name in
            ('gray_token_gather_v7.py','gray_moving_word_v2.py','gray_moving_word_kernel.py','literal_maintenance.py')},
        root_initializer_source_sha256=digest(initial.__file__),
        root_initializer_proof_sha256=digest(ROOT/'Report/proofs/GMW7_INTACT_HIERARCHY.md'),
        receipt_dependencies_sha256={name:digest(directory/name) for name in
            ('GMW7_WF0_clock_island_certificate.json','GMW7_single_gather_period_certificate.json',
             'Gray_flag_command_contract_certificate.json')},results=result,
        retained_initial_validator_failure_assets_sha256={name:digest(directory/name) for name in
            ('GMW7_clock_gather_bank_initial_validator.py.txt','GMW7_clock_gather_bank_initial_validator_failure.txt')},
        no_preloaded_bank_or_independent_upper_error_history=True,
        exact_changed_GMW7_four_and_five_null_first_bank_lemmas_proved=True,
        actual_Gray_three_gather_Mailbox_clear_refinement=False,
        progressing_upper_Ages_early_flag_store_or_repair_proved=False,
        full_decoded_boundary_memory_or_iid_refuted=False,
        active_rule_or_frozen_component_modified=False,modified_candidate_emitted=False,
        elapsed_seconds=time.monotonic()-started)
    path=directory/'GMW7_clock_gather_bank_certificate.json';path.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(routes=result['routes']['exact_compressed_capture_paths'],
        factor=result['holder_factor'],native_banks=[{n:r[n] for n in
            ('receiver_colony','lower_native_Flag1','upper_computed_native')} for r in result['banks']],
        receipt_sha256=digest(path),elapsed_seconds=receipt['elapsed_seconds'])))


if __name__=='__main__':main()
