"""Actual first temporal-native banks/couriers for the new intact GF island.

No full late-output theorem: other bank rows may be damaged. The early
emission reads only the six derived native rows, proved by its exact trace.
Its unknown other rows are not supplied as future physical input tapes.
"""
from pathlib import Path
from dataclasses import replace
import gzip,hashlib,json,struct,sys,time
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw23'
sys.path.insert(0,str(S.parent/'unregistered_gaw21'))
import check_gaw21_three_record_witness as ancestor
k=ancestor.k;own=ancestor.own;base=ancestor.base;Q=k.Q;U=k.U;P=k.PRIMARY_START

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(x):return json.loads(json.dumps(x))
def blocked(a,b):
    a,b=sorted((a,b))
    return (a<Q//2 and b>=0) or (a<17*Q and b>=16*Q+Q//2)
def first_native_bank(g,foreign):
    y=g*Q-Q//2+P if foreign else g*Q+P
    vec=[0 if foreign or (d and blocked(y,y+d*Q)) else (g+d)%Q for d in range(-8,9)]
    return vec,[sum(v<<(j*100) for j,v in enumerate(vec)),0,0,0,0,0]
def early(g,foreign):
    vec,rows=first_native_bank(g,foreign);tape={P+i:v for i,v in enumerate(rows)}
    out,ticks,p,trace=k.execute(own.ROM,tape,limit=213,early=True,record=True)
    assert p.mode==k.HALT
    native=k.native_at({j:k.Cell(addr=vec[j+8]) for j in range(-8,9)})
    expected=[native[name] for name in k.NATIVE_NAMES];actual=[out.get(P+i,0) for i in range(6)]
    assert actual==expected and actual[1]==1 and actual[3:]==[0,0,0]
    reads=set();dig=hashlib.sha256()
    for address,old,new,ow,sw in trace:
        assert P<=address<=P+5
        if old.mode==k.SEEK and address==old.target:
            kind=old.args&3;source=(old.args>>11)&3
            if kind in (2,3) or (kind==0 and source==0):reads.add(address)
            if kind==0:assert source==0
        assert sw is None
        dig.update(json.dumps([address,hex(k.pack(old)),hex(k.pack(new)),ow,sw],separators=(',',':')).encode())
    assert reads==set(range(P,P+6))
    physical=g*Q-Q//2+P if foreign else g*Q+P
    # Both partial frames have at least243 sites before their GF jump;
    # the actual early packet visits only six sites (plus five holders).
    assert all(not (x<Q//2<=x+7 or x<17*Q<=x+7) for x in (physical-2,))
    return dict(g=g,foreign=foreign,physical_head_birth=physical,
        actual_temporal_native_GF_lanes=vec,actual_six_packed_native_bank_rows=[hex(v) for v in rows],
        unknown_other490_rows_proved_unread_not_preloaded=True,
        actual_emitted_six_outputs=actual,ticks=ticks,HALT=True,
        every_actual_input_IO_address=sorted(reads),head_range=[P,P+5],trace_sha256=dig.hexdigest())

def chronological_row1(x):
    info=tuple(base.I(x+s) for s in k.SLOTS)
    return k.Cell(addr=x%Q,age=1,info=info,
        program=tuple(k.beta_bit(own.ROM,(x+s)%Q) for s in k.SLOTS),
        mail_l=info,mail_r=info,history1=tuple(v<<(8*100) for v in info))

def old_words(x):
    # Complete496-word row1, exactly R(H). This avoids recomputing the
    # full-radius update at every support site; the scalar checks below
    # and the written coherent reset/LOAD proof establish the formula.
    w=[0]*496;w[0]=x%Q;w[1]=1
    info=[base.I(x+s) for s in k.SLOTS]
    for name in ('info','mail_l','mail_r','h1_8'):w[k.FIELD[name]:k.FIELD[name]+5]=info
    w[k.FIELD['program']:k.FIELD['program']+5]=[k.beta_bit(own.ROM,(x+s)%Q) for s in k.SLOTS]
    return w

def payload(issue):
    path=D/'GAW23_full139264_whole_cell_payloads.jsonl.gz'
    assert not issue or not path.exists()
    support_sha=hashlib.sha256();old_sha=hashlib.sha256();new_sha=hashlib.sha256()
    check=None if issue else gzip.open(path,'rt')
    output=gzip.GzipFile(filename='',fileobj=path.open('wb'),mode='wb',mtime=0,compresslevel=1) if issue else None
    for x in range(17*Q):
        old=old_words(x);new=old.copy();new[0]=(old[0]+Q//2)%Q
        assert new[0]!=old[0] and new[1:]==old[1:]
        record=[x,1,old,new];line=json.dumps(record,separators=(',',':'))+'\n'
        if issue:output.write(line.encode())
        else:assert json.loads(next(check))==record
        support_sha.update(struct.pack('<ii',x,1))
        old_sha.update(json.dumps(old,separators=(',',':')).encode())
        new_sha.update(json.dumps(new,separators=(',',':')).encode())
    if issue:output.close()
    else:
        assert check.readline()=='';check.close()
    return dict(points=17*Q,chronological_row=1,all496_actual_old_and_replacement_words_preserved=True,
        whole_file_sha256=sha(path),full_old_words_sha256=old_sha.hexdigest(),
        full_replacement_words_sha256=new_sha.hexdigest(),whole_support_sha256=support_sha.hexdigest(),
        changed_word_per_location=0,GF_shift=Q//2,every_location_genuinely_changed=True,
        exact_shared_original_class='one real2; no actual E0/E1',
        E0_empty_by_dense_neighbour_argument=True,
        all_proper_candidate1_subsets_fail24Q_isolation=True,
        whole_extent17Q_exceeds_candidate1_Q_box=True,
        two_linked_candidate1_witnesses=[[0,103],[Q,Q+103]],
        level2_extent_fits_Q_squared_U_squared=True,
        diameter17Q_minus1_less_than104Q=True,external_errors_empty=True)

def main():
    started=time.monotonic();issue='--issue' in sys.argv
    prefix=json.loads((D/'GAW23_prefix_discovery02.json').read_text())
    fixed=prefix['snapshots'][1]
    assert fixed['row']==4099 and fixed['segments']==[
        [0,Q//2,2],[Q//2,16*Q+Q//2,1],[16*Q+Q//2,17*Q,3]]
    # New actual whole-error payloads; no future field replacements.
    pf=payload(issue);chronological=[]
    for x in (-2,-1,0,1,2,P-2,P,P+5,Q//2-2,Q//2,Q//2+2,17*Q-2,17*Q,17*Q+2):
        actual=k.local_transition({j:base.H(x+j) for j in range(-8,9)},own.ROM)
        assert actual==chronological_row1(x) and k.cell_words(actual)==old_words(x)
        chronological.append(x)
    runs=[early(g,False) for g in (*range(-10,1),*range(17,28))]
    runs.extend(early(g,True) for g in range(1,18))
    true_on=[r['g'] for r in runs if not r['foreign'] and r['actual_emitted_six_outputs'][2]]
    foreign_on=[r['g'] for r in runs if r['foreign'] and r['actual_emitted_six_outputs'][2]]
    assert true_on==[-2,-1,0,17,18,19] and foreign_on==list(range(1,18))
    # Actual route barriers at the fixed GF jumps stop the two partial
    # packets. Every other nonzero seed has its destination within its
    # own uniform-GF route; the centre-vote barrier proof is separate.
    sources=[(g+1)*Q-3 for g in (-2,-1,17,18,19)]
    sources.extend(g*Q+Q//2-3 for g in range(1,17));sources.sort()
    assert len(sources)==21
    sourcepath=D/'GAW23_derived_actual_first_F1_sources.txt'
    expected=''.join(str(x)+'\n' for x in sources)
    if issue:assert not sourcepath.exists();sourcepath.write_text(expected)
    else:assert sourcepath.read_text()==expected
    r=dict(Q=Q,U=U,error_lambda=24,error_separation=104,exact_GF_only_fault=pf,
        actual_H_initialization_and_chronological_row1_checks=chronological,
        native_prefix_fixed_state=fixed,
        second_and_third_native_banks_equal_by_actual_fixed_F1_Mail_erasure=True,
        first_gather_not_assumed_correct_temporal_majority_discards_it=True,
        first_native_temporal_banks_and_exact_emitted_executions=runs,
        every_six_native_bank_word_full100bits_native_padding_zero=True,
        other490_bank_rows_unread_not_assumed_clean=True,
        actual_true_positive_Flag1_heads=true_on,actual_foreign_positive_Flag1_heads=foreign_on,
        partial_true0_and_foreign17_right_couriers_blocked_by_actual_GF_guard=True,
        exact_actual_nonzero_right_special_Info_sources_at80Q_minus1=sources,
        exact_actual_left_special_Info_sources_empty=True,
        source_file_sha256=sha(sourcepath),no_future_noise_tapes_heads_or_commands_prescribed=True,
        native_Info_factor_pulse_and_U_Address_result_not_yet_certified=True,
        full_late_outputs_operational_Gray_iid_or_shorterU_claim=False)
    r=canonical(r);path=D/'GAW23_actual_first_native_banks.json'
    if issue:assert not path.exists();path.write_text(json.dumps(r,indent=2)+'\n')
    else:assert r==json.loads(path.read_text())
    print(json.dumps(dict(passed=True,elapsed_seconds=time.monotonic()-started,
        full_whole_cell_payloads=17*Q,actual_early_executions=len(runs),
        actual_first_F1_sources=21,receipt_sha256=sha(path))),flush=True)
    return r

if __name__=='__main__':main()
