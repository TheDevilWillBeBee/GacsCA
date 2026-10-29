"""Actual H mixed GF/legal Age/native flag native-envelope search.

Not a whole-period simulator. Before using the native/Info factor, its
zero-head/Out/courier premise is proved by excluding both physical birth
clocks from the entire candidate prefix. Actual Info/WF are evaluated.
"""
from pathlib import Path
from dataclasses import replace
from functools import lru_cache
import ctypes,hashlib,json,random,sys,time
ROOT=Path(__file__).resolve().parents[4];S=Path(__file__).resolve().parent
D=ROOT/'figs/gray_counterexamples/unregistered_gaw9'
sys.path.insert(0,str(ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw8'))
import check_gaw8_mixed_clock_repair as prior
k=prior.k;base=prior.base;own=prior.own;T=96*k.Q;LIMIT=4*k.Q
BIRTHS=(k.EARLY_BIRTH,102*k.Q+1)
class Site(ctypes.Structure):
    _fields_=[('gf',ctypes.c_uint16),('age',ctypes.c_uint32)]+[(n,ctypes.c_uint8) for n in ('f1','f2','w1','w2','info')]
class Result(ctypes.Structure):
    _fields_=[(n,ctypes.c_int) for n in ('status','steps','first_geometry_quiet','first_native_quiet',
        'max_geometry_count','max_geometry_span','min_geometry_x','max_geometry_x',
        'final_geometry_count','final_flag_count','final_info_count')]+[('updates',ctypes.c_uint64)]

def library():
    c=ctypes.CDLL(str(D/'gaw9_native_info.so'))
    c.gaw9_cofactor.argtypes=[ctypes.POINTER(Site),ctypes.POINTER(Site)];c.gaw9_cofactor.restype=ctypes.c_int
    c.gaw9_campaign.argtypes=[ctypes.POINTER(Site),ctypes.POINTER(Site),ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.POINTER(Result),ctypes.POINTER(ctypes.c_int),ctypes.c_int,ctypes.POINTER(Site)]
    c.gaw9_campaign.restype=ctypes.c_int
    return c

def allowed_age(age,limit=LIMIT):
    assert 0<=age<k.U
    return all(not 1<=(birth-age)%k.U<=limit for birth in BIRTHS)

def site(cell):return Site(cell.addr,cell.age,cell.f1,cell.f2,cell.wf1,cell.wf2,sum((w&1)<<h for h,w in enumerate(cell.info)))

def cofactor_checks(c,count=4096):
    rng=random.Random(0x9e104);digest=hashlib.sha256()
    for case in range(count):
        cells={}
        for d in range(-8,9):
            age=rng.randrange(k.U)
            while not allowed_age(age):age=rng.randrange(k.U)
            # Free non-native tapes prove the factor does not assume that
            # History/Mail/Mem are clean. Out, Head and couriers must be0.
            vals=dict(addr=rng.randrange(k.Q),age=age,f1=rng.randrange(2),f2=rng.randrange(2),
                wf1=rng.randrange(2),wf2=rng.randrange(2))
            for name in ('info','program','scratch','mail_l','mail_r'):
                vals[name]=tuple(rng.randrange(k.Q) for _ in range(5))
            for name in ('mem','history1','history2','history3'):
                vals[name]=tuple(rng.randrange(k.Q)<<((case%17)*100) for _ in range(5))
            cells[d]=k.Cell(**vals)
        native=k.native_at(cells);assert native['age'] not in BIRTHS
        got=k.local_transition(cells,own.ROM);out=Site()
        assert c.gaw9_cofactor((Site*17)(*[site(cells[d]) for d in range(-8,9)]),ctypes.byref(out))==0
        expected=site(got)
        assert bytes(out)==bytes(expected),(case,list(k.cell_words(got)[:6]),[(n,getattr(out,n)) for n,_ in Site._fields_])
        assert not any(got.heads+got.out+got.courier_l+got.courier_r)
        digest.update(bytes(out));digest.update(b''.join(bytes(site(cells[d])) for d in range(-8,9)))
    return dict(actual_full_local_R_checks=count,free_History_Mail_Mem_Programme_inputs=True,
        actual_WF_and_Info_compared=True,signature_sha256=digest.hexdigest())

@lru_cache(None)
def initial_domain(colonies=4):
    offset=-colonies*k.Q;n=2*colonies*k.Q+32
    initial=(ctypes.c_uint8*n)(*[sum((base.I(offset+x+s)&1)<<h for h,s in enumerate(k.SLOTS)) for x in range(n)])
    a=(Site*n)(*[Site((offset+x)%k.Q,T,0,0,0,0,initial[x]) for x in range(n)])
    return offset,n,initial,a

def run(c,b,payload,limit=LIMIT,colonies=4):
    offset,n,initial,clean=initial_domain(colonies);a=(Site*n)();ctypes.memmove(a,clean,ctypes.sizeof(clean))
    other=(Site*n)();final=(Site*n)();events=(ctypes.c_int*(8*limit))();r=Result()
    assert len(payload)==16 and all(allowed_age(p[1],limit) for p in payload)
    for j,(gf,age,flags) in enumerate(payload):
        x=b+j-offset
        a[x]=Site(gf,age,*[(flags>>i)&1 for i in range(4)],initial[x])
    code=c.gaw9_campaign(a,other,initial,n,offset,limit,ctypes.byref(r),events,limit,final)
    summary={name:getattr(r,name) for name,_ in Result._fields_}
    summary['return_code']=code
    summary['events']=[list(events[8*t:8*t+8]) for t in range(r.steps)]
    summary['final_native_Info_disagreement']=[[x+offset]+[getattr(final[x],name) for name,_ in Site._fields_]
        for x in range(n) if final[x].gf!=(x+offset)%k.Q or final[x].age!=(T+r.steps)%k.U or any((final[x].f1,final[x].f2,final[x].w1,final[x].w2)) or final[x].info!=initial[x]] if code!=-4 else []
    return summary

def cases():
    rng=random.Random(0x99104)
    starts=(0,k.PRIMARY_START,k.Q-16,k.Q-8)
    ages=(0,k.U-1,32*k.Q,64*k.Q,k.EARLY_BIRTH,80*k.Q-1,T,102*k.Q+1,112*k.Q,120*k.Q)
    assert all(allowed_age(age) for age in ages)
    # Begin with a small source-aware targeted campaign, not thousands of
    # expensive unsupported native runs. Error recipes are retained.
    result=[]
    for b in starts:
        for mode in range(4):
            payload=[]
            for j in range(16):
                gf=((b+j)+((1,k.Q//2,k.Q-1,3)[mode]))%k.Q
                age=ages[(j+mode)%len(ages)]
                payload.append([gf,age,rng.randrange(16)])
            result.append(dict(start=b,payload=payload,kind='mixed-structured'))
    for b in starts:
        payload=[]
        for j in range(16):
            age=rng.randrange(k.U)
            while not allowed_age(age):age=rng.randrange(k.U)
            payload.append([rng.randrange(k.Q),age,rng.randrange(16)])
        result.append(dict(start=b,payload=payload,kind='mixed-full-range-random'))
    return result

def main():
    start=time.monotonic();c=library();checks=cofactor_checks(c)
    print(json.dumps(dict(cofactors=checks,starting_actual_intact_mixed_search=True)),flush=True)
    results=[]
    for index,recipe in enumerate(cases()):
        tick=time.monotonic();out=run(c,recipe['start'],recipe['payload'])
        result=dict(recipe,case_index=index,**out);results.append(result)
        print(json.dumps(dict(case=index,kind=recipe['kind'],status=out['status'],steps=out['steps'],
            geometry_quiet=out['first_geometry_quiet'],native_quiet=out['first_native_quiet'],
            final_geometry=out['final_geometry_count'],geometry_hull=[out['min_geometry_x'],out['max_geometry_x']],
            elapsed_seconds=time.monotonic()-tick)),flush=True)
        checkpoint=dict(name='GAW9 exploratory actual H mixed GF/legal Age/native flag factor search',Q=k.Q,U=k.U,
            error_lambda=24,error_separation=104,actual_factor_cofactor_checks=checks,cases=results,
            no_head_birth_horizon=LIMIT,prohibited_birth_Ages=list(BIRTHS),
            future_Workspace_inputs_selected=False,whole_period_or_Gray_failure_proved=False,
            source_stage_Head_Out_Courier_premises_need_written_proof=True,elapsed_seconds=time.monotonic()-start)
        (D/'GAW9_mixed_native_search.json').write_text(json.dumps(checkpoint,indent=2)+'\n')
    return checkpoint

if __name__=='__main__':main()
