"""Complete selected actual phase-dependent histories and decoded boundaries."""
from pathlib import Path
import hashlib,json,sys,time
S=Path(__file__).resolve().parent;sys.path.insert(0,str(S))
import search_gaw15_phase_packets as phase
k=phase.k;own=phase.own;base=phase.base;prior=phase.prior;D=phase.D;P=phase.P

def selected():
    return [phase.recipes()[i] for i in (0,4)]+phase.source_recipes()+[
        dict(tag='history_capture_3841',start=P-7,width=16,rows=1,gf_shift=-1,age=72*k.Q+1,flags=0,
            packet_kind='stationary-store',Out=1,Scratch=k.MASK)]

def derive_coherent(state):
    assert all(len(set(v))==1 for row in state.diff.values() for v in row.values())
    def value(name,y):return state.diff.get(y,{}).get(name,(state.clean(name,y),)*5)[0]
    work={}
    for name in ('heads','out','scratch'):
        initial=getattr(state.shadow,name)
        work[name]={y:k.pack(v) if name=='heads' else v for y,v in initial.items()}
        for y,row in state.diff.items():
            if name in row:work[name][y]=row[name][0]
        work[name]={y:v for y,v in work[name].items() if v}
    work['heads']={y:k.unpack(v) for y,v in work['heads'].items()}
    return value,work

def complete(state):
    value,work=derive_coherent(state);heads=work['heads'];out=work['out'];scratch=work['scratch']
    digest=hashlib.sha256();events=[];last=state.age
    for age in range(state.age+1,120*k.Q+1):
        if all(p.mode in (k.HALT,k.ERROR) and not p.move for p in heads.values()):break
        heads,out,scratch,writes,collisions=prior.logical_update(heads,out,scratch,age,lambda y:value('mem',y))
        assert all(-2*k.Q<=y<4*k.Q for y in heads),('coherent Head finite cut',age)
        digest.update(json.dumps([age,[[y,hex(k.pack(p))] for y,p in sorted(heads.items())],writes,collisions],separators=(',',':')).encode()+b'\n')
        if writes or collisions:events.append(dict(age=age,writes=writes,collisions=collisions))
        last=age
    assert all(p.mode in (k.HALT,k.ERROR) and not p.move for p in heads.values())
    groups=range(-2,4)
    records={g:[out.get(g*k.Q+P+i,0) for i in range(k.FRAME_WORDS)] for g in groups}
    bad=[g for g,ws in records.items() if ws!=k.cell_words(base.nextH(g))]
    covers=[j for j in range(-4,5) if set(bad).issubset({j,j+1})]
    auxiliary=[[y,hex(v)] for y,v in sorted(out.items()) if v and not P<=y%k.Q<P+k.FRAME_WORDS]
    legal=all(all(0<=ws[i]<(k.Q,k.U,2,2,2,2)[i] for i in range(6)) for ws in records.values())
    def record(g):return records[g] if g in records else k.cell_words(base.nextH(g))
    def encoded(x):
        def info(y):
            g,a=divmod(y,k.Q);i=a-P
            return record(g)[i] if 0<=i<k.FRAME_WORDS else out.get(y,0)
        return k.Cell(addr=x%k.Q,info=tuple(info(x+s) for s in k.SLOTS),
            program=tuple(k.beta_bit(own.ROM,(x+s)%k.Q) for s in k.SLOTS))
    def raw(x):
        data={name:tuple(value(name,x+s) for s in k.SLOTS) for name in phase.FIELDS}
        data['heads']=tuple(k.pack(heads.get(x+s,k.ZERO)) for s in k.SLOTS)
        data['out']=tuple(out.get(x+s,0) for s in k.SLOTS)
        data['scratch']=tuple(scratch.get(x+s,0) for s in k.SLOTS)
        data['program']=tuple(k.beta_bit(own.ROM,(x+s)%k.Q) for s in k.SLOTS)
        return k.Cell(addr=x%k.Q,age=k.U-1,**data)
    xs={g*k.Q+a for g in groups for a in range(P-4,P+k.FRAME_WORDS+5)}
    xs.update(y-s+d for y in state.diff|{y:None for y,v in out.items() if v} for s in k.SLOTS for d in (-1,0,1))
    sig=hashlib.sha256()
    for x in sorted(xs):
        z=k.local_transition({d:raw(x+d) for d in range(-8,9)},own.ROM)
        assert z==encoded(x),(state.recipe['tag'],x,'actual old-Out commit/reset')
        sig.update(json.dumps([x,k.cell_words(z)],separators=(',',':')).encode())
    second=[]
    if legal:
        def upper(g):
            z=k.cell_from_words(record(g));assert k.cell_words(z)==record(g),('unmasked legal record',g)
            return z
        for g in sorted({y for b in bad for y in range(b-8,b+9)}):
            z=k.local_transition({d:upper(g+d) for d in range(-8,9)},own.ROM)
            second.append(dict(receiver=g,actual_next_full_upper_words=[hex(v) for v in k.cell_words(z)],shadow=z==base.next2H(g)))
    return dict(actual_remaining_execution_last_age=last,terminal_before120Q=True,
        actual_remaining_execution_trace_sha256=digest.hexdigest(),actual_writes_collisions=events,
        actual_U_bad_normal_receivers=bad,fixed_adjacent_pair_covers=covers,actual_U_native_words_legal=legal,
        actual_U_normal_full_words={str(g):[hex(v) for v in ws] for g,ws in records.items()},
        actual_U_nonzero_unused_Info=auxiliary,actual_U_full_local_R_commit_reset_checks=len(xs),
        actual_U_commit_signature_sha256=sig.hexdigest(),actual_derived_second_upper_transitions=second,
        complete2U_shadow=bool(legal and all(v['shadow'] for v in second)),
        actual_legal_record_period_theorem_applied=bool(legal))

def run(recipe,limit=12000):
    started=time.monotonic();state=phase.Phase(recipe);rows=[];digest=hashlib.sha256();closure=None
    first_geometry=first_native=None
    for tick in range(limit):
        check=tick in (0,1,2,3,7,15,31,63) or (tick+1)%512==0
        row=state.step(check=check);rows.append(row)
        digest.update(json.dumps([row,state.snapshot()],separators=(',',':')).encode()+b'\n')
        if not row['geometry'] and first_geometry is None:first_geometry=state.tick
        if not(row['geometry'] or row['native_flags'] or row['actual_Workspace_sources']) and first_native is None:first_native=state.tick
        if state.quiet_coherent(row):closure=state.snapshot();break
    result=dict(recipe=recipe,Q=k.Q,U=k.U,error_lambda=24,error_separation=104,actual_intact_H=True,
        actual_chronological_fault_clock=phase.T,complete_old_and_replacement_payload=state.payload,
        original_c104_classification=state.classification,actual_physical_prefix_rows=rows,
        actual_prefix_trace_sha256=digest.hexdigest(),first_geometry_quiet=first_geometry,first_native_quiet=first_native,
        actual_quiet_coherent_closure=closure,new_transition_or_selected_future_tape=False,
        universal_recovery_or_Gray_iid_or_shorter_U=False)
    if closure is not None:result['actual_boundary_continuation']=complete(state)
    result['elapsed_seconds']=time.monotonic()-started
    return result

def main():
    for recipe in selected():
        result=run(recipe)
        (D/(recipe['tag']+'_complete.json')).write_text(json.dumps(result,indent=2)+'\n')
        b=result.get('actual_boundary_continuation',{})
        print(json.dumps(dict(tag=recipe['tag'],prefix_rows=len(result['actual_physical_prefix_rows']),
            WF_rows=sum(bool(v['actual_Workspace_sources']) for v in result['actual_physical_prefix_rows']),
            closure=result['actual_quiet_coherent_closure'] is not None,bad_U=b.get('actual_U_bad_normal_receivers'),
            legal=b.get('actual_U_native_words_legal'),shadow2U=b.get('complete2U_shadow'),seconds=result['elapsed_seconds'])),flush=True)

if __name__=='__main__':main()
