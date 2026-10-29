"""NEW third actual late-bank and interacting-head discovery.

All banks and packets derive from the accepted GAW25 actual third native
pulse and unmasked second raw boundary, using the same row1 fault.
Physical majority, commit and exterior composition are certified separately.
"""
from pathlib import Path
from functools import lru_cache
import hashlib,json,struct,sys,time
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw26'
sys.path.insert(0,str(S.parent/'unregistered_gaw25'))
import check_gaw25_physical_late_factor as boundary
import check_gaw25_actual_third_sources as source25
prior=boundary.d.prior
k=prior.k;own=prior.own;base=prior.base;Q=k.Q;U=k.U;P=k.PRIMARY_START
WIDTHS=(Q,U,2,2,2,2)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def masks(path):
    data=path.read_bytes();lo,hi=struct.unpack_from('<ii',data);tags=data[8:]
    assert len(tags)==hi-lo and set(tags)<={0,31}
    return lambda p:tags[p-lo] if lo<=p<hi else 31
PREFIX=masks(D/'GAW26_prefix_Info_masks.bin')
RETAIN=masks(D/'GAW26_retained_H2_H3_masks.bin')
SOURCES=set(map(int,(ROOT/'figs/gray_counterexamples/unregistered_gaw25/GAW25_derived_actual_third_F1_sources.txt').read_text().split()))
def label(p):return int(43*Q//2<=p<26*Q)
def addr(p):return (p+label(p)*Q//2)%Q
def f1(p):return int(21*Q<=p<43*Q//2 or 51*Q//2<=p<26*Q)
@lru_cache(None)
def snap(p):return boundary.committed_info(p) if PREFIX(p) else 0
@lru_cache(None)
def before_commit_info(p):return (1 if p in SOURCES else snap(p)) if RETAIN(p) else 0
@lru_cache(None)
def bank(p):
    if not RETAIN(p):return 0
    return sum((snap(p+d*Q) if not d or not source25.blocked(p,p+d*Q) else 0)<<((d+8)*100) for d in range(-8,9))
@lru_cache(None)
def input_rows(origin):return tuple(bank(origin+P+i) for i in range(k.FRAME_WORDS))
def raw_neighbours(origin):
    rows=input_rows(origin)
    return {d:k.cell_from_words([(w>>((d+8)*100))&k.MASK for w in rows]) for d in range(-8,9)}

def independent(origin,name):
    rows=input_rows(origin);tape={P+i:w for i,w in enumerate(rows)}
    out,ticks,p,trace=k.execute(own.ROM,tape,limit=147455,record=True)
    assert p.mode==k.HALT and ticks<=141557,(name,ticks,p)
    cells=raw_neighbours(origin)
    assert all(0<=getattr(c,n)<limit for c in cells.values() for n,limit in zip(k.NATIVE_NAMES,WIDTHS))
    expected=k.cell_words(k.local_transition(cells,own.ROM));values=[out.get(P+i,0) for i in range(k.FRAME_WORDS)]
    assert values==expected,(name,'selected exact own emission')
    dig=hashlib.sha256();low=high=P;writes=[]
    for address,old,new,ow,sw in trace:
        assert P<=address<P+k.FRAME_WORDS;low=min(low,address);high=max(high,address)
        dig.update(json.dumps([address,hex(k.pack(new)),ow,sw],separators=(',',':')).encode())
        if ow is not None:writes.append((address,hex(ow)))
    return dict(name=name,physical_origin=origin,actual_full496x17_late_bank=[hex(w) for w in rows],
        all_six_native_input_words_legal_unmasked=True,HALT=True,ticks=ticks,
        head_address_range=[low,high],exact_literal_local_R_successor_equal=True,
        actual_output_full496_words=[hex(w) for w in values],actual_store_count=len(writes),
        trace_sha256=dig.hexdigest()),dict(out={origin+a:v for a,v in out.items()},
        packet=p,address=origin+trace[-1][0])

def coupled(origins,names):
    heads={o+P:k.Packet(p=1,pc=0) for o in origins};out={};scratch={}
    births=sorted(heads);dig=hashlib.sha256();collisions=[];writes=[];paths={y:[y,y] for y in births}
    # A packet label is diagnostic only; no lineage is used as a control.
    minpos=min(births);maxpos=max(births);initial_banks={str(o):[hex(w) for w in input_rows(o)] for o in origins}
    entered=set();boundary_events=[]
    for tick in range(1,147456):
        targets={y+(1 if p.move==1 else -1 if p.move==2 else 0) for y,p in heads.items()}
        nextheads={}
        for y in sorted(targets):
            old=[heads.get(y+j,k.ZERO) for j in (-1,0,1)]
            candidates=[p for index,p in enumerate(old) if p.p and
                ((index==1 and p.move not in (1,2)) or (index==0 and p.move==1) or(index==2 and p.move==2))]
            if len(candidates)>1:collisions.append(dict(tick=tick,physical_position=y,
                old_packets=[hex(k.pack(p)) for p in old],candidate_count=len(candidates)))
            p=k.incoming(old)
            p,ow,sw=k.step_packet(p,addr(y),bank(y),out.get(y,0),scratch.get(y,0),k.beta_bit(own.ROM,addr(y)),own.ROM)
            if p.p:nextheads[y]=p;minpos=min(minpos,y);maxpos=max(maxpos,y)
            if ow is not None:out[y]=ow;writes.append((tick,y,hex(ow)))
            if sw is not None:scratch[y]=sw
            if y in (43*Q//2,26*Q):boundary_events.append((tick,y,addr(y),hex(k.pack(p))))
            dig.update(json.dumps([tick,y,hex(k.pack(p)),ow,sw],separators=(',',':')).encode())
        heads=nextheads
        if heads and all(p.mode==k.ERROR and p.move==0 for p in heads.values()):break
    assert heads
    r=dict(names=names,physical_origins=origins,actual_birth_positions=births,
        exact_initial_actual_late_bank_all496x17=initial_banks,
        ticks_followed=tick,last_computed_Age=102*Q+1+tick,
        all_heads_stationary_ERROR_by_last_row=all(p.mode==k.ERROR and p.move==0 for p in heads.values()),
        head_spatial_hull=[minpos,maxpos],collisions=collisions,GF_jump_crossings=boundary_events,
        actual_chronological_Out_stores=writes,
        actual_final_nonzero_Out_words=[[y,hex(v)] for y,v in sorted(out.items()) if v],
        actual_final_all_stored_Out_words=[[y,hex(v)] for y,v in sorted(out.items())],
        actual_final_Scratch_words=[[y,hex(v)] for y,v in sorted(scratch.items())],
        actual_final_Head_packets=[[y,hex(k.pack(p))] for y,p in sorted(heads.items())],
        trace_sha256=dig.hexdigest(),no_forged_future_head_tape_or_extra_error=True,
        logical_majority_to_raw_physical_factor_not_yet_certified=True)
    return r,dict(out=out,heads=heads,scratch=scratch)

def main():
    started=time.monotonic();issue='--issue' in sys.argv
    cases=[];outputs={};works=[]
    # Independent complete frames except the two neighbours coupled to
    # partial frames. Margins support a later infinite-exterior proof.
    for g in (*range(-26,21),*range(27,47)):
        r,w=independent(g*Q,'true%d'%g);cases.append(r);outputs.update(w['out'])
    for g in range(23,26):
        r,w=independent(g*Q-Q//2,'foreign%d'%g);cases.append(r);outputs.update(w['out'])
    left,lw=coupled([21*Q,22*Q-Q//2],['partial_true21','complete_foreign22'])
    right,rw=coupled([26*Q-Q//2,26*Q],['partial_foreign26','complete_true26'])
    assert not set(lw['out'])&set(rw['out'])
    outputs.update(lw['out']);outputs.update(rw['out'])
    windows={}
    for g in range(-26,47):
        windows[str(g)]=[hex(outputs.get(g*Q+P+i,0)) for i in range(k.FRAME_WORDS)]
    r=dict(Q=Q,U=U,error_lambda=24,error_separation=104,
        same_actual_GAW23_row1_GF_only_shared_real2=True,
        retention_mask_discovery=json.loads((D/'GAW26_retained_mask_discovery01.json').read_text()),
        actual_complete_frame_independent_executions=cases,
        actual_coupled_partial_frame_executions=[left,right],
        selected_true_normal_3U_committed_out_words=windows,
        all_future_banks_derived_from_same_history_no_preloading=True,
        physical_majority_and_full_3U_commit_exterior_lift_not_yet_certified=True,
        faithful_Gray_Proposition5_iid_or_shorterU_claim=False)
    r=json.loads(json.dumps(r));p=D/'GAW26_actual_late_discovery01.json'
    if issue:assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n')
    else:assert r==json.loads(p.read_text())
    print(json.dumps(dict(passed=True,elapsed_seconds=time.monotonic()-started,
        independent_executions=len(cases),coupled_cases=2,
        pair_summary=[{a:z[a] for a in ('names','ticks_followed','all_heads_stationary_ERROR_by_last_row','head_spatial_hull','collisions')} for z in (left,right)],
        receipt_sha256=sha(p))),flush=True);return r

if __name__=='__main__':main()
