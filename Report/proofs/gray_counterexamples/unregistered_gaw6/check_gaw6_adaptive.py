"""Compare adaptive finite-envelope execution to the dense same projection."""
from pathlib import Path
import ctypes,sys,json,hashlib,time
sys.path.insert(0,str(Path(__file__).resolve().parent))
import check_gaw6_native_factor as f
Site=f.Site;k=f.k;I=f.base.I;D=f.D

def main(write=True):
    t=time.monotonic();C=f.lib();C.gaw6_campaign.argtypes=[ctypes.POINTER(Site),ctypes.POINTER(Site),ctypes.POINTER(ctypes.c_uint8),ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.POINTER(ctypes.c_int),ctypes.POINTER(ctypes.c_int),ctypes.c_int]
    digest=hashlib.sha256();cases=0;sites=0
    for centre in (0,k.PRIMARY_START):
        for delta in (1,16,k.Q//2,k.Q-1):
            for flags in range(16):
                n=4096;offset=centre-n//2;steps=32
                A=(Site*n)();B=(Site*n)();X=(Site*n)();Y=(Site*n)();initial=(ctypes.c_uint8*n)()
                for x in range(n):
                    p=x+offset;bits=sum((I(p+s)&1)<<h for h,s in enumerate(k.SLOTS));initial[x]=bits
                    A[x]=Site(p%k.Q,0,0,0,0,bits,31);B[x]=A[x]
                for p in range(centre,centre+16):
                    x=p-offset;A[x].gf=(A[x].gf+delta)%k.Q
                    A[x].f1=flags&1;A[x].f2=(flags>>1)&1;A[x].w1=(flags>>2)&1;A[x].w2=(flags>>3)&1
                ctypes.memmove(X,A,ctypes.sizeof(A));ctypes.memmove(Y,B,ctypes.sizeof(B))
                summary=(ctypes.c_int*8)();events=(ctypes.c_int*(steps*8))()
                assert C.gaw6_campaign(A,B,initial,n,offset,96*k.Q,steps,summary,events,steps)==0
                for row in range(summary[0]):
                    assert C.gaw6_step(X,Y,n,96*k.Q+row)==0
                    X,Y=Y,X
                adaptive=A if summary[0]%2==0 else B
                assert bytes(adaptive)==bytes(X),(centre,delta,flags)
                digest.update(bytes(adaptive));cases+=1;sites+=n
    result=dict(name='GAW6 adaptive-versus-dense exact finite check',cases=cases,all_final_site_checks=sites,
        dense_projection_equal=True,digest_sha256=digest.hexdigest(),
        adaptive_interval_proof_required=True,elapsed_seconds=time.monotonic()-t)
    p=D/'GAW6_adaptive_receipt.json'
    if write:p.write_text(json.dumps(result,indent=2)+'\n')
    else:
        old=json.loads(p.read_text());a=dict(result);a.pop('elapsed_seconds');old.pop('elapsed_seconds');assert a==old
    print(json.dumps(result));return result

if __name__=='__main__':main()
