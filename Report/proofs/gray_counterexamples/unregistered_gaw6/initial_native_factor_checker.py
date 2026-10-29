"""Pin common-clock native/Info factor to actual frozen GAW2R local_R."""
from pathlib import Path
from dataclasses import replace
import ctypes,sys,hashlib,json,random,time
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw4'))
import check_gaw4_real1_mail as base
k=base.k;own=base.own
S=Path(__file__).resolve().parent;D=ROOT/'figs/gray_counterexamples/unregistered_gaw6'

class Site(ctypes.Structure):
    _fields_=[('gf',ctypes.c_uint16),('f1',ctypes.c_uint8),('f2',ctypes.c_uint8),
              ('w1',ctypes.c_uint8),('w2',ctypes.c_uint8),('info',ctypes.c_uint8)]

def project(c):return Site(c.addr,c.f1,c.f2,c.wf1,c.wf2,sum((v&1)<<h for h,v in enumerate(c.info)))
def vector(c):return [c.gf,c.f1,c.f2,c.w1,c.w2,c.info]
def lib():
    result=ctypes.CDLL(str(D/'gaw6_native_info.so'))
    result.gaw6_step.argtypes=[ctypes.POINTER(Site),ctypes.POINTER(Site),ctypes.c_int,ctypes.c_int]
    return result

def main(write=True):
    start=time.monotonic();C=lib();rng=random.Random(0x6c104);checks=0;digest=hashlib.sha256()
    ages=[96*k.Q-1,96*k.Q,96*k.Q+1,98*k.Q-2,98*k.Q-1,98*k.Q,102*k.Q-1,102*k.Q,102*k.Q+1,k.U-2]
    for age in ages:
        for case in range(48):
            cells={};array=(Site*49)();new=(Site*49)()
            for x in range(-24,25):
                kwargs=dict(addr=rng.randrange(k.Q),age=age,f1=rng.randrange(2),f2=rng.randrange(2),wf1=rng.randrange(2),wf2=rng.randrange(2))
                # Arbitrary private tracks; Info high bits included. Only low
                # Info bits belong to the projection. Large packet fields
                # remain legal declared raw bit patterns.
                for name in base.NAMES:
                    width=2200 if name=='heads' else 1700 if name in ('mem','history1','history2','history3') else 100
                    kwargs[name]=tuple(rng.getrandbits(width) for _ in range(5))
                cells[x]=k.Cell(**kwargs);array[x+24]=project(cells[x])
            assert C.gaw6_step(array,new,49,age)==0
            for x in range(-16,17):
                actual=k.local_transition({j:cells[x+j] for j in range(-8,9)},own.ROM)
                expected=vector(project(actual));obtained=vector(new[x+24])
                assert obtained==expected,(age,case,x,obtained,expected)
                checks+=1;digest.update(json.dumps([age,case,x,expected],separators=(',',':')).encode()+b'\n')
    result=dict(name='GAW6 common-clock held-Info native factor cofactor audit',Q=k.Q,U=k.U,
        error_lambda=24,error_separation=104,common_clock_required=True,
        computed_age0_or80Qminus1_excluded=True,private_fields_free_in_actual_checks=True,
        Info_high_bits_free=True,actual_local_R_checks=checks,cofactor_digest=digest.hexdigest(),
        algebraic_factor_proof_required=True,full_rule_or_noise_proof=False,
        elapsed_seconds=time.monotonic()-start)
    p=D/'GAW6_native_factor_receipt.json'
    if write:p.write_text(json.dumps(result,indent=2)+'\n')
    else:
        old=json.loads(p.read_text());a=dict(result);a.pop('elapsed_seconds');old.pop('elapsed_seconds');assert a==old
    print(json.dumps(result));return result

if __name__=='__main__':main()
