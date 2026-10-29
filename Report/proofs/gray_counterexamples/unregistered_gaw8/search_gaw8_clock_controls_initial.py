"""Finite actual-prefix campaign with canonical GF and native-only faults.

Actual WF silence is supplied only by the frozen GAW7 source-cone proof.
No result past3844 is accepted unless every clock label has healed by then.
"""
from pathlib import Path
import ctypes,hashlib,json,random,sys,time
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw6'))
import check_gaw6_actual_bank_map as prior
base=prior.base;k=base.k;own=base.own
S=Path(__file__).resolve().parent;D=ROOT/'figs/gray_counterexamples/unregistered_gaw8'
F1,F2,W1,W2=1<<16,1<<17,1<<18,1<<19
AGEONLY=1<<31
class Result(ctypes.Structure):
    _fields_=[(n,ctypes.c_int) for n in ('status','clock_recovery','native_recovery','max_segments',
        'min_hull','max_hull','final_segments')]+[('events',ctypes.c_uint64)]

def library():
    c=ctypes.CDLL(str(D/'gaw8_categorical_native.so'))
    c.gaw8_cofactor.argtypes=[ctypes.POINTER(ctypes.c_uint32),ctypes.c_int]
    c.gaw8_cofactor.restype=ctypes.c_uint32
    c.gaw8_run.argtypes=[ctypes.c_int,ctypes.POINTER(ctypes.c_uint32),ctypes.c_int,ctypes.c_int,
        ctypes.c_int,ctypes.POINTER(Result),ctypes.POINTER(ctypes.c_uint32),ctypes.c_int]
    c.gaw8_run.restype=ctypes.c_int
    return c

def run(c,b,rows):
    payload=(ctypes.c_uint32*(len(rows)*16))(*[v for row in rows for v in row])
    r=Result();final=(ctypes.c_uint32*(3*4096))()
    updates=c.gaw8_run(b,payload,16,len(rows),32768,ctypes.byref(r),final,len(final))
    assert updates>=0
    return dict({n:getattr(r,n) for n,_ in r._fields_},updates=updates,
        final_state=[[ctypes.c_int(final[3*i]).value,ctypes.c_int(final[3*i+1]).value,final[3*i+2]]
            for i in range(r.final_segments)])

def native_checks(c):
    rng=random.Random(0x8c104);count=0;digest=hashlib.sha256()
    phases=list(range(5))+[5]+list(range(k.Q-5,k.Q))
    deltas=[0]+rng.sample(range(1,k.U),32)
    for p in phases:
        for case in range(256):
            theta=rng.randrange(k.U);v=[rng.randrange(33)|(rng.randrange(16)<<16) for _ in range(11)]
            labels=[z&65535 for z in v]
            cells={j:dict(addr=(p+j)%k.Q,age=(theta+deltas[labels[j+5]])%k.U,
                f1=(v[j+5]>>16)&1,f2=(v[j+5]>>17)&1,
                wf1=(v[j+5]>>18)&1,wf2=(v[j+5]>>19)&1) for j in range(-5,6)}
            got=c.gaw8_cofactor((ctypes.c_uint32*11)(*v),p)
            result=k.predecessor.scalar_native(cells)
            expected=dict(addr=p,age=(theta+deltas[got&65535]+1)%k.U,
                f1=(got>>16)&1,f2=(got>>17)&1,wf1=0,wf2=0)
            assert result==expected,(p,case,result,expected)
            count+=1;digest.update(json.dumps([p,theta,v,got],separators=(',',':')).encode()+b'\n')
    return dict(actual_scalar_checks=count,signature_sha256=digest.hexdigest(),
        count_exists_fallback_Flag1_Flag2_WF_correspondence_checked=True)

def campaign():
    start=time.monotonic();c=library();checks=native_checks(c);rng=random.Random(0x8a8192)
    patterns=[list(range(1,17)),[1,2]*8,[1]*8+[2]*8,[1]*5+[2]*6+[3]*5,
        [1,1,2,2]*4,[1]*16,[1,2,3,4]*4]
    starts=[0,1,2,3,4,5,k.PRIMARY_START-8,k.PRIMARY_START,k.Q-16,k.Q-8,k.Q-1]
    controls=[0,F1,F2,W1,W2,F1|F2,F1|F2|W1|W2]
    cases=[]
    for b in starts:
        for pi,p in enumerate(patterns):
            for control in controls:
                rows=[[v|control for v in p]];result=run(c,b,rows)
                cases.append(dict(start=b,pattern=pi,native_rows=rows,kind='structured-one-row',**result))
    for index in range(256):
        b=rng.choice(starts) if index<128 else rng.randrange(k.Q)
        rows=[[rng.randrange(1,17)|(rng.randrange(16)<<16) for _ in range(16)] for _ in range(16 if index%4==0 else 1)]
        result=run(c,b,rows)
        cases.append(dict(start=b,pattern=None,native_rows=rows,kind='random-native16row' if len(rows)>1 else 'random-one-row',**result))
    result=dict(name='GAW8 finite nonuniform Age/native-control actual-prefix campaign',Q=k.Q,U=k.U,
        error_lambda=24,error_separation=104,source_silence_horizon=3844,
        GF_canonical_and_SF_untouched_required=True,source_cone_derived_from_actual_intact_reset=True,
        native_cofactor_checks=checks,cases=cases,
        clock_survivors_past_proved_source_horizon=[i for i,v in enumerate(cases) if v['status']==1],
        unresolved_native_cases=[i for i,v in enumerate(cases) if v['status']!=0],
        maximum_clock_recovery=max(v['clock_recovery'] for v in cases),
        maximum_native_recovery=max(v['native_recovery'] for v in cases),
        general_native_eroder_or_decoded_relation_proved=False,Gray_or_iid_counterexample=False,
        elapsed_seconds=time.monotonic()-start)
    (D/'GAW8_clock_control_campaign.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(cases=len(cases),survivors=result['clock_survivors_past_proved_source_horizon'],
        maximum_clock_recovery=result['maximum_clock_recovery'],maximum_native_recovery=result['maximum_native_recovery'],
        elapsed_seconds=result['elapsed_seconds'])),flush=True)
    return result

if __name__=='__main__':campaign()
