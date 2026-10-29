#!/usr/bin/env python3
"""Pinned GMW7 intact initializer contracts; universal proof is in the Markdown.

The finite checks supplement rank/self-encoding and all-time inductions. They
are not a whole-CA simulation or a proof of higher/iid error recovery.
"""
from pathlib import Path
import hashlib,json,sys,time

ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'Report/proofs/gray_counterexamples'
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(SOURCE))
import gray_token_gather_v7 as k


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def logical_info(y,trace=None):
    """Integer recursion with an explicitly checked decreasing rank."""
    while True:
        g,r=divmod(y,k.Q);w=r-k.PRIMARY_START
        if trace is not None:trace.append(y)
        if w==0:return g%k.Q
        i=w-k.FIELD['info']
        if not 0<=i<5:return 0
        parent=g+k.SLOTS[i]
        assert abs(y)>=4011 and abs(parent)<abs(y),(y,parent)
        y=parent


def initial_cell(x):
    return k.Cell(addr=x%k.Q,info=tuple(logical_info(x+s) for s in k.SLOTS))


def main():
    started=time.monotonic();out=ROOT/'figs/robustness';gray=ROOT/'figs/gray_counterexamples'
    assert (k.Q,k.U,k.WORD,k.PRIMARY_START,k.FRAME_WORDS)==(8192,1048576,100,4001,191)
    assert k.SLOTS==(0,-2,-1,1,2) and k.FIELD['info']==176
    assert k.NATIVE_NAMES==('addr','age','f1','f2','wf1','wf2')
    assert len(k.FIELD_NAMES)==37 and k.FIELD_NAMES[34]=='info'
    assert k.FIELD['info']+5<=k.FRAME_WORDS
    recursive=[k.PRIMARY_START+k.FIELD['info']+i for i in range(5)]
    assert recursive==list(range(4177,4182))
    assert min(min(r,k.Q-r) for r in recursive)==4011
    assert 4011*(k.Q-1)>3*k.Q  # Universal strict-rank arithmetic.
    # Actual word encoder, both signs and every possible native Address.
    primary_checks=holder_checks=legal_cells=0
    contexts=[*range(-k.Q,k.Q)]
    for g in contexts:
        cell=initial_cell(g);words=k.cell_words(cell)
        assert k.cell_from_words(words)==cell
        assert words[0]==g%k.Q and not any(words[1:176]) and not any(words[181:])
        assert words[176:181]==[logical_info(g+s) for s in k.SLOTS]
        assert all(0<=v<1<<k.WORD for v in words)
        for w,value in enumerate(words):
            primary=g*k.Q+k.PRIMARY_START+w
            assert logical_info(primary)==value,(g,w,value)
            primary_checks+=1
        for i,s in enumerate(k.SLOTS):
            assert cell.info[i]==logical_info(g+s)
            assert initial_cell(g-s).info[i]==logical_info(g)
            holder_checks+=2
        legal_cells+=1
    # Negative Euclidean division and very large coordinates cannot be
    # silently replaced by finite-ring wrapping. This remains finite evidence.
    big=[];maximum_trace=0
    for exponent in (16,32,64,128,512,1024,4096):
        for sign in (-1,1):
            g=sign*(1<<exponent)+17
            for i,r in enumerate(recursive):
                y=g*k.Q+r;trace=[];value=logical_info(y,trace)
                assert value==logical_info(g+k.SLOTS[i]) and 0<=value<k.Q
                assert all(abs(b)<abs(a) for a,b in zip(trace,trace[1:]))
                maximum_trace=max(maximum_trace,len(trace))
                big.append(dict(exponent=exponent,sign=sign,slot=i,trace_length=len(trace),value=value))
    assert primary_checks==16384*191==3129344 and holder_checks==163840 and len(big)==70
    deep=[]
    for sign in (-1,1):
        leaf=sign*k.Q+k.PRIMARY_START
        expected=logical_info(leaf)
        assert expected==(k.Q-1 if sign<0 else 1)
        for depth in (16,64,320):
            y=leaf
            for j in range(depth):
                i=j%5;y=(y-k.SLOTS[i])*k.Q+recursive[i]
            trace=[];assert logical_info(y,trace)==expected
            assert len(trace)==depth+1 and trace[-1]==leaf
            assert all(abs(b)<abs(a) for a,b in zip(trace,trace[1:]))
            maximum_trace=max(maximum_trace,len(trace))
            deep.append(dict(sign=sign,depth=depth,trace_length=len(trace),value=expected))
    assert len(deep)==6 and maximum_trace==321
    # Pin the existing period/coupling theorem, not just the finite checks.
    period=json.loads((gray/'GMW7_single_gather_period_certificate.json').read_text())
    assert period['kernel_sha256']==digest(k.__file__)
    assert period['proof_sha256']==digest(SOURCE/'GMW7_SINGLE_GATHER_PERIOD.md')
    assert period['broad_Info_encoded_period_proved_for_changed_rule']
    assert period['pure_E0_majority_decoder_period_proved_for_changed_rule']
    assert not period['literal_Gray_three_gathers_early_flags_or_flag_repair_proved']
    assert not period['real1_higher_or_iid_or_shorter_U_proved'] and not period['active_rule_modified']
    checkpoint=json.loads((gray/'checkpoint_validation.json').read_text())
    assert checkpoint['document_sha256']==digest(ROOT/'Report/GRAY_COUNTEREXAMPLES.md')
    assert not checkpoint['active_rule_modified'] and not checkpoint['global_reliability_established']
    fixture=out/'GMW7_intact_hierarchy_finite_checks.json'
    fixture.write_text(json.dumps(dict(context_range=[-8192,8192],represented_primary_equalities=primary_checks,
        actual_holder_equalities=holder_checks,legal_raw_encoder_roundtrips=legal_cells,
        large_coordinate_traces=big,deep_recursive_traces=deep,maximum_retained_trace_length=maximum_trace,
        finite_checks_supplement_written_universal_proof=True),indent=2)+'\n')
    source_names=('gray_token_gather_v7.py','build_gray_token_gather_v7.py',
        'GMW7_SINGLE_GATHER_PERIOD.md','GMW6_E0_COMPONENT_COUPLING.md')
    receipts=('GMW7_single_gather_period_certificate.json','GMW7_prepared_execution_certificate.json',
        'GMW7_execution_bound.json','checkpoint_validation.json')
    result=dict(name='GMW7 explicit intact infinite hierarchy and all-time noiseless/row-density corollary',
        Q=k.Q,U=k.U,lambda_original=24,c_original=104,Info_word_indices=list(range(176,181)),
        recursive_residues=recursive,minimum_recursive_absolute_coordinate=4011,
        logical_Info_range=[0,k.Q-1],represented_primary_equalities=primary_checks,
        actual_holder_equalities=holder_checks,legal_raw_encoder_roundtrips=legal_cells,
        large_coordinate_trace_count=len(big),deep_recursive_trace_count=len(deep),maximum_retained_trace_length=maximum_trace,
        unique_initializer_on_Z_proved_by_strict_rank=True,
        initializer_self_encoding_E7_X_contains_X_proved=True,
        simultaneous_intact_infinite_hierarchy_initialization_proved=True,
        all_time_all_level_noiseless_decoder_identity_proved=True,
        all_time_all_level_row_density_and_original_pure_E0_decoder_identity_proved=True,
        row_noise_limit={'window_sites':11,'maximum_whole_cell_replacements':2},
        arbitrary_legal_error_payloads=True,current_raw_error_row_decoding_proved=True,
        finite_initializer_checks_supplement_written_inductions=True,
        iid_positive_rate_satisfies_noise_hypothesis_almost_surely=False,
        real1_higher_or_iid_or_bit_memory_or_Gray_faithfulness_proved=False,
        global_reliability_established=False,active_G17_modified=False,
        rule_programme_or_constant_change=False,numerical_whole_CA_trajectory_used=False,
        checker_sha256=digest(__file__),written_proof_sha256=digest(ROOT/'Report/proofs/GMW7_INTACT_HIERARCHY.md'),
        initial_import_failure_receipt_sha256=digest(out/'GMW7_intact_hierarchy_initial_import_failure.json'),
        fixture_sha256=digest(fixture),source_dependencies_sha256={n:digest(SOURCE/n) for n in source_names},
        receipt_dependencies_sha256={n:digest(gray/n) for n in receipts},elapsed_seconds=time.monotonic()-started)
    (out/'GMW7_intact_hierarchy_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ('represented_primary_equalities','actual_holder_equalities',
        'maximum_retained_trace_length','all_time_all_level_noiseless_decoder_identity_proved',
        'global_reliability_established','elapsed_seconds')}),flush=True)


if __name__=='__main__':main()
