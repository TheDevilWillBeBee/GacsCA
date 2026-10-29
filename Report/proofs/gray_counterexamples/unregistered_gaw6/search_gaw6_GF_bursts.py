"""Exploratory actual common-clock GF-only bursts after96Q, no later errors.

The projection is exact only through held-Info/held-History phases; no
prepared source and no substituted zero Workspace. Full-period claims
require lifting the retained bank and head/store state separately.
"""
from pathlib import Path
import ctypes,json,sys,time,hashlib
sys.path.insert(0,str(Path(__file__).resolve().parent))
import check_gaw6_native_factor as factor
base=factor.base;k=base.k;I=base.I;Site=factor.Site
ROOT=factor.ROOT;D=factor.D

def campaign(start,delta,steps=k.Q,width=16):
    n=32*k.Q;offset=-16*k.Q
    A=(Site*n)();B=(Site*n)();initial=(ctypes.c_uint8*n)()
    # H's actual low Info bits. The finite window supplies a fixed canonical
    # exterior only while the checked adaptive hull stays16 sites inside it.
    for x in range(n):
        y=x+offset;ib=sum((I(y+s)&1)<<h for h,s in enumerate(k.SLOTS));initial[x]=ib
        A[x]=Site(y%k.Q,0,0,0,0,ib,31);B[x]=A[x]
    fault=[]
    for y in range(start,start+width):
        x=y-offset;old=A[x].gf;new=(old+delta)%k.Q;A[x].gf=new
        fault.append(dict(x=y,t=96*k.Q,old_GF=old,new_GF=new,all_other_bits_unchanged=True))
    summary=(ctypes.c_int*8)();events=(ctypes.c_int*(steps*8))();C=factor.lib()
    C.gaw6_campaign.argtypes=[ctypes.POINTER(Site),ctypes.POINTER(Site),ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.POINTER(ctypes.c_int),ctypes.POINTER(ctypes.c_int),ctypes.c_int]
    t=time.monotonic();status=C.gaw6_campaign(A,B,initial,n,offset,96*k.Q,steps,summary,events,steps)
    if status:
        result=dict(start=start,delta=delta,steps=steps,status=status,elapsed_seconds=time.monotonic()-t)
        print(json.dumps(result),flush=True);return result
    rows=[list(events[8*i:8*i+8]) for i in range(summary[1])]
    final=A if summary[0]%2==0 else B
    native=[];history=[];info=[]
    for x in range(n):
        z=final[x];y=x+offset
        if z.gf!=y%k.Q or z.f1 or z.f2 or z.w1 or z.w2:native.append([y,*factor.vector(z)[:5]])
        if z.keep!=31:history.append([y,z.keep])
        if z.info!=initial[x]:info.append([y,z.info])
    result=dict(start=start,delta=delta,requested_steps=steps,computed_steps=summary[0],status=0,
        original_real1_support=fault,max_GF_sites=summary[2],max_GF_hull=summary[3],
        final_native_disagreement=native,final_History_holder_keep=history,final_Info_lowbit=info,
        event_rows=rows,event_digest_sha256=hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest(),
        actual_H_source=True,full_period_result_claimed=False,elapsed_seconds=time.monotonic()-t)
    print(json.dumps({p:result[p] for p in ('start','delta','requested_steps','computed_steps','status','max_GF_sites','max_GF_hull','elapsed_seconds')}|
        dict(final_native_sites=len(native),final_history_holders=len(history),final_info_holders=len(info))),flush=True)
    return result

def main():
    start=time.monotonic();cases=[]
    for position in (0,5,k.PRIMARY_START-8,k.Q-16,k.Q-8):
        for delta in (1,16,k.Q//2,k.Q-1):cases.append(campaign(position,delta))
    result=dict(name='GAW6 exploratory native-control GF-only bursts from actual intact H',Q=k.Q,U=k.U,
        error_lambda=24,error_separation=104,cases=cases,source_phase=96*k.Q,
        algebraic_projection_proof_required=True,full_period_result=False,Gray_iid_failure=False,
        elapsed_seconds=time.monotonic()-start)
    (D/'GAW6_GF_burst_search.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(cases=len(cases),elapsed_seconds=result['elapsed_seconds'],all_projection_runs_passed=all(c['status']==0 for c in cases))),flush=True)

if __name__=='__main__':main()
