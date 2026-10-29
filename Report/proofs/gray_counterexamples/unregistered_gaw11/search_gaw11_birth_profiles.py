"""NEW exact full-local_R prefix search, sharing only equal old reads.

Every SF transition is the frozen GAW2R function. Native batching and
logical-read/immutable packet caching are diagnostic evaluation changes,
not CA transitions. Future Workspace and tapes are never prescribed.
"""
from pathlib import Path
from dataclasses import replace
from functools import lru_cache
import ctypes,hashlib,json,random,sys,time
ROOT=Path(__file__).resolve().parents[4];S=Path(__file__).resolve().parent
D=ROOT/'figs/gray_counterexamples/unregistered_gaw11'
sys.path.insert(0,str(S.parent/'unregistered_gaw10'))
import trace_gaw10_birth as prior
k=prior.k;own=prior.own;base=prior.base;T=prior.T
FIELDS=('heads','mem','out','info','scratch','program','courier_l','courier_r','mail_l','mail_r','history1','history2','history3')
Site=prior.mixed.Site

class View(dict):
    def __init__(self,origin,read):
        self.origin=origin
        super().__init__((d,read(origin+d)) for d in range(-8,9))

class SharedReads:
    def __init__(self):
        self.native_original=k.native_at;self.logical_original=k.logical
        self.base_native_original=k.base.native_at;self.base_logical_original=k.base.logical
        self.pack_original=k.pack;self.unpack_original=k.unpack
        self.c=ctypes.CDLL(str(D/'gaw11_native_batch.so'))
        self.c.gaw11_native_batch.argtypes=[ctypes.POINTER(Site),ctypes.c_int,ctypes.POINTER(Site)]
        self.c.gaw11_native_batch.restype=ctypes.c_int
    def __enter__(self):
        k.native_at=k.base.native_at=self.native
        k.logical=k.base.logical=self.logical
        k.pack=lru_cache(maxsize=8192)(self.pack_original)
        k.unpack=lru_cache(maxsize=8192)(self.unpack_original)
        return self
    def __exit__(self,*args):
        k.native_at=self.native_original;k.base.native_at=self.base_native_original
        k.logical=self.logical_original;k.base.logical=self.base_logical_original
        k.pack=self.pack_original;k.unpack=self.unpack_original
    def begin(self,lo,hi,read):
        self.lo=lo-8;self.hi=hi+8;self.read={x:read(x) for x in range(self.lo,self.hi+1)}
        n=self.hi-self.lo+1;a=(Site*n)();b=(Site*n)()
        for x,z in self.read.items():a[x-self.lo]=Site(z.addr,z.age,z.f1,z.f2,z.wf1,z.wf2,0)
        assert self.c.gaw11_native_batch(a,n,b)==0
        self.natives={x:dict(addr=b[x-self.lo].gf,age=b[x-self.lo].age,
            f1=b[x-self.lo].f1,f2=b[x-self.lo].f2,wf1=0,wf2=0) for x in range(lo-3,hi+4)}
        self.votes={}
    def native(self,cells,centre=0):
        if isinstance(cells,View):return dict(self.natives[cells.origin+centre])
        return self.native_original(cells,centre)
    def logical(self,cells,name,y):
        if not isinstance(cells,View):return self.logical_original(cells,name,y)
        key=(cells.origin+y,name)
        if key not in self.votes:
            values=[getattr(self.read[key[0]-s],name)[h] for h,s in enumerate(k.SLOTS)]
            self.votes[key]=values[0] if all(v==values[0] for v in values) else k.vote(values)
        return self.votes[key]
    def update(self,lo,hi,read):
        self.begin(lo,hi,read)
        return {x:k.local_transition(View(x,self.read.__getitem__),own.ROM) for x in range(lo,hi+1)}

def packed(z):return [z.addr,z.age,z.f1,z.f2,z.wf1,z.wf2]+[[hex(v) for v in getattr(z,n)] for n in FIELDS]

def recipes():
    # Full-range legal clocks; Q-sized near-birth jumps are deliberately
    # distinct from the earlier tiny-offset noise families.
    ages=(k.EARLY_BIRTH-1,102*k.Q, k.EARLY_BIRTH-2,102*k.Q-2,
          k.U-1,k.U-16,k.EARLY_BIRTH-k.Q,102*k.Q-k.Q)
    cases=[]
    for index in range(24):
        start=(k.PRIMARY_START-6,k.PRIMARY_START-14,k.PRIMARY_START+32,k.Q-16)[index%4]
        age=ages[(index//3)%len(ages)];mode=(index//4)%3
        flags=(0,2,3,15)[(index//2)%4]
        centre=start+7
        payload=[]
        for j in range(16):
            x=start+j
            gf=x%k.Q if mode==0 else (k.PRIMARY_START+x-centre)%k.Q if mode==1 else (x+1)%k.Q
            payload.append([gf,age,flags])
        cases.append(dict(start=start,payload=payload,mode=mode,flags=flags,kind='uniform-birth-near-native'))
    return cases

def run(recipe,limit=128):
    start=time.monotonic();state={};b=recipe['start'];payload=[];support=set()
    for j,(gf,age,flags) in enumerate(recipe['payload']):
        x=b+j;old=prior.reference(x,0)
        z=replace(old,addr=gf,age=age,f1=flags&1,f2=(flags>>1)&1,wf1=(flags>>2)&1,wf2=(flags>>3)&1)
        assert z!=old;state[x]=z;support.add((x,T))
        payload.append(dict(x=x,t=T,old_words=[hex(w) for w in k.cell_words(old)],replacement_words=[hex(w) for w in k.cell_words(z)]))
    classification=base.gray_errors.classify(support,support,Q=k.Q,U=k.U,sep=104,exact_limit=1)
    assert classification['level1'] and classification['level0']==0 and classification['extent']==(16,1)
    rows=[];digest=hashlib.sha256();first_out=None;max_heads=0;maxpc=0
    with SharedReads() as shared:
        for t in range(1,limit+1):
            old=state
            def read(x):return old.get(x,prior.reference(x,t-1))
            lo=min(old)-8;hi=max(old)+8;raw=shared.update(lo,hi,read)
            state={x:z for x,z in raw.items() if z!=prior.reference(x,t)}
            if not state:break
            head=[(x,h,k.unpack(v)) for x,z in state.items() for h,v in enumerate(z.heads) if v]
            nonzero={name:[(x,h,hex(v)) for x,z in state.items() for h,v in enumerate(getattr(z,name)) if v] for name in ('out','courier_l','courier_r')}
            if nonzero['out'] and first_out is None:
                x=nonzero['out'][0][0];cone={d:read(x+d) for d in range(-8,9)}
                direct=k.local_transition(cone,own.ROM);assert direct==raw[x]
                first_out=dict(elapsed=t,x=x,full_old_cone_words=[[d,[hex(v) for v in k.cell_words(z)]] for d,z in cone.items()],
                    full_new_words=[hex(v) for v in k.cell_words(direct)],nonzero_Out=nonzero['out'],
                    direct_unbatched_full_local_R_equal=True)
            max_heads=max(max_heads,len(head));maxpc=max([maxpc]+[p.pc for x,h,p in head])
            dirty=sorted((x,packed(z)) for x,z in state.items())
            digest.update(json.dumps([t,dirty],separators=(',',':')).encode()+b'\n')
            rows.append(dict(elapsed=t,computed_cells=hi-lo+1,dirty_cells=len(state),
                native_geometry_disagreement=sum(z.addr!=x%k.Q or z.age!=T+t for x,z in state.items()),
                raw_head_copies=len(head),head_pcs=sorted({p.pc for x,h,p in head}),
                nonzero_Out_or_couriers=nonzero))
    return dict(recipe=recipe,whole_cell_payloads=payload,support=sorted(support),classification=classification,
        elapsed_prefix=rows[-1]['elapsed'] if rows else 0,rows=rows,maximum_head_copies=max_heads,maximum_head_pc=maxpc,
        first_actual_nonzero_Out=first_out,final_complete_dirty_cells=[[x,packed(z)] for x,z in sorted(state.items())],
        complete_prefix_state_sha256=digest.hexdigest(),actual_H_same_error_history=True,
        future_Workspace_or_tapes_selected=False,whole_period_or_operational_Gray_iid_failure=False,
        elapsed_seconds=time.monotonic()-start)

def native_checks(count=1024):
    rng=random.Random(0xb104102);c=SharedReads();checks=0;digest=hashlib.sha256()
    for trial in range(count):
        cells={j:k.Cell(addr=rng.randrange(k.Q),age=rng.randrange(k.U),f1=rng.randrange(2),f2=rng.randrange(2),
            wf1=rng.randrange(2),wf2=rng.randrange(2)) for j in range(-8,9)}
        c.begin(0,0,cells.__getitem__)
        expected=c.native_original(cells);assert c.natives[0]==expected
        digest.update(json.dumps(expected,sort_keys=True,separators=(',',':')).encode());checks+=1
    return dict(actual_scalar_native_checks=checks,signature_sha256=digest.hexdigest())

def main():
    D.mkdir(parents=True,exist_ok=True);start=time.monotonic();checks=native_checks();cases=[]
    print(json.dumps(dict(native_checks=checks,starting_full_SF_birth_profile_search=True)),flush=True)
    for index,recipe in enumerate(recipes()):
        result=run(recipe);cases.append(result)
        print(json.dumps(dict(case=index,age=recipe['payload'][0][1],flags=recipe['flags'],mode=recipe['mode'],
            prefix=result['elapsed_prefix'],head_max=result['maximum_head_copies'],maxpc=result['maximum_head_pc'],
            first_Out_tick=None if result['first_actual_nonzero_Out'] is None else result['first_actual_nonzero_Out']['elapsed'],
            elapsed_seconds=result['elapsed_seconds'])),flush=True)
        out=dict(name='GAW11 full-SF birth-near actual prefix discovery campaign',Q=k.Q,U=k.U,error_lambda=24,error_separation=104,
            native_checks=checks,cases=cases,actual_frozen_GAW2R_used=True,whole_period_or_Gray_iid_conclusion=False,
            independent_future_commands=False,new_rule_created=False,elapsed_seconds=time.monotonic()-start)
        (D/'GAW11_birth_profile_search.json').write_text(json.dumps(out,indent=2)+'\n')
    return out

if __name__=='__main__':main()
