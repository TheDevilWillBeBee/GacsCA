"""Continue actual derived coherent states to U and the next boundary.

No selected future tape or command. The first tape is the readonly bank
remaining from the mixed fault; the second is built from its actual U
Out commit. Legal upper records use the frozen period theorem. Selected
illegal padding requires concrete derived-bank execution instead.
"""
from pathlib import Path
from dataclasses import replace
import hashlib,json,sys,time
S=Path(__file__).resolve().parent;sys.path.insert(0,str(S))
import check_gaw14_active_factor as source
k=source.k;own=source.own;base=source.base;prior=source.prior
ROOT=source.ROOT;D=source.D;P=source.P;history=prior.history

def decode_pairs(v):return {y:int(z,16) for y,z in v}
def continue_active(closure):
    heads={y:k.unpack(v) for y,v in decode_pairs(closure['Head']).items()}
    out=decode_pairs(closure['Out']);scratch=decode_pairs(closure['Scratch'])
    erased=set(closure['readonly_erased_coordinates'])
    def bank(y):return prior.B(y)*int(y not in erased)
    digest=hashlib.sha256();events=[];last=closure['age'];headlo=min(heads,default=0);headhi=max(heads,default=0)
    for age in range(closure['age']+1,120*k.Q+1):
        if all(p.mode in (k.HALT,k.ERROR) and not p.move for p in heads.values()):break
        heads,out,scratch,ws,cs=prior.logical_update(heads,out,scratch,age,bank)
        assert all(-2*k.Q<=y<3*k.Q for y in heads),('head outside chosen finite region',age,sorted(heads))
        headlo=min(headlo,min(heads,default=headlo));headhi=max(headhi,max(heads,default=headhi))
        digest.update(json.dumps([age,[[y,hex(k.pack(p))] for y,p in sorted(heads.items())],ws,cs],separators=(',',':')).encode()+b'\n')
        if cs:events.append(dict(age=age,collision=cs,writes=ws))
        last=age
    return heads,out,scratch,dict(last_actual_execution_age=last,
        terminal_before120Q=all(p.mode in (k.HALT,k.ERROR) and not p.move for p in heads.values()),
        execution_trace_sha256=digest.hexdigest(),collision_events=events,head_extent=[headlo,headhi+1],
        final_Out=[[y,hex(v)] for y,v in sorted(out.items())],
        final_Scratch=[[y,hex(v)] for y,v in sorted(scratch.items())],
        final_Head=[[y,hex(k.pack(p))] for y,p in sorted(heads.items())])

def boundary(closure,heads,out,scratch):
    groups=range(-2,3);erased=set(closure['readonly_erased_coordinates'])
    def raw(x,age):
        return k.Cell(addr=x%k.Q,age=age,
            info=tuple(base.I(x+s)*int(x+s not in erased) for s in k.SLOTS),
            program=tuple(k.beta_bit(own.ROM,(x+s)%k.Q) for s in k.SLOTS),
            mem=tuple(prior.B(x+s)*int(x+s not in erased) for s in k.SLOTS),
            history1=tuple(prior.B(x+s)*int(x+s not in erased) for s in k.SLOTS),
            history2=tuple(prior.B(x+s)*int(x+s not in erased) for s in k.SLOTS),
            history3=tuple(prior.B(x+s)*int(x+s not in erased) for s in k.SLOTS),
            heads=tuple(k.pack(heads.get(x+s,k.ZERO)) for s in k.SLOTS),
            out=tuple(out.get(x+s,0) for s in k.SLOTS),scratch=tuple(scratch.get(x+s,0) for s in k.SLOTS))
    records={g:[out.get(g*k.Q+P+i,0) for i in range(k.FRAME_WORDS)] for g in groups}
    bad=[g for g,ws in records.items() if ws!=k.cell_words(base.nextH(g))]
    covers=[j for j in range(-4,4) if set(bad).issubset({j,j+1})]
    auxiliary=[[y,hex(v)] for y,v in sorted(out.items()) if v and not P<=y%k.Q<P+k.FRAME_WORDS]
    legal=all(all(ws[i]<(k.Q,k.U,2,2,2,2)[i] for i in range(6)) for ws in records.values())
    def info(y):
        g,a=divmod(y,k.Q);i=a-P
        if g not in records:return base.D1(y)
        return records[g][i] if 0<=i<k.FRAME_WORDS else out.get(y,0)
    def encoded(x):return k.Cell(addr=x%k.Q,info=tuple(info(x+s) for s in k.SLOTS),
        program=tuple(k.beta_bit(own.ROM,(x+s)%k.Q) for s in k.SLOTS))
    xs=sorted({g*k.Q+a for g in groups for a in list(range(P-5,P+k.FRAME_WORDS+5))+list(range(-5,9))+list(range(k.Q-8,k.Q+6))}|
        {y-s+d for y in erased|{v[0] for v in auxiliary} for s in k.SLOTS for d in (-1,0,1)})
    digest=hashlib.sha256()
    for x in xs:
        got=k.local_transition({d:raw(x+d,k.U-1) for d in range(-8,9)},own.ROM)
        assert got==encoded(x),(x,'actual old-Out U commit/reset')
        digest.update(json.dumps([x,k.cell_words(got)],separators=(',',':')).encode())
    result=dict(actual_U_bad_normal_receivers=bad,fixed_adjacent_pair_covers=covers,
        no_fixed_adjacent_pair_counterexample=not bool(covers),U_native_padding_legal=legal,
        actual_U_normal_raw_records={str(g):[hex(v) for v in ws] for g,ws in records.items()},
        actual_U_nonzero_unrepresented_Info=auxiliary,actual_raw_U_commit_and_reset_local_R_checks=len(xs),
        commit_signature_sha256=digest.hexdigest(),complete2U_shadow=False,
        legal_record_theorem_applied=False,selected_untyped_second_bank_executions=[])
    def record(g):return records[g] if g in records else k.cell_words(base.nextH(g))
    affected=sorted({g for b in bad for g in range(b-8,b+9)})
    if legal:
        def upper(g):return k.cell_from_words(record(g))
        for g in records:assert k.cell_words(upper(g))==record(g),(g,'unmasked legal upper roundtrip')
        results=[]
        for g in affected:
            z=k.local_transition({d:upper(g+d) for d in range(-8,9)},own.ROM)
            results.append(dict(receiver=g,actual_next_full_upper_words=[hex(v) for v in k.cell_words(z)],
                shadow=z==base.next2H(g)))
        result['actual_next_upper_transitions']=results
        result['complete2U_shadow']=all(v['shadow'] for v in results)
        result['legal_record_theorem_applied']=True
    else:
        for g in affected:
            tape=history.tape_of(record,g);early=history.run(tape,early=True);late=history.run(tape)
            words=[int(v,16) for v in late[0]['out_words']]
            result['selected_untyped_second_bank_executions'].append(dict(receiver=g,
                actual_derived_input_raw_records=[[g+d,[hex(v) for v in record(g+d)]] for d in range(-8,9)],
                early=early[0],late=late[0],shadow=words==k.cell_words(base.next2H(g))))
        result['complete2U_shadow']=all(v['shadow'] for v in result['selected_untyped_second_bank_executions'])
    return result

def run(prefix):
    start=time.monotonic();closure=prefix['closure'];heads,out,scratch,late=continue_active(closure)
    boundary_result=boundary(closure,heads,out,scratch)
    return dict(recipe=prefix['recipe'],actual_fault_clock=source.T,Q=k.Q,U=k.U,error_lambda=24,error_separation=104,
        actual_active_native_SF_prefix_trace=source.source.signature(source.source.stable(prefix)),actual_same_intact_H=True,
        actual_derived_late_continuation=late,actual_U_and2U=boundary_result,
        independent_future_tape_Workspace_or_Head=False,new_rule=False,
        Gray_or_iid_or_shorter_U=False,elapsed_seconds=time.monotonic()-start)

def main():
    D.mkdir(parents=True,exist_ok=True)
    for recipe in source.recipes():
        prefix=json.loads((D/(recipe['tag']+'_active_receipt.json')).read_text())
        result=run(prefix)
        (D/(recipe['tag']+'_boundary_receipt.json')).write_text(json.dumps(result,indent=2)+'\n')
        b=result['actual_U_and2U']
        print(json.dumps(dict(tag=recipe['tag'],bad_U=b['actual_U_bad_normal_receivers'],
            native_padding_legal=b['U_native_padding_legal'],complete2U=b['complete2U_shadow'],
            second_raw_runs=len(b['selected_untyped_second_bank_executions']),
            fixed_adjacent_pair=b['fixed_adjacent_pair_covers'],seconds=result['elapsed_seconds'])),flush=True)

if __name__=='__main__':main()
