"""Actual intact-start three-record Info-majority counterexample.

This refutes only the proposed three-record extension of GAW21's
one-period contraction in unchanged, explicitly non-Gray GAW2R.
Every state follows from one Info-only row at U; no future tape is chosen.
"""
from pathlib import Path
from functools import lru_cache
from dataclasses import replace
import hashlib,json,sys,time
import check_gaw21_two_raw_records as contract
k=contract.k;own=contract.own;S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw21'
sys.path.insert(0,str(S.parent/'unregistered_gaw4'))
import check_gaw4_real1_mail as base
sys.path.insert(0,str(ROOT))
from gacsca import gray_errors
RECORDS=(-1,0,1);P=k.PRIMARY_START
INDICES={g:k.FIELD['info']+k.SLOTS.index(-g) for g in RECORDS}
PRIMARIES={g:g*k.Q+P+INDICES[g] for g in RECORDS}

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def canonical(x):return json.loads(json.dumps(x))
@lru_cache(None)
def oldwords(g):return tuple(k.cell_words(base.nextH(g)))
@lru_cache(None)
def words(g):
    w=list(oldwords(g))
    if g in RECORDS:assert w[INDICES[g]]==0;w[INDICES[g]]=1
    return tuple(w)
@lru_cache(None)
def upper(g):return k.cell_from_words(words(g))
@lru_cache(None)
def successor(g):return k.local_transition({j:upper(g+j) for j in range(-8,9)},own.ROM)
@lru_cache(None)
def data(y):
    g,a=divmod(y,k.Q);i=a-P
    return words(g)[i] if 0<=i<k.FRAME_WORDS else 0
@lru_cache(None)
def encoded(x):
    return k.Cell(addr=x%k.Q,info=tuple(data(x+s) for s in k.SLOTS),
        program=tuple(k.beta_bit(own.ROM,(x+s)%k.Q) for s in k.SLOTS))
@lru_cache(None)
def bank(y):return sum(data(y+d*k.Q)<<((d+8)*k.WORD) for d in range(-8,9))

def actual_errors():
    cells=sorted({primary-s for primary in PRIMARIES.values() for s in k.SLOTS})
    payload=[]
    for x in cells:
        before=base.encoded(x,base.nextH);after=encoded(x)
        assert before!=after and replace(before,info=after.info)==after
        assert all(old^new in (0,1) for old,new in zip(before.info,after.info))
        assert sum(old!=new for old,new in zip(before.info,after.info))==1
        payload.append(dict(site=x,tick=k.U,old_full496_words=[hex(w) for w in k.cell_words(before)],
            replacement_full496_words=[hex(w) for w in k.cell_words(after)]))
    assert len(cells)==15
    # Complete actual shared history E, not classifications in isolation.
    support=[(x,k.U) for x in cells]
    assert not gray_errors.level0_points(support)
    full=gray_errors.classify(support,Q=k.Q,U=k.U,sep=104)
    assert not full['candidate_level1'] and not full['level1']
    clusters=[]
    for g,primary in PRIMARIES.items():
        group={(primary-s,k.U) for s in k.SLOTS}
        classified=gray_errors.classify(group,E=support,Q=k.Q,U=k.U,sep=104)
        assert classified['candidate_level1'] and not classified['level1']
        assert gray_errors.linked(group,set(support)-group,24*k.Q,24*k.U)
        clusters.append(dict(record=g,primary=primary,points=sorted(group),classification=classified))
    diameter=max(cells)-min(cells);assert diameter==2*k.Q+3 and diameter<24*k.Q
    # Any nonempty proper subset fails original real1 isolation because
    # every pair in this one row is (<24Q,<24U)-linked. WholeE failsi.
    assert len(support)==15 and diameter+1>k.Q
    assert diameter<104*k.Q and diameter+1<k.Q*k.Q
    r=dict(error_row=k.U,points=len(support),support=sorted(support),full_whole_cell_payloads=payload,
        every_location_genuinely_changed=True,only_one_actual_Info_bit_changed_per_cell=True,
        shared_E0_points=0,shared_actual_E1_points=0,
        full_level1_classification=full,candidate1_clusters=clusters,
        proper_subset_real1_isolation_excluded_by_all_pair_diameter=[diameter,0],
        level1_isolation_threshold=[24*k.Q,24*k.U],
        candidate2_box=[k.Q*k.Q,k.U*k.U],
        candidate2_linked_candidate1_clusters=2,
        condition_iii_candidate2_all_subset_diameter_bound=[diameter,0],
        condition_iii_threshold=[104*k.Q,104*k.U],
        condition_iv_empty_external_error_history=True,
        exact_original_c104_class='one actual real2; no actual E0/E1 points',
        single_real1_counterexample=False)
    return canonical(r)

def main():
    started=time.monotonic();fault=actual_errors();host=[];different=[];input_records=[]
    for g in RECORDS:
        w=words(g);old=oldwords(g)
        assert [i for i,(x,y) in enumerate(zip(w,old)) if x!=y]==[INDICES[g]]
        input_records.append(dict(location=g,changed_Info_copy_index=INDICES[g],
            old_full496_words=[hex(v) for v in old],raw_full496_words=[hex(v) for v in w]))
    # The whole one-step upper radius8 cone is[-9,9]. At Age2 only Info
    # uses the changed raw track: Mail shifts its separate OLD mail,
    # History holds, sources/commit/birth guards are closed. Thus the
    # written logical-group calculation proves no exterior discrepancy.
    for g in range(-9,10):
        got=k.cell_words(successor(g));expected=k.cell_words(base.next2H(g))
        changes=[i for i,(a,b) in enumerate(zip(got,expected)) if a!=b]
        if -2<=g<=2:
            idx=k.FIELD['info']+k.SLOTS.index(-g)
            assert changes==[idx] and got[idx]==1 and expected[idx]==0
            different.append(g)
        else:assert not changes
        assert successor(g).f1==successor(g).f2==successor(g).wf1==successor(g).wf2==0
        host.append(dict(receiver=g,changed_normal_indices=changes,output_words=[hex(v) for v in got]))
    assert different==[-2,-1,0,1,2]
    # Actual banks are derived from faulted Info, then frozen interpreter
    # executes them. These do not prescribe a future Head or command.
    emitted=[]
    for g in range(-3,4):
        tape={P+i:bank(g*k.Q+P+i) for i in range(k.FRAME_WORDS)}
        outputs=[]
        for early in (True,False):
            out,ticks,packet,trace=k.execute(own.ROM,tape,limit=147455,record=True,early=early)
            assert packet.mode==k.HALT and ticks<=(213 if early else 141557)
            n=6 if early else k.FRAME_WORDS
            got=[out.get(P+i,0) for i in range(n)];expected=k.cell_words(successor(g))[:n]
            assert got==expected,(g,early)
            if early:assert got[2:4]==[0,0]
            assert all(P<=address<P+k.FRAME_WORDS for address,*_ in trace)
            dig=hashlib.sha256()
            for address,oldp,newp,ow,sw in trace:
                dig.update(json.dumps([address,hex(k.pack(oldp)),hex(k.pack(newp)),ow,sw],separators=(',',':')).encode())
            outputs.append(dict(early=early,updates=ticks,HALT=True,head_range=[min(x[0] for x in trace),max(x[0] for x in trace)],
                output_words=[hex(v) for v in got],trace_sha256=dig.hexdigest()))
        emitted.append(dict(receiver=g,derived_actual_full496x17_bank=[hex(tape[P+i]) for i in range(k.FRAME_WORDS)],executions=outputs))
    # The legal global period theorem applies literally to W: native
    # fields retain legal values, every SF WORD100 pattern is legal.
    assert all(words(g)[:6]==oldwords(g)[:6] for g in RECORDS)
    assert all([c['executions'][0]['output_words'][i] for i in (2,3)]==['0x0','0x0'] for c in emitted)
    r=dict(Q=k.Q,U=k.U,error_lambda=24,error_separation=104,
        baseline_upper='C=R(H), actual intact physical rowU is E(C,0)',
        fault=fault,three_raw_records=input_records,
        host_all_affected_radius8_outputs=host,actual_bank_emitted_executions=emitted,
        all_record_native_words_legal_no_projection_or_malformed_compiler_extension=True,
        early_repair_flags0_derived_from_actual_faulted_banks=True,
        actual_three_gather_temporal_vote_courier_reset_and_commit_lift_from_frozen_legal_global_period=True,
        actual_complete_boundary_at2U='E(R(W),0)',clean_complete_boundary_at2U='E(R^2(H),0)',
        changed_decoded_normal_record_indices=different,
        three_record_one_period_contraction_identity=False,
        changed_decoded_records_cannot_fit_any_fixed_adjacent_pair=True,
        illegal_decoded_padding_records=False,
        general_operational_real2_repair_or_eventual_memory_failure_claim=False,
        faithful_Gray_counterexample_iid_reliability_failure_or_shorter_U=False,
        no_rule_ROM_or_accepted_assets_modified=True,
        inherited_legal_period_proof_scope_used_without_extension=True)
    r=canonical(r);p=D/'GAW21_three_record_witness_certificate.json'
    if '--issue' in sys.argv:assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n')
    else:assert r==json.loads(p.read_text())
    print(json.dumps(dict(passed=True,elapsed_seconds=time.monotonic()-started,
        fault_points=fault['points'],class_original_c104=fault['exact_original_c104_class'],
        damaged_decoded_normal_records=different,late_ticks=[v['executions'][1]['updates'] for v in emitted],
        receipt_sha256=sha(p))),flush=True);return r

if __name__=='__main__':main()
