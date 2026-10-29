"""NEW actual local_R prefix of the retained GAW9 shifted late birth.

Frozen GAW2R, actual intact H row96 and the same sixteen native-only
overwrites. No future tapes, heads or Workspace inputs are supplied.
"""
from pathlib import Path
from dataclasses import replace
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[4];S=Path(__file__).resolve().parent
D=ROOT/'figs/gray_counterexamples/unregistered_gaw10'
sys.path.insert(0,str(S.parent/'unregistered_gaw9'))
import check_gaw9_native_factor as prior
k=prior.k;own=prior.own;mixed=prior.mixed;base=prior.base;T=mixed.T

def reference(x,t):
    assert 0<=t<6*k.Q
    return replace(mixed.prior.held(x),age=T+t)

def recipe():
    b=k.PRIMARY_START-6
    return dict(start=b,payload=[[(b+j+1)%k.Q,102*k.Q,0] for j in range(16)])

def prefix(limit=32,write=True,verbose=True):
    start=time.monotonic();r=recipe();state={}
    for j,(gf,age,flags) in enumerate(r['payload']):
        x=r['start']+j;state[x]=replace(reference(x,0),addr=gf,age=age)
    digest=hashlib.sha256();rows=[]
    for t in range(1,limit+1):
        out={};lo=min(state)-8;hi=max(state)+8
        for x in range(lo,hi+1):
            cone={d:state.get(x+d,reference(x+d,t-1)) for d in range(-8,9)}
            z=k.local_transition(cone,own.ROM)
            if z!=reference(x,t):out[x]=z
        state=out
        heads=[(x,h,k.unpack(v)) for x,z in state.items() for h,v in enumerate(z.heads) if v]
        nz={name:[(x,h,hex(v)) for x,z in state.items() for h,v in enumerate(getattr(z,name)) if v]
            for name in ('out','courier_l','courier_r')}
        native=[(x,k.cell_words(z)[:6]) for x,z in state.items() if k.cell_words(z)[:6]!=k.cell_words(reference(x,t))[:6]]
        packed=[(x,[hex(w) for w in k.cell_words(z)]) for x,z in sorted(state.items())]
        digest.update(json.dumps([t,packed],separators=(',',':')).encode()+b'\n')
        row=dict(elapsed=t,computed_cells=hi-lo+1,dirty_cells=len(state),native=native,
            heads=[dict(x=x,holder=h,logical_coordinate=x+k.SLOTS[h],packet=hex(k.pack(p)),
                        mode=p.mode,pc=p.pc,target=p.target,move=p.move) for x,h,p in heads],
            nonzero_Out_or_couriers=nz,complete_dirty_words=packed)
        rows.append(row)
        if verbose:print(json.dumps(dict(t=t,dirty=len(state),native=len(native),heads=len(heads),
            out=len(nz['out']),courier_l=len(nz['courier_l']),courier_r=len(nz['courier_r']),
            head_pc=sorted({p.pc for x,h,p in heads}))),flush=True)
    result=dict(name='GAW10 same intact-start shifted late-Head birth actual prefix',Q=k.Q,U=k.U,
        error_lambda=24,error_separation=104,payload=prior.payload(r,complete=True),rows=rows,
        final_dirty_words=rows[-1]['complete_dirty_words'],trace_sha256=digest.hexdigest(),
        actual_same_H_shared_error_history=True,future_Workspace_or_tapes_selected=False,
        whole_period_or_Gray_iid_failure_proved=False,elapsed_seconds=time.monotonic()-start)
    D.mkdir(parents=True,exist_ok=True)
    if write:(D/'GAW10_shifted_birth_prefix.json').write_text(json.dumps(result,indent=2)+'\n')
    return result,state

if __name__=='__main__':prefix()
