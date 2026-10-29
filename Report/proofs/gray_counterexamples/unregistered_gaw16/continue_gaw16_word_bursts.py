"""Actual U boundary/typed next upper map after derived GAW16 closure."""
from pathlib import Path
import hashlib,json,sys,time
S=Path(__file__).resolve().parent;sys.path.insert(0,str(S))
import search_gaw16_word_bursts as m
k=m.k;own=m.own;base=m.base;prior=m.prior;D=m.D;P=m.P

def boundary(state):
    value,work=m.continuation.derive_coherent(state)
    heads=work['heads'];out=work['out'];scratch=work['scratch']
    trace=hashlib.sha256();events=[];last=state.age
    for age in range(state.age+1,120*k.Q+1):
        if all(p.mode in (k.HALT,k.ERROR) and not p.move for p in heads.values()):break
        heads,out,scratch,writes,collisions=prior.logical_update(heads,out,scratch,age,lambda y:value('mem',y))
        assert all(-2*k.Q<=y<4*k.Q for y in heads),('derived coherent Head cut',age)
        trace.update(json.dumps([age,[[y,hex(k.pack(p))] for y,p in sorted(heads.items())],writes,collisions],separators=(',',':')).encode()+b'\n')
        if writes or collisions:events.append(dict(age=age,writes=writes,collisions=collisions))
        last=age
    terminal=all(p.mode in (k.HALT,k.ERROR) and not p.move for p in heads.values())
    records={g:[out.get(g*k.Q+P+i,0) for i in range(k.FRAME_WORDS)] for g in range(-2,4)}
    bad=[g for g,ws in records.items() if ws!=k.cell_words(base.nextH(g))]
    covers=[j for j in range(-4,5) if set(bad).issubset({j,j+1})]
    illegal=[[g,i,hex(ws[i]),limit] for g,ws in records.items()
        for i,limit in enumerate((k.Q,k.U,2,2,2,2)) if not 0<=ws[i]<limit]
    auxiliary=[[y,hex(v)] for y,v in sorted(out.items()) if v and not P<=y%k.Q<P+k.FRAME_WORDS]
    def record(g):return records[g] if g in records else k.cell_words(base.nextH(g))
    def encoded(x):
        def info(y):
            g,a=divmod(y,k.Q);i=a-P
            return record(g)[i] if 0<=i<k.FRAME_WORDS else out.get(y,0)
        return k.Cell(addr=x%k.Q,info=tuple(info(x+s) for s in k.SLOTS),
            program=tuple(k.beta_bit(own.ROM,(x+s)%k.Q) for s in k.SLOTS))
    def raw(x):
        data={name:tuple(value(name,x+s) for s in k.SLOTS) for name in m.previous.FIELDS}
        data['heads']=tuple(k.pack(heads.get(x+s,k.ZERO)) for s in k.SLOTS)
        data['out']=tuple(out.get(x+s,0) for s in k.SLOTS)
        data['scratch']=tuple(scratch.get(x+s,0) for s in k.SLOTS)
        data['program']=tuple(k.beta_bit(own.ROM,(x+s)%k.Q) for s in k.SLOTS)
        return k.Cell(addr=x%k.Q,age=k.U-1,**data)
    xs={g*k.Q+a for g in range(-2,4) for a in range(P-4,P+k.FRAME_WORDS+5)}
    xs.update(y-s+d for y in state.diff|{y:None for y,v in out.items() if v} for s in k.SLOTS for d in (-1,0,1))
    signature=hashlib.sha256()
    for x in sorted(xs):
        actual=k.local_transition({d:raw(x+d) for d in range(-8,9)},own.ROM)
        assert actual==encoded(x),(state.recipe['tag'],x,'literal old-Out U commit/reset')
        signature.update(json.dumps([x,k.cell_words(actual)],separators=(',',':')).encode())
    second=[]
    if not illegal:
        def upper(g):
            z=k.cell_from_words(record(g));assert k.cell_words(z)==record(g),('unmasked legal upper record',g)
            return z
        for g in sorted({y for b in bad for y in range(b-8,b+9)}):
            actual=k.local_transition({d:upper(g+d) for d in range(-8,9)},own.ROM)
            second.append(dict(receiver=g,actual_next_full_upper_words=[hex(v) for v in k.cell_words(actual)],
                shadow=actual==base.next2H(g)))
    return dict(actual_execution_last_age=last,actual_execution_trace_sha256=trace.hexdigest(),
        actual_remaining_writes_collisions=events,terminal_by120Q=terminal,
        actual_terminal_or_unfinished_heads=[[y,hex(k.pack(p))] for y,p in sorted(heads.items())],
        actual_U_bad_normal_receivers=bad,fixed_adjacent_pair_covers=covers,
        actual_U_normal_full_words={str(g):[hex(v) for v in ws] for g,ws in records.items()},
        actual_U_nonzero_unused_Info=auxiliary,actual_U_illegal_native_words=illegal,
        actual_U_full_local_R_commit_reset_checks=len(xs),actual_U_commit_signature_sha256=signature.hexdigest(),
        actual_U_legal_E_encoding=not illegal,legal_record_period_theorem_applied=not illegal,
        actual_derived_second_upper_transitions=second,complete2U_shadow=bool(not illegal and all(v['shadow'] for v in second)),
        untyped_record_not_decoded_or_given_legal_period_theorem=bool(illegal),
        general_operational_Gray_or_iid_counterexample=False)

def run(recipe,limit=14000):
    started=time.monotonic();r,s=m.run(recipe,limit=limit)
    if r['actual_quiet_coherent_closure'] is not None:r['actual_U_and2U_boundary']=boundary(s)
    r['elapsed_seconds']=time.monotonic()-started
    return r

def main():
    for recipe in m.recipes():
        r=run(recipe);(D/(recipe['tag']+'_complete.json')).write_text(json.dumps(r,indent=2)+'\n')
        b=r.get('actual_U_and2U_boundary',{})
        print(json.dumps(dict(tag=recipe['tag'],rows=len(r['actual_rows']),closure=r['actual_quiet_coherent_closure'] is not None,
            WF_outputs=sum(len(v['actual_Workspace_sources']) for v in r['actual_rows']),
            bad_U=b.get('actual_U_bad_normal_receivers'),illegal_U=b.get('actual_U_illegal_native_words'),
            terminal=b.get('terminal_by120Q'),shadow2U=b.get('complete2U_shadow'),seconds=r['elapsed_seconds'])),flush=True)

if __name__=='__main__':main()
