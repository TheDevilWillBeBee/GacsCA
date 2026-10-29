"""Actual third early native banks/couriers from the proved second boundary.

No extra upper errors and no prescribed commands. SF rows not read by
the native early programme are not assumed clean or replaced by tapes.
"""
from pathlib import Path
import hashlib,json,sys,time
import check_gaw25_physical_late_factor as boundary
import check_gaw25_late_discovery as d
k=d.k;own=d.own;Q=d.Q;U=d.U;P=d.P
S=Path(__file__).resolve().parent;ROOT=S.parents[3];D=d.D
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def blocked(a,b):
    a,b=sorted((a,b))
    return a<29*Q//2 and b>=14*Q or a<23*Q and b>=45*Q//2
def native_bank(origin):
    return [sum((boundary.committed_info(origin+P+i+v*Q) if not v or not blocked(origin+P+i,origin+P+i+v*Q) else 0)<<((v+8)*100) for v in range(-8,9)) for i in range(6)]
def run(g,foreign):
    origin=g*Q-Q//2 if foreign else g*Q;rows=native_bank(origin)
    out,ticks,p,trace=k.execute(own.ROM,{P+i:v for i,v in enumerate(rows)},limit=213,record=True,early=True)
    assert p.mode==k.HALT and ticks<=213
    cells={v:k.Cell(**dict(zip(k.NATIVE_NAMES,[(w>>((v+8)*100))&k.MASK for w in rows]))) for v in range(-8,9)}
    assert all(0<=getattr(c,n)<limit for c in cells.values() for n,limit in zip(k.NATIVE_NAMES,(Q,U,2,2,2,2)))
    expected=k.native_at(cells);values=[out.get(P+i,0) for i in range(6)]
    assert values==[expected[n] for n in k.NATIVE_NAMES]
    assert values[4:]==[0,0]
    reads=set();dig=hashlib.sha256()
    for address,old,new,ow,sw in trace:
        assert P<=address<=P+5 and sw is None
        if old.mode==k.SEEK and address==old.target:
            kind=old.args&3;source=(old.args>>11)&3
            if kind in (2,3) or(kind==0 and source==0):reads.add(address)
            if kind==0:assert source==0
        dig.update(json.dumps([address,hex(k.pack(new)),ow,sw],separators=(',',':')).encode())
    assert reads==set(range(P,P+6))
    return dict(receiver=g,foreign=foreign,physical_origin=origin,
        actual_six_native_bank_rows_all100bits=[hex(w) for w in rows],actual_early_six_outputs=values,
        actual_native_Age_lanes=[(rows[1]>>((v+8)*100))&k.MASK for v in range(-8,9)],
        ticks=ticks,HALT=True,input_other490_rows_unread_not_selected=True,
        trace_sha256=dig.hexdigest())
def main():
    started=time.monotonic();issue='--issue' in sys.argv
    runs=[run(g,False) for g in (*range(-18,15),*range(23,39))]
    runs.extend(run(g,True) for g in range(15,24))
    true_on=[r['receiver'] for r in runs if not r['foreign'] and r['actual_early_six_outputs'][2]]
    foreign_on=[r['receiver'] for r in runs if r['foreign'] and r['actual_early_six_outputs'][2]]
    left_on=[r for r in runs if r['actual_early_six_outputs'][3]]
    def origin(row):return row['physical_origin']
    right_seeds=[origin(r)+P+2 for r in runs if r['actual_early_six_outputs'][2]]
    left_seeds=[origin(r)+P+3 for r in left_on]
    def forward(seeds,direction):
        active=set(seeds);first={}
        for tick in range(1,5*Q):
            nxt=set();candidates=active|{y+direction for y in active}
            for y in candidates:
                q=d.addr(y);dest=Q-3 if direction==1 else 3
                bit=(y in active or y-direction in active) if q==dest else y-direction in active
                lo,hi=(P+2,Q-3) if direction==1 else (3,P+3)
                if lo<=q<=hi and bit:
                    nxt.add(y)
                    if q==dest:first.setdefault(y,tick)
            active=nxt
        assert all(d.addr(y)==(Q-3 if direction==1 else 3) for y in active)
        return sorted(active),max(first.values(),default=0)
    right_sources,right_max=forward(right_seeds,1)
    left_sources,left_max=forward(left_seeds,-1)
    sourcefile=D/'GAW25_derived_actual_third_F1_sources.txt';text=''.join(str(p)+'\n' for p in right_sources)
    leftfile=D/'GAW25_derived_actual_third_F2_sources.txt';lefttext=''.join(str(p)+'\n' for p in left_sources)
    if issue:
        assert not sourcefile.exists() and not leftfile.exists();sourcefile.write_text(text);leftfile.write_text(lefttext)
    else:assert sourcefile.read_text()==text and leftfile.read_text()==lefttext
    r=dict(Q=Q,U=U,error_lambda=24,error_separation=104,
        second_full_boundary_receipt_sha256=sha(D/'GAW25_full_2U_physical_certificate.json'),
        same_original_shared_row1_GF_only_real2_and_no_future_errors=True,
        actual_fixed_native_prefix_all_three_third_period_gathers_equal=True,
        complete_actual_third_native_early_banks_and_executions=runs,
        actual_true_positive_Flag1_heads=true_on,actual_foreign_positive_Flag1_heads=foreign_on,
        actual_early_WF_output_words_zero=True,actual_positive_Flag2_receivers=[(r['receiver'],r['foreign']) for r in left_on],
        no_common_upper_Age_assumed_actual_native_lanes_retained=True,
        partial_true14_foreign23_right_courier_lineages_blocked_by_actual_GF_guard=True,
        actual_right_max_first_arrival=right_max,actual_left_max_first_arrival=left_max,
        actual_nonzero_right_sources_at2U_plus80Q_minus1=right_sources,
        actual_nonzero_left_sources_at2U_plus80Q_minus1=left_sources,actual_all_left_sources_zero=not left_sources,source_file_sha256=sha(sourcefile),left_source_file_sha256=sha(leftfile),
        actual_third_native_pulse_and3U_boundary_not_yet_certified=True,
        full_late3U_encoding_higher_Gray_P5_iid_or_shorter_U_claim=False)
    r=json.loads(json.dumps(r));path=D/'GAW25_actual_third_sources_certificate.json'
    if issue:assert not path.exists();path.write_text(json.dumps(r,indent=2)+'\n')
    else:assert r==json.loads(path.read_text())
    print(json.dumps(dict(passed=True,elapsed_seconds=time.monotonic()-started,
        actual_early_runs=len(runs),actual_right_sources=len(right_sources),actual_left_sources=len(left_sources),receipt_sha256=sha(path))),flush=True);return r
if __name__=='__main__':main()
