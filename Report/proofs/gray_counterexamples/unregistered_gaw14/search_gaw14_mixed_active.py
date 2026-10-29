"""Actual intact-H mixed native/interpreter faults in the frozen GAW2R.

This is a diagnostic executor, not a new cellular-automaton transition.
SharedReads caches identical old reads and batches the exact native prefix.
The full frozen local_transition computes every SF/Workspace output.
"""
from pathlib import Path
from dataclasses import replace
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[4];S=Path(__file__).resolve().parent
D=ROOT/'figs/gray_counterexamples/unregistered_gaw14'
sys.path.insert(0,str(S.parent/'unregistered_gaw12'))
import check_gaw12_active_sf as prior
k=prior.k;own=prior.own;base=prior.base;sharedmod=prior.previous
FIELDS=sharedmod.FIELDS;P=k.PRIMARY_START;T=prior.T

def stable(v):return prior.stable(v)
def signature(v):return prior.signature(v)
def packet(p):return hex(k.pack(p))

class Shadow:
    def __init__(self,groups=(-2,-1,0,1,2),updates=prior.N):
        self.n=updates;self.age=102*k.Q+1+updates
        self.snaps={g:prior.actual_snapshot(g,updates) for g in groups}
        self.heads,self.out,self.scratch=prior.global_work(self.snaps)
    def read(self,x):
        g=x//k.Q
        assert g in self.snaps,('outside certified chronological shadow',x,g)
        return prior.actual_cell(x,self.age,self.heads,self.out,self.scratch)
    def advance(self):
        self.age+=1
        self.heads,self.out,self.scratch,_,_=prior.logical_update(self.heads,self.out,self.scratch,self.age)

def recipes():
    cases=[]
    masks=(k.MASK,1,1<<99)
    for b in (P-7,k.Q-8):
        for index,(shift,age) in enumerate(((1,T),(k.Q//2,102*k.Q+1),(-1,102*k.Q),
                    (k.Q//2,k.U-1),(1,k.EARLY_BIRTH),(-1,96*k.Q+1))):
            cases.append(dict(tag='mixed_%s_%d'%(b,index),start=b,width=16,rows=1,
                gf_shift=shift,age=age,flags=0,packet_kind='cross-store' if b==k.Q-8 else 'stationary-store',
                Out=masks[index%3],Scratch=k.MASK))
    return cases

def replacement(recipe,x,old,t):
    # A coherent logical forged packet at every logical coordinate in the
    # core. Five raw copies refer to their own y=x+s; no future packets.
    regs=[0]*16;regs[0]=recipe['Out'];heads=[]
    for s in k.SLOTS:
        y=x+s
        move=(1 if y<k.Q else 2) if recipe['packet_kind']=='cross-store' else 0
        address=(y+recipe['gf_shift'])%k.Q
        heads.append(k.pack(k.Packet(p=1,move=move,mode=k.SEEK,pc=prior.HLT_PC,
            target=address,args=k.descriptor(1,0,dest=0),regs=tuple(regs))))
    f=recipe['flags']
    return replace(old,addr=(x+recipe['gf_shift'])%k.Q,age=(recipe['age']+t)%k.U,
        f1=f&1,f2=(f>>1)&1,wf1=(f>>2)&1,wf2=(f>>3)&1,heads=tuple(heads),
        out=(recipe['Out'],)*5,scratch=(recipe['Scratch'],)*5)

def coherence(state,shadow):
    if not state:return dict(exact_shadow=True,native_quiet=True,coherent_SF=True,logical_changes={n:[] for n in FIELDS})
    lo=min(state)-3;hi=max(state)+3
    native=all((z.addr,z.age,z.f1,z.f2,z.wf1,z.wf2)==(x%k.Q,shadow.age,0,0,0,0) for x,z in state.items())
    changes={n:[] for n in FIELDS};coherent=True;bad=[]
    def read(x):return state.get(x,shadow.read(x))
    for y in range(lo,hi+1):
        for name in FIELDS:
            values=[getattr(read(y-s),name)[h] for h,s in enumerate(k.SLOTS)]
            if len(set(values))!=1:
                coherent=False
                if len(bad)<8:bad.append([y,name,[hex(v) for v in values]])
            elif values[0]!=getattr(shadow.read(y),name)[0]:changes[name].append([y,hex(values[0])])
    return dict(exact_shadow=not state,native_quiet=native,coherent_SF=coherent,
        first_noncoherent_groups=bad,logical_changes=changes if coherent else None)

def run(recipe,limit=96,write_prefix=False):
    started=time.monotonic();shadow=Shadow();state={};b=recipe['start'];payload=[];support=set()
    for x in range(b,b+recipe['width']):
        old=shadow.read(x);new=replacement(recipe,x,old,0);assert new!=old
        state[x]=new;support.add((x,shadow.age))
        payload.append(dict(x=x,t=shadow.age,old_complete_words=[hex(v) for v in k.cell_words(old)],
            replacement_complete_words=[hex(v) for v in k.cell_words(new)]))
    rows=[];digest=hashlib.sha256();checks=[];closure=None
    with sharedmod.SharedReads() as shared:
        for tick in range(1,limit+1):
            old=state
            def read(x):return old.get(x,shadow.read(x))
            lo=min(old)-8;hi=max(old)+8
            raw=shared.update(lo,hi,read)
            # Pin direct unbatched actual kernels at all fault cells on the
            # first row and at every native/SF frontier thereafter.
            probes=list(range(b,b+recipe['width'])) if tick==1 else sorted({lo+8,hi-8,*[x for x in raw if any(raw[x].heads)]})
            if tick in (1,2,4,8,16,32,64):
                for x in probes:
                    direct=shared.logical_original
                    cone={d:read(x+d) for d in range(-8,9)}
                    got=k.local_transition(cone,own.ROM);assert got==raw[x]
                    checks.append([tick,x,signature(k.cell_words(got))])
            shadow.advance()
            state={x:z for x,z in raw.items() if z!=shadow.read(x)}
            heads=[(x,h,k.unpack(v)) for x,z in state.items() for h,v in enumerate(z.heads) if v]
            native=[x for x,z in state.items() if (z.addr,z.age,z.f1,z.f2,z.wf1,z.wf2)!=(x%k.Q,shadow.age,0,0,0,0)]
            geometry=[x for x,z in state.items() if (z.addr,z.age)!=(x%k.Q,shadow.age)]
            out=[(x,h,hex(v)) for x,z in state.items() for h,v in enumerate(z.out) if v]
            row=dict(elapsed=tick,age=shadow.age,computed_cells=len(raw),dirty_cells=len(state),
                geometry_dirty=len(geometry),native_dirty=len(native),raw_Head_copies=len(heads),
                raw_Out_copies=len(out),head_x_h_pc_mode_move=[(x,h,p.pc,p.mode,p.move) for x,h,p in heads],
                native_hull=None if not native else [min(native),max(native)+1],
                geometry_hull=None if not geometry else [min(geometry),max(geometry)+1])
            rows.append(row);digest.update(json.dumps([tick,[[x,sharedmod.packed(z)] for x,z in sorted(state.items())]],separators=(',',':')).encode()+b'\n')
            if tick>=recipe['rows'] and not native:
                closure=coherence(state,shadow)
                if closure['coherent_SF']:break
            if tick<recipe['rows']:
                for x in range(b,b+recipe['width']):
                    old=state.get(x,shadow.read(x));new=replacement(recipe,x,old,tick)
                    assert new!=old;state[x]=new;support.add((x,shadow.age))
                    payload.append(dict(x=x,t=shadow.age,old_complete_words=[hex(v) for v in k.cell_words(old)],
                        replacement_complete_words=[hex(v) for v in k.cell_words(new)]))
    classification=base.gray_errors.classify(support,support,Q=k.Q,U=k.U,sep=104,exact_limit=1)
    assert classification['level0']==0 and classification['level1'] and classification['extent']==(recipe['width'],recipe['rows'])
    result=dict(recipe=recipe,Q=k.Q,U=k.U,error_lambda=24,error_separation=104,actual_fault_clock=T,
        chronological_shadow_snapshots=[v[0] for g,v in sorted(shadow.snaps.items())],
        whole_cell_payloads=payload,actual_original_c104_classification=classification,rows=rows,
        full_local_R_checks=checks,complete_prefix_trace_sha256=digest.hexdigest(),
        closure=closure,final_age=shadow.age,final_complete_dirty_cells=[[x,[hex(v) for v in k.cell_words(z)]] for x,z in sorted(state.items())],
        actual_same_intact_H=True,future_Workspace_Head_tape_or_command_chosen=False,
        new_rule_or_shorter_U=False,Gray_or_iid_failure=False,elapsed_seconds=time.monotonic()-started)
    if write_prefix:
        D.mkdir(parents=True,exist_ok=True)
        (D/(recipe['tag']+'_prefix.json')).write_text(json.dumps(result,indent=2)+'\n')
    return result,state,shadow

def main():
    D.mkdir(parents=True,exist_ok=True);results=[]
    for i,recipe in enumerate(recipes()):
        rec,_,_=run(recipe,write_prefix=True);results.append(rec)
        c=rec['closure']
        print(json.dumps(dict(case=i,tag=recipe['tag'],elapsed=len(rec['rows']),last=rec['rows'][-1],
            closure=None if c is None else {a:c[a] for a in ('exact_shadow','native_quiet','coherent_SF')},
            seconds=rec['elapsed_seconds'])),flush=True)
        (D/'GAW14_mixed_active_discovery.json').write_text(json.dumps(dict(cases=results,actual_frozen_rule=True,
            operational_conclusion=False,Gray_or_iid_conclusion=False),indent=2)+'\n')
    return results

if __name__=='__main__':main()
