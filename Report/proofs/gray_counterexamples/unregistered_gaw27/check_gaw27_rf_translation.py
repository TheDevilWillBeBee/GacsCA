"""Conditional native RF-template renewal, not future actual source supply.

The all-row event equality ties one instance to the actual fifth pulse.
The companion proof supplies integer-Q translation and the left barrier.
"""
from pathlib import Path
import hashlib,json,struct,sys,time
import check_gaw27_actual_fifth_native as actual
S=Path(__file__).resolve().parent;ROOT=S.parents[3];D=actual.D
Q=actual.Q;U=actual.U
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read(path):
    data=path.read_bytes();pos=0;rows=[]
    while pos<len(data):
        row,n,ns=struct.unpack_from('<iii',data,pos);pos+=12
        z=struct.unpack_from('<'+'i'*(3*n+2*ns),data,pos);pos+=4*len(z)
        rows.append((row,[list(z[3*i:3*i+3]) for i in range(n)],
            {z[3*n+2*i]:z[3*n+2*i+1] for i in range(ns)}))
    assert pos==len(data) and rows[0][0]==0 and rows[-1][0]==U
    return rows
def main():
    start=time.monotonic();issue='--issue' in sys.argv
    rows=read(D/'GAW27_RF_template_native_events01.bin')
    shadow=read(D/'GAW27_fifth_native_pulse_events01.bin')
    audit=json.loads((D/'GAW27_RF_template_native_audit_issue01.log').read_text())
    assert audit['passed'] and audit['exact_final_native_segments']==rows[-1][1]
    assert rows[0][1]==[[0,Q//2,2],[Q//2,7*Q//2,1],[7*Q//2,4*Q,3]]
    assert rows[-1][1]==[[3*Q,7*Q//2,2],[7*Q//2,13*Q//2,1],[13*Q//2,7*Q,3]]
    expected=sorted([g*Q+Q//2-3 for g in range(1,4)]+[(g+1)*Q-3 for g in range(4,7)])
    assert sorted(rows[0][2])==expected and all(v==0 for v in rows[0][2].values())
    # The canonical five cells at the left cut remain canonical on every
    # old/new row. Their in-colony native windows exclude any external WF;
    # right-front counts use only positive offsets, never external F1.
    assert all(all(not v&1 or a>=Q//2 for a,b,v in seg) for row,seg,src in rows)
    assert all(all(not v&2 or a>=0 for a,b,v in seg) for row,seg,src in rows)
    cursor=0;cut=25*Q;dig=hashlib.sha256()
    for row,seg,src in shadow:
        while cursor+1<len(rows) and rows[cursor+1][0]<=row:cursor+=1
        tr,ts,tb=rows[cursor]
        crop=[[max(a,cut)-cut,b-cut,v] for a,b,v in seg if b>cut]
        assert crop==ts,(row,tr,crop,ts)
        assert {p-cut:v for p,v in src.items() if p>=cut}==tb
        dig.update(json.dumps([row,crop,tb],sort_keys=True,separators=(',',':')).encode())
    # Supplementary actual scalar cofactors for the proved left barrier.
    # Arbitrary omitted left F1/WF1 do not enter the native result at k=0..4.
    k=actual.k;checks=0;digest=hashlib.sha256()
    for x in range(5):
        for bits in range(2048):
            for which in ('f1','wf1'):
                c={j:k.Cell(addr=(x+j)%Q,age=123,f1=(j+5)%2,wf1=int(j>0 and j%3==0)) for j in range(-8,9)}
                base=k.native_at(c)
                for j in range(-5,6):
                    if x+j<0:
                        f={'addr':(x+j)%Q,'age':123,'f1':c[j].f1,'wf1':c[j].wf1}
                        f[which]=(bits>>(j+5))&1;c[j]=k.Cell(**f)
                got=k.native_at(c);assert got==base,(x,bits,which)
                digest.update(json.dumps([x,bits,which,got],sort_keys=True,separators=(',',':')).encode());checks+=1
    # Diagnostic obstruction to declaring the RF-only supply automatic.
    # This is a prepared native bank, not an additional actual history.
    prepared={j:k.Cell(addr=0,age=15,f1=1) for j in range(-8,9)}
    native=k.native_at(prepared)
    assert native==dict(addr=0,age=16,f1=1,f2=1,wf1=0,wf2=0)
    out,ticks,packet,_=k.execute(actual.own.ROM,k.input_tape(prepared),limit=1000,early=True)
    assert packet.mode==k.HALT and [out.get(k.PRIMARY_START+i,0) for i in range(6)]==[0,16,1,1,0,0]
    r=dict(passed=True,Q=Q,U=U,error_lambda=24,error_separation=104,
        same_actual_fifth_pulse_core_all_event_rows_checked=len(shadow),
        normalized_template_event_rows=len(rows),actual_core_trace_sha256=dig.hexdigest(),
        template_native_word_audit=audit,left_barrier_actual_scalar_cofactors=checks,
        left_barrier_cofactor_sha256=digest.hexdigest(),
        left_barrier_universal_equation_proof_in_companion_text=True,
        integer_Q_translation_universal_native_equivariance=True,
        RF_only_template_to_same_template_translated_plus3Q=True,
        core_endpoint_wrongGF_width=7*Q//2,
        actual_fifth_pulse_instantiates_template_at_A25=True,
        arbitrary_earlier_true_right_sources_below_AQ_do_not_change_core=True,
        actual_future_native_bank_and_six_command_renewal_not_proved=True,
        nonzero_future_left_Flag2_commands_not_covered=True,
        prepared_source3_Flag2_birth_diagnostic=dict(native_input_each_lane=[0,15,1,0,0,0],
            six_emitted_outputs=[0,16,1,1,0,0],ticks=ticks,
            old_Flag2_and_Workspace_zero_but_no_GF_quorum=True,
            actual_reachability_in_the_row1_fault_history_not_claimed=True),
        future_persistence_erosion_P5_Gray_iid_shorterU_claim=False,
        template_event_sha256=sha(D/'GAW27_RF_template_native_events01.bin'),
        actual_event_sha256=sha(D/'GAW27_fifth_native_pulse_events01.bin'))
    r=json.loads(json.dumps(r));p=D/'GAW27_conditional_RF_translation_certificate.json'
    if issue:assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n')
    else:assert r==json.loads(p.read_text())
    print(json.dumps(dict(passed=True,seconds=time.monotonic()-start,
        exact_actual_core_rows=len(shadow),conditional_template_rows=len(rows),
        barrier_scalar_cofactors=checks,receipt_sha256=sha(p))),flush=True);return r
if __name__=='__main__':main()
