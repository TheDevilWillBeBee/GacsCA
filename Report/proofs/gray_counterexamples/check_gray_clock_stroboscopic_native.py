#!/usr/bin/env python3
"""Actual changed-F7 stroboscopic map on the shared intact clock history.

The physical lift is proved in GMW7_CLOCK_STROBOSCOPIC_NATIVE.md. This emits
exact finite full-rule coupling and supplementary raw-holder/program checks.
It changes neither F7 nor any previously accepted source or receipt.
"""
from pathlib import Path
from dataclasses import replace
from itertools import product
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'Report/proofs'))
import gray_token_gather_v7 as k
import build_gray_token_gather_v7 as builder
import check_gmw7_intact_hierarchy as initial

B=17*k.Q;SF=('heads','mem','out','info','scratch','program')
WIDTH={'heads':k.HEAD_BITS,'mem':11*k.WORD,'out':k.WORD,
    'info':k.WORD,'scratch':k.WORD,'program':k.WORD}


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def bitlabel(x):return int(0<=x<B)


def colonylabel(g):return int(0<=g<17)


def noise_native(x,t):
    h=min(3*t,k.Q)
    return dict(addr=x%k.Q,age=(t+bitlabel(x))%k.U,
        f1=int(-h<=x<0 or B-h<=x<B),f2=0,wf1=0,wf2=0)


def randomword(tag,width):
    result=0
    for i in range((width+255)//256):
        result|=int.from_bytes(hashlib.sha256(f'{tag}/{i}'.encode()).digest(),'little')<<(256*i)
    return result&((1<<width)-1)


def holder_factor(rom):
    phases=(0,1,32*k.Q-1,32*k.Q,32*k.Q+1,33*k.Q,37*k.Q-1,
        37*k.Q,37*k.Q+1,112*k.Q-1,112*k.Q,112*k.Q+1,
        112*k.Q+2,120*k.Q,120*k.Q+1,k.U-1)
    centres=[b+j for b in (0,B) for j in range(-3,4)]+[k.HEAD_ADDRESS,B-k.Q+k.HEAD_ADDRESS]
    signature=hashlib.sha256();groups=holders=0
    for y,phase in product(centres,phases):
        n=k.U+phase;t=n-1
        row={x:k.Cell(**noise_native(x,t),**{f:tuple(randomword(f'{y}/{phase}/{x}/{f}/{q}',WIDTH[f])
            for q in range(5)) for f in SF}) for x in range(y-7,y+8)}
        reference=k.local_transition({j:row[y+j] for j in range(-5,6)},rom)
        assert sum(bitlabel(y-s)==bitlabel(y) for s in k.SLOTS)>=3
        outputs={f:[] for f in SF}
        for q,s in enumerate(k.SLOTS):
            x=y-s;out=k.local_transition({j:row[x+j] for j in range(-5,6)},rom)
            assert {name:getattr(out,name) for name in k.NATIVE_NAMES}==noise_native(x,n)
            for f in SF:outputs[f].append(getattr(out,f)[q])
            holders+=1
        for f in SF:
            value=k.vote(outputs[f]);assert value==getattr(reference,f)[0],(y,phase,f)
            signature.update(value.to_bytes((WIDTH[f]+7)//8,'little'))
        groups+=1
    repeated=0
    for count,a,b in product((3,4,5),range(2),range(2)):
        assert k.vote([a]*count+[b]*(5-count))==a;repeated+=1
    return dict(actual_all_SF_raw_incoherent_group_checks=groups,actual_holder_transitions=holders,
        all_six_SF_fields_compared=True,phase_cases=list(phases),signature_sha256=signature.hexdigest(),
        repeated_candidate_bit_cofactors=repeated,universal_factor_by_identical_candidate_proof=True)


def clean(g,n,rom):
    c=initial.initial_cell(g)
    return replace(c,age=n,program=tuple(k.beta_bit(rom,(g+s)%k.Q) for s in k.SLOTS) if n else (0,)*5)


def captured_words(row,g,j):
    source=g+j;words=k.cell_words(row[source])
    shift=((j>0)-(j<0))*(colonylabel(source)-colonylabel(g))
    if shift==1:words=words[1:]+[0]
    elif shift==-1:words=[0]+words[:-1]
    assert 0<=words[0]<k.Q and 0<=words[1]<k.U
    projected=words.copy()
    for w in range(2,6):projected[w]&=1
    assert all(0<=v<=k.MASK for v in words)
    return words,projected,shift


def quiet_family(cell,g,n):
    assert cell.addr==g%k.Q and 1<=cell.age<=n
    assert not any(cell.heads+cell.mem+cell.out+cell.scratch)
    assert cell.wf1==cell.wf2==0
    assert all(0<=v<=k.MASK for v in cell.info+cell.program)
    assert k.cell_from_words(k.cell_words(cell))==cell


def stroboscopic(rom):
    lo=-128;hi=145;row={g:clean(g,0,rom) for g in range(lo,hi)}
    stages=[];first=None;native_signature=hashlib.sha256();word_signature=hashlib.sha256();cofactors=0
    prepared=[]
    for n in range(16):
        output={};safe_left=-5*(n+1);safe_right=17+5*(n+1)
        for g in range(lo+5,hi-5):
            records={j:k.cell_from_words(captured_words(row,g,j)[1]) for j in range(-5,6)}
            c=k.local_transition(records,rom);quiet_family(c,g,n+1);output[g]=c;cofactors+=1
            assert c.program==tuple(k.beta_bit(rom,(g+s)%k.Q) for s in k.SLOTS)
            for value in k.cell_words(c):word_signature.update(value.to_bytes((k.WORD+7)//8,'little'))
            for name in k.NATIVE_NAMES:native_signature.update(getattr(c,name).to_bytes(4,'little'))
            if not safe_left<=g<safe_right:assert c==clean(g,n+1,rom)
            if first is None and c.age!=n+1:
                first=dict(output_epoch=n+1,g=g,output={name:getattr(c,name) for name in k.NATIVE_NAMES},
                    inputs={str(j):dict(raw=dict(zip(k.NATIVE_NAMES,captured_words(row,g,j)[0][:6])),
                        projected={name:getattr(records[j],name) for name in k.NATIVE_NAMES},
                        capture_shift=captured_words(row,g,j)[2]) for j in range(-5,6)})
            if (n,g) in ((0,16),(1,16),(4,2),(9,13),(10,15),(15,16)):
                prepared.append(dict(name=f'epoch{n+1}_g{g}',raw={j:captured_words(row,g,j)[0]
                    for j in range(-5,6)},projected=records,expected=c))
        for g in range(lo,lo+5):output[g]=clean(g,n+1,rom)
        for g in range(hi-5,hi):output[g]=clean(g,n+1,rom)
        differences=[g for g,c in output.items() if c!=clean(g,n+1,rom)]
        assert not differences or min(differences)>lo+10 and max(differences)<hi-10
        f2=[g for g in range(17) if output[g].f2];assert not f2
        stages.append(dict(epoch=n+1,native=[{name:getattr(output[g],name) for name in k.NATIVE_NAMES}
            for g in range(-85,103)],right_edge_Ages=[output[g].age for g in (13,14,15,16)],
            maximum_Age=max(c.age for c in output.values()),all_Address_canonical=True,
            Flag2_columns_inside=f2,all_Head_Mem_Out_Scratch_zero=True,
            differing_full_cell_columns=differences,coupling_safe_interval=[safe_left,safe_right]))
        row=output
    assert first['output_epoch']==5 and first['g']==2 and first['output']['age']==2
    assert stages[9]['right_edge_Ages']==[6,6,10,10]
    assert all(s['right_edge_Ages']==[6,6,7,7] for s in stages[10:])
    return dict(epochs=16,retained_frame=[lo,hi],finite_full_F7_local_cofactors=cofactors,
        full_word_signature_sha256=word_signature.hexdigest(),native_signature_sha256=native_signature.hexdigest(),
        first_noncommon_Age=first,stages=stages,frame_margin_and_infinite_line_extension_proved=True),prepared


def supplementary_beta(rom,prepared):
    results=[];flag_reads=0
    for case in prepared:
        tape={k.PRIMARY_START+w:sum(case['raw'][j][w]<<((j+5)*k.WORD) for j in range(-5,6))
            for w in range(k.FRAME_WORDS)}
        projected_tape=k.input_tape(case['projected'])
        actual,ticks,last,trace=k.execute(rom,tape,record=True)
        projected,projected_ticks,projected_last,_=k.execute(rom,projected_tape)
        assert last.mode==projected_last.mode==k.HALT and ticks==projected_ticks
        expected=k.cell_words(case['expected'])
        assert [actual.get(k.PRIMARY_START+w,0) for w in range(k.FRAME_WORDS)]==expected
        assert actual==projected
        reads=[]
        for address,p,np,ow,sw in trace:
            if p.mode==k.SEEK and address==p.target and k.PRIMARY_START+2<=address<=k.PRIMARY_START+5:
                kind=p.args&3;source=(p.args>>10)&3
                if kind==3:flag_reads+=1;reads.append(address-k.PRIMARY_START)
                elif kind==0:assert source==1  # Computed Out, not raw input tape.
                else:assert kind==1  # Native Out store; not an input read.
        results.append(dict(name=case['name'],ticks=ticks,raw_equals_lowbit_projected_execution=True,
            exact_actual_F7_output=True,native_flag_raw_READMASK_offsets=reads,
            raw_words_sha256=hashlib.sha256(json.dumps(case['raw'],sort_keys=True).encode()).hexdigest(),
            output_words_sha256=hashlib.sha256(json.dumps(expected).encode()).hexdigest()))
    return dict(prepared_paired_raw_and_normalized_actual_executions=len(results),
        raw_flag_READMASK_events=flag_reads,records=results,
        comparisons_are_supplementary_not_universal_normalization_proof=True)


def calculate():
    rom,listing,labels,errors=builder.programme().assemble();assert not errors
    assert rom.token_count*9==7902 and len(rom.dictionary)==512
    for inst in listing:
        args=tuple(v&((1<<w)-1) for v,w in zip(inst['operands'],k.ARGS[inst['opcode']]))
        assert k.decode(k.beta_word(rom,inst['address']))==(inst['opcode'],args)
    factor=holder_factor(rom);maps,prepared=stroboscopic(rom)
    beta=supplementary_beta(rom,prepared)
    return dict(all_SF_holder_factor=factor,actual_stroboscopic_map=maps,
        supplementary_emitted_beta_checks=beta,unchanged_own_beta_tokens=rom.token_count,
        total_immutable_code_capacity_bits=59392)


def main():
    started=time.monotonic();source=Path(__file__).parent;directory=ROOT/'figs/gray_counterexamples'
    result=calculate()
    receipt=dict(name='actual GMW7 sixteen gathered native steps on one intact clock real2',
        Q=k.Q,U=k.U,lambda_original=24,c_original=104,checker_sha256=digest(__file__),
        proof_sha256=digest(source/'GMW7_CLOCK_STROBOSCOPIC_NATIVE.md'),
        source_dependencies_sha256={name:digest(source/name) for name in
            ('gray_token_gather_v7.py','build_gray_token_gather_v7.py','gray_moving_word_v2.py',
                'gray_moving_word_kernel.py','GMW7_SINGLE_GATHER_PERIOD.md','GMW7_CLOCK_GATHER_BANK.md',
                'GMW7_WF0_CLOCK_ISLAND.md')},
        receipt_dependencies_sha256={name:digest(directory/name) for name in
            ('GMW7_single_gather_period_certificate.json','GMW7_execution_bound.json',
                'GMW7_prepared_execution_certificate.json','GMW7_clock_gather_bank_certificate.json',
                'GMW7_WF0_clock_island_certificate.json','GMW7_token_beta.bin','GMW7_dictionary.json',
                'GMW7_token_listing.json')},
        root_initializer_source_sha256=digest(initial.__file__),
        root_initializer_proof_sha256=digest(ROOT/'Report/proofs/GMW7_INTACT_HIERARCHY.md'),
        retained_initial_instrumentation_failure_assets_sha256={name:digest(directory/name) for name in
            ('GMW7_stroboscopic_native_initial_checker.py.txt',
                'GMW7_stroboscopic_native_initial_checker_failure.txt')},
        results=result,actual_physical_history_lift_proved_by_factor_gather_programme_commit_contracts=True,
        intact_recursive_start_and_one_shared_actual_original_real2_history=True,
        no_preloaded_bank_or_independent_upper_error_history=True,
        decoded_fifth_Age_failure_for_changed_GMW7_proved=True,
        inside_Flag2_zero_for_first16_actual_evaluations_proved=True,
        actual_Gray_gathering_or_simulated_flag_repair_refinement=False,
        all_time_stroboscopic_recovery_or_iid_or_memory_failure_proved=False,
        active_rule_or_previously_frozen_component_modified=False,
        new_rule_or_schedule_emitted=False,elapsed_seconds=time.monotonic()-started)
    path=directory/'GMW7_clock_stroboscopic_native_certificate.json'
    path.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(groups=result['all_SF_holder_factor']['actual_all_SF_raw_incoherent_group_checks'],
        maps=result['actual_stroboscopic_map']['finite_full_F7_local_cofactors'],
        beta_cases=result['supplementary_emitted_beta_checks']['prepared_paired_raw_and_normalized_actual_executions'],
        first=result['actual_stroboscopic_map']['first_noncommon_Age'],
        receipt_sha256=digest(path),elapsed_seconds=time.monotonic()-started)))


if __name__=='__main__':main()
