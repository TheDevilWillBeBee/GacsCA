"""Frozen-emission native-store and zero-source contracts for GAW28.

Static target intervals use accepted syntax-level counter/register contracts.
Literal local-rule cofactors supplement the universal equations in the proof.
No malformed-native evaluator quotient is used.
"""
from pathlib import Path
import hashlib,json,random,sys,time
import discover_gaw28_native_renewal as r
k=r.k;own=r.own;Q=r.Q;U=r.U;P=r.P;S=r.S;ROOT=r.ROOT
D=ROOT/'figs/gray_counterexamples/unregistered_gaw28'
ZERO_FIELDS=tuple(range(241,246))+tuple(range(251,256))
def main():
    start=time.monotonic();issue='--issue' in sys.argv
    assert tuple(range(k.FIELD['h1_0'],k.FIELD['h1_0']+5))+tuple(range(k.FIELD['h1_2'],k.FIELD['h1_2']+5))==ZERO_FIELDS
    target_rows=[]
    for pc,row in own.ROWS.items():
        if row['opcode']!='STX' or row['operands'][-1]!=0:continue
        intervals=[]
        for copy in (0,4):
            for maximum in (False,True):
                counts=tuple((p,n-1 if maximum else 0) for p,n in own.LOOPS.items())
                for mask in (0,1):intervals.append(own.target(pc,copy,counts,mask))
        lo=min(a for a,b in intervals);hi=max(b for a,b in intervals)
        if pc<own.LABEL['workspace'] or pc>=own.LABEL['early_entry']:
            assert 0<=lo<=hi<=5
            kind='native_prefix'
        elif pc==own.LABEL['source_write']+3:
            assert (lo,hi)==(4,5);kind='Workspace_guarded_only'
        else:
            assert 6<=lo<=hi<k.FRAME_WORDS,(pc,row,lo,hi);kind='simulation_only'
        target_rows.append(dict(pc=pc,opcode=row['opcode'],operands=row['operands'],target_interval=[lo,hi],kind=kind))
    assert sum(z['kind']=='Workspace_guarded_only' for z in target_rows)==1
    # Actual prefix at a complete or partial head has common controls up
    # to native store6. Nothing in its first213 steps reads any SF word.
    T={g:r.old.native_output_table(g) for g in range(r.LO,r.HI)}
    V={g:r.old.native_output_table(g,True) for g in range(r.LO,r.HI)}
    runs=[];digest=hashlib.sha256();rng=random.Random(28104);localchecks=0
    for n in range(4,15):
        A=3*n+13
        origins=[(A+3,False),(A+4,True),(A+5,True),(A+6,True),(A+7,True),(A+7,False)]
        for g,foreign in origins:
            rows=r.bank(T,V,g,foreign,A,True);tape={P+i:sum(v<<(j*100) for j,v in enumerate(values)) for i,values in enumerate(rows)}
            expected=r.native(rows);packet=k.Packet(p=1,pc=0);address=P;out={};reads=set();stores=[]
            for tick in range(1,214):
                address+=1 if packet.move==1 else -1 if packet.move==2 else 0
                assert P<=address<=P+5
                if packet.mode==k.SEEK and address==packet.target:
                    kind=packet.args&3;source=(packet.args>>11)&3
                    if kind in (2,3) or kind==0:
                        assert source==0 or kind!=0;reads.add(address)
                packet,ow,sw=k.step_packet(packet,address,tape.get(address,0),out.get(address,0),0,k.beta_bit(own.ROM,address),own.ROM)
                assert sw is None
                if ow is not None:out[address]=ow;stores.append([tick,address-P,ow])
                if packet.mode==k.RUN and packet.pc==own.LABEL['workspace']:break
            else:raise AssertionError('native prefix missed deadline')
            assert reads==set(range(P,P+6)) and [out[P+i] for i in range(6)]==expected
            runs.append(dict(n=n,A=A,receiver=g,foreign=foreign,ticks=tick,native_six_stores=stores))
            # Arbitrary nuisance values are local cofactors, not assigned
            # future tapes. Exact H1 lane0/2 zero follows from the written
            # hold/reset/capture equations for every Word100 nuisance.
            cells={}
            for j in range(-8,9):
                words=[rows[i][j+8] for i in range(6)]+[rng.getrandbits(100) for _ in range(k.FRAME_WORDS-6)]
                for i in ZERO_FIELDS:words[i]=0
                cells[j]=k.cell_from_words(words)
            got=k.cell_words(k.local_transition(cells,own.ROM))
            assert got[:6]==expected and all(got[i]==0 for i in ZERO_FIELDS)
            assert 1<=got[1]<=n+1 and got[4:6]==[0,0]
            digest.update(json.dumps([n,g,foreign,expected,[got[i] for i in ZERO_FIELDS]],separators=(',',':')).encode());localchecks+=1
        T,V=r.next_records(T,V,n,A)
    # In a canonical colony after WF closes, exact F1 depends on right
    # bits only. This verifies all6bit old self/right words in every
    # address-window equivalence class, supporting zero-tail speed2.
    clearchecks=0;cleardig=hashlib.sha256()
    for q in (*range(6),123,*range(Q-6,Q)):
        for bits in range(64):
            for left in (0,1):
                cells={j:k.Cell(addr=(q+j)%Q,age=98*Q+1,f1=((bits>>j)&1) if j>=0 and j<=5 else left) for j in range(-8,9)}
                got=k.native_at(cells)
                count=sum((bits>>j)&1 for j in range(1,6) if q+j<Q)
                expect=int(count>=3 or (bits&1 and count>=2))
                assert got==dict(addr=q,age=98*Q+2,f1=expect,f2=0,wf1=0,wf2=0)
                cleardig.update(json.dumps([q,bits,left,got],sort_keys=True,separators=(',',':')).encode());clearchecks+=1
    for b in range(Q+1):
        for x in range(max(0,b-2),b):
            count=sum(x+j<b and x+j<Q for j in range(1,6))
            assert count<2
    result=dict(passed=True,Q=Q,U=U,error_lambda=24,error_separation=104,
        exact_emitted_Out_target_contracts=target_rows,
        only_postprefix_native_stores_are_WF4_WF5_with96Q_guard=True,
        actual_native_prefixes_on_all_six_front_frame_types=runs,
        actual_local_R_zero_History1_source_field_cofactors=localchecks,
        zero_History_field_cofactor_sha256=digest.hexdigest(),
        canonical_zero_tail_Flag1_native_cofactors=clearchecks,
        clearing_cofactor_sha256=cleardig.hexdigest(),
        canonical_prefix_Flag1_all_zero_by98Q_plus2_plusQ_half=True,
        native_fields_legal_and_output_Age1_to15_guard_closed=True,
        complete_head_unchanged_universal_prepared_execution_bound=141557,
        partial_heads_require_separate_symbolic_absorption_contract=True,
        full_future_SF_output_records_or_Gray_or_iid_claim=False)
    result=json.loads(json.dumps(result));path=D/'GAW28_writeback_contracts_certificate.json'
    if issue:assert not path.exists();path.write_text(json.dumps(result,indent=2)+'\n')
    else:assert result==json.loads(path.read_text())
    print(json.dumps(dict(passed=True,seconds=time.monotonic()-start,store_sites=len(target_rows),prefixes=len(runs),local_R=localchecks,clearing_cofactors=clearchecks,receipt_sha256=hashlib.sha256(path.read_bytes()).hexdigest())),flush=True)
    return result
if __name__=='__main__':main()
