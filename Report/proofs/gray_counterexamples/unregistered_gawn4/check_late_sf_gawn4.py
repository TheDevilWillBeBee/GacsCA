"""Exact new-scale supplements for the written late-SF burst proof.

The word/packet/spatial inductions are in GAWN4_LATE_SF_BURST_REPAIR.md.
No rule or inherited asset is generated or modified here.
"""
from pathlib import Path
from dataclasses import replace
from functools import lru_cache
from itertools import product
import hashlib,json,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE.parent/'unregistered_gawn2'));sys.path.insert(0,str(ROOT))
import small_rule_gawn2 as k
import small_compositional_cost as own
from gacsca import gray_errors
OUT=ROOT/'figs/gray_counterexamples/unregistered_gawn4'
SF=('heads','mem','out','info','scratch','program','courier_l','courier_r',
    'mail_l','mail_r','history1','history2','history3')

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def serial(value):return json.loads(json.dumps(value))
def cells_words(cells):return [[x,[hex(v) for v in k.cell_words(c)]] for x,c in sorted(cells.items())]

@lru_cache(None)
def intact_info(y):
    g,a=divmod(y,k.Q);i=a-k.PRIMARY_START
    if not 0<=i<k.FRAME_WORDS:return 0
    if i<6:return g%k.Q if i==0 else 0
    name=k.FIELD_NAMES[(i-6)//5];h=(i-6)%5
    if name=='info':
        assert abs(g+k.SLOTS[h])<abs(y)
        return intact_info(g+k.SLOTS[h])
    if name=='program':return k.beta_bit(own.ROM,(g+k.SLOTS[h])%k.Q)
    return 0

@lru_cache(None)
def H(x):
    return k.Cell(addr=x%k.Q,info=tuple(intact_info(x+s) for s in k.SLOTS),
        program=tuple(k.beta_bit(own.ROM,(x+s)%k.Q) for s in k.SLOTS))

@lru_cache(None)
def C1(x):return k.local_transition({j:H(x+j) for j in range(-8,9)},own.ROM)
@lru_cache(None)
def C2(x):return k.local_transition({j:C1(x+j) for j in range(-8,9)},own.ROM)

def intact_checks():
    info_rows=[6+5*k.FIELD_NAMES.index('info')+h for h in range(5)]
    assert info_rows==list(range(206,211))
    assert min(k.PRIMARY_START+i for i in info_rows)==2006
    coordinates=(-10**12,-k.Q**3,-k.Q,-9,-2,-1,0,1,2,9,k.Q,k.Q**3,10**12)
    field_cases=holder_cases=coherent_cases=0
    for g in coordinates:
        record=k.cell_words(H(g))
        for i,value in enumerate(record):
            y=g*k.Q+k.PRIMARY_START+i
            assert intact_info(y)==value;field_cases+=1
            for h,s in enumerate(k.SLOTS):
                assert H(y-s).info[h]==value;holder_cases+=1
        for a in (0,3,k.Q-3,k.Q-1):assert intact_info(g*k.Q+a)==0
    for y in range(-12,13):
        native=C1(y)
        assert (native.addr,native.age,native.f1,native.f2,native.wf1,native.wf2)==(y%k.Q,1,0,0,0,0)
        for name in SF:
            values=[getattr(C1(y-s),name)[h] for h,s in enumerate(k.SLOTS)]
            assert len(set(values))==1;coherent_cases+=1
    return dict(field_cases=field_cases,holder_cases=holder_cases,all13_upper_C1_holder_cases=coherent_cases,
        coordinates=list(coordinates),recursive_info_rows=info_rows,minimum_recursive_absolute_coordinate=2006)

def endpoints():
    seek_count=run_count=invalid_count=0
    def check(p,a):
        nonlocal invalid_count
        result,ow,sw=k.step_packet(p,a,0,k.MASK,k.MASK,k.MASK,own.ROM)
        assert result.move in (0,1,2)
        assert not (a==0 and result.move==2) and not (a==k.Q-1 and result.move==1)
        return result
    for a in (0,k.Q-1):
        for target in range(k.Q):
            check(k.Packet(p=k.MASK,move=1,mode=k.SEEK,target=target,args=1,regs=(k.MASK,)*16),a)
            seek_count+=1
        for pc in range(k.CODE_CAPACITY):
            for v in (0,k.Q-1,k.Q,k.MASK):
                check(k.Packet(p=k.MASK,mode=k.RUN,pc=pc,regs=(v,)*16),a);run_count+=1
        for move,mode,pc,target in product((0,1,2,3,k.MASK),(0,1,2,3,4,k.MASK),
            (0,k.Q-1,k.Q,k.MASK),(0,k.Q-1,k.Q,k.MASK)):
            check(k.Packet(p=k.MASK,move=move,mode=mode,pc=pc,target=target,args=k.MASK,regs=(k.MASK,)*16),a)
            invalid_count+=1
    return dict(all4096_SEEK_targets_at_both_endpoints=seek_count,
        all4096_immutable_RUN_words_times4_boundary_operand_classes_times2_endpoints=run_count,
        selected_invalid_metadata_endpoint_cases=invalid_count,
        universal_target_inequality_argument_in_written_proof=True)

def quiet_pair_checks():
    phases=sorted({0,1,2,3,4,5,k.Q-5,k.Q-4,k.Q-3,k.Q-2,k.Q-1})
    native_cases=full_cases=0
    for a in phases:
        for start in range(-6,6):
            for p1,p2 in product(range(16),repeat=2):
                cells={j:dict(addr=(a+j)%k.Q,age=1,f1=0,f2=0,wf1=0,wf2=0) for j in range(-5,6)}
                for j,value in zip((start,start+1),(p1,p2)):
                    if j in cells:
                        cells[j].update(addr=(a+j+1)%k.Q,age=k.U-1,
                            **{name:(value>>h)&1 for h,name in enumerate(('f1','f2','wf1','wf2'))})
                actual=k.scalar_native(cells)
                assert actual==dict(addr=a,age=2,f1=0,f2=0,wf1=0,wf2=0)
                native_cases+=1
    for av,bv in product((0,1,1<<99,k.MASK),repeat=2):
        bad={}
        for j,v in zip((0,1),(av,bv)):
            words=[v]*k.FRAME_WORDS
            bad[j]=k.project(k.cell_from_words(words))
        for x in range(-8,10):
            neighborhood={j:bad.get(x+j,C1(x+j)) for j in range(-8,9)}
            actual=k.local_transition(neighborhood,own.ROM)
            assert k.cell_words(actual)==k.cell_words(C2(x));full_cases+=1
    return dict(exhaustive_two_site_flag_payload_cases_at_selected_Address_classes=native_cases,
        selected_all496_word_full_kernel_pair_cases=full_cases,
        GF_Age_and_whole_SF_value_quantifiers_proved_by_three_correct_word_argument=True)

def bank(y):return sum(intact_info(y+j*k.Q)<<((j+8)*k.WORD) for j in range(-8,9))
def trace_digest(trace):
    h=hashlib.sha256()
    for address,oldp,newp,ow,sw in trace:
        row=(address,k.pack(oldp),k.pack(newp),ow,sw)
        h.update((json.dumps(row,separators=(',',':'))+'\n').encode())
    return h.hexdigest()

def execution(tape,early=False):
    out,ticks,p,trace=k.execute(own.ROM,tape,record=True,early=early)
    assert p.mode==k.HALT and ticks<=(221 if early else 104572)
    assert all(k.PRIMARY_START<=r[0]<k.PRIMARY_START+k.FRAME_WORDS for r in trace)
    scratch={r[0]:r[4] for r in trace if r[4] is not None}
    return out,ticks,p,trace,scratch

def witness():
    tape=k.input_tape({j:H(j) for j in range(-8,9)})
    assert all(tape[y]==bank(y) for y in tape)
    early,et,ep,etr,es=execution(tape,early=True)
    assert [early[k.PRIMARY_START+i] for i in range(6)]==[0,1,0,0,0,0]
    out,ticks,p,trace,scratch=execution(tape)
    expected=k.cell_words(C1(0))
    assert [out[k.PRIMARY_START+i] for i in range(k.FRAME_WORDS)]==expected
    assert set(out)==set(range(k.PRIMARY_START,k.PRIMARY_START+k.FRAME_WORDS))
    final_address=trace[-1][0]
    def rest(x):
        return k.Cell(addr=x%k.Q,age=k.U-1,
            heads=tuple(k.pack(p) if x+s==final_address else 0 for s in k.SLOTS),
            mem=tuple(bank(x+s) for s in k.SLOTS),
            out=tuple(out.get(x+s,0) for s in k.SLOTS),
            info=tuple(intact_info(x+s) for s in k.SLOTS),
            scratch=tuple(scratch.get(x+s,0) for s in k.SLOTS),
            program=tuple(k.beta_bit(own.ROM,(x+s)%k.Q) for s in k.SLOTS),
            history1=tuple(bank(x+s) for s in k.SLOTS),
            history2=tuple(bank(x+s) for s in k.SLOTS),
            history3=tuple(bank(x+s) for s in k.SLOTS))
    target=k.PRIMARY_START;state={x:rest(x) for x in range(target-24,target+25)}
    noisy=dict(state);replacements=[]
    for h,s in enumerate(k.SLOTS):
        x=target-s;old=state[x];values=list(old.out);assert values[h]==0;values[h]=1<<99
        noisy[x]=replace(old,out=tuple(values))
        replacements.append(dict(x=x,t=k.U-1,slot=h,old_words=[hex(v) for v in k.cell_words(old)],
            replacement_words=[hex(v) for v in k.cell_words(noisy[x])]))
    support={(target-s,k.U-1) for s in k.SLOTS}
    classified=gray_errors.classify(support,support,Q=k.Q,U=k.U,sep=104)
    assert classified['level0']==0 and classified['level1']
    clean_commit={};noisy_commit={};changed=[]
    for x in range(target-16,target+17):
        clean=k.local_transition({j:state[x+j] for j in range(-8,9)},own.ROM)
        actual=k.local_transition({j:noisy[x+j] for j in range(-8,9)},own.ROM)
        clean_commit[x]=clean;noisy_commit[x]=actual
        if clean!=actual:changed.append(x)
        assert (actual.addr,actual.age,actual.f1,actual.f2,actual.wf1,actual.wf2)==(x%k.Q,0,0,0,0,0)
        for name in SF:
            if name not in ('info','program'):assert getattr(actual,name)==(0,)*5
        for h,s in enumerate(k.SLOTS):
            expected_word=1<<99 if x+s==target else out.get(x+s,0)
            assert actual.info[h]==expected_word
    assert changed==list(range(target-2,target+3))
    raw_record=list(expected);assert raw_record[0]==0;raw_record[0]=1<<99
    assert k.cell_words(k.project(k.cell_from_words(raw_record)))==expected
    raw_upper={j:k.cell_from_words(raw_record) if j==0 else C1(j) for j in range(-8,9)}
    second_tape=k.input_tape(raw_upper)
    second_early,seticks,sep,setrace,ses=execution(second_tape,early=True)
    second,st,sp,strace,ss=execution(second_tape)
    expected2=k.cell_words(C2(0))
    assert [second[k.PRIMARY_START+i] for i in range(k.FRAME_WORDS)]==expected2
    assert [second_early[k.PRIMARY_START+i] for i in range(6)]==expected2[:6]
    return dict(name='actual GAWN2 intact late SF-only malformed-native-padding original-real1',
        Q=k.Q,U=k.U,target=target,error_support=sorted([list(v) for v in support]),
        original_c104_error_classification=classified,replacements=replacements,
        actual_H2_first_bank=[hex(tape[y]) for y in range(k.PRIMARY_START,k.PRIMARY_START+k.FRAME_WORDS)],
        first_early_updates=et,first_full_updates=ticks,first_final_address=final_address,
        first_final_packet=hex(k.pack(p)),first_out=[[y,hex(v)] for y,v in sorted(out.items())],
        first_scratch=[[y,hex(v)] for y,v in sorted(scratch.items())],first_trace_sha256=trace_digest(trace),
        prefix_and_global_exterior_derived_by_frozen_physical_period_proof=True,
        pre_error_raw_cone=cells_words(state),clean_commit_cone=cells_words(clean_commit),
        noisy_commit_cone=cells_words(noisy_commit),changed_raw_commit_sites=changed,
        derived_raw_upper_record=[hex(v) for v in raw_record],pi2_record_equals_actual_clean_C1=True,
        second_actual_raw_bank=[hex(second_tape[y]) for y in range(k.PRIMARY_START,k.PRIMARY_START+k.FRAME_WORDS)],
        second_early_updates=seticks,second_full_updates=st,second_out=[[y,hex(v)] for y,v in sorted(second.items())],
        second_final_packet=hex(k.pack(sp)),second_trace_sha256=trace_digest(strace),
        complete2U_recovery_from_universal_derived_D_encoding_composition=True,
        arbitrary_burst_quantifier_from_selected_execution=False,Gray_or_iid_counterexample=False)

def compute(write=False):
    started=time.monotonic();intact=intact_checks();shield=endpoints();pair=quiet_pair_checks();actual=witness()
    result=dict(name='GAWN4 unchanged GAWN2 late SF burst contracts',Q=k.Q,U=k.U,
        maximum_spatial_width=104,fault_first_row=k.LATE_BIRTH+1,fault_last_row=k.U-1,
        native_replacement_allowed=False,intact=intact,endpoint_shield=shield,quiet_pair=pair,
        actual_witness=dict(error_support=actual['error_support'],first_full_updates=actual['first_full_updates'],
            second_full_updates=actual['second_full_updates'],first_early_updates=actual['first_early_updates'],
            second_early_updates=actual['second_early_updates'],changed_raw_commit_sites=actual['changed_raw_commit_sites']),
        same_rule_ROM_constants_unchanged=True,general_real1_higher_iid_memory_minimum_proved=False)
    if write:
        OUT.mkdir(parents=True,exist_ok=True)
        for name,value in (('GAWN4_late_SF_contracts.json',result),('GAWN4_actual_padding_witness.json',actual)):
            path=OUT/name;assert not path.exists(),'never overwrite receipts';path.write_text(json.dumps(serial(value),indent=2)+'\n')
    else:
        assert serial(result)==json.loads((OUT/'GAWN4_late_SF_contracts.json').read_text())
        assert serial(actual)==json.loads((OUT/'GAWN4_actual_padding_witness.json').read_text())
    print(json.dumps(dict(passed=True,contracts=result,seconds=time.monotonic()-started)),flush=True)
    return result

if __name__=='__main__':compute(write=True)
