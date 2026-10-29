"""Exploratory, not a universal repair proof or a changed CA rule."""
from pathlib import Path
import ctypes,hashlib,json,subprocess,tempfile,time
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
Q=4096;U=128*Q;T0=100*Q+2;OFFSET=-Q-16;N=2*Q+32
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

class Site(ctypes.Structure):
    _fields_=[(n,ctypes.c_uint8) for n in ('foreign','f1','f2','wf1','wf2')]

def main():
    started=time.perf_counter();out=ROOT/'figs/gray_counterexamples/unregistered_gawn13'
    out.mkdir(parents=True,exist_ok=True);records=[]
    with tempfile.TemporaryDirectory(prefix='gawn13_sparse_') as temp:
        so=Path(temp)/'probe.so'
        subprocess.run(['cc','-O3','-std=c99','-fPIC','-shared',str(HERE/'gawn13_sparse_native_probe.c'),'-o',str(so)],check=True)
        lib=ctypes.CDLL(str(so));fn=lib.gawn13_run
        fn.argtypes=[ctypes.POINTER(Site),ctypes.c_int,ctypes.c_int,ctypes.POINTER(ctypes.c_int),ctypes.POINTER(Site),ctypes.POINTER(ctypes.c_int)]
        fn.restype=ctypes.c_int
        for b in (0,1,5,64,3992):
            for width in (9,10,31,64,104):
                for delta in sorted({1,2,3,8,(Q-b)%Q or Q-1,Q//2,Q-1}):
                    for flags in (0,1,2,3,8,15):
                        initial=np.zeros((N,5),dtype=np.uint8)
                        initial[b-OFFSET:b+width-OFFSET:2,0]=1
                        for k in range(4):initial[b-OFFSET:b+width-OFFSET,k+1]=(flags>>k)&1
                        limit=12000;events=np.zeros((limit+1,6),dtype=np.int32)
                        final=np.zeros_like(initial);summary=np.zeros(4,dtype=np.int32)
                        status=fn(initial.ctypes.data_as(ctypes.POINTER(Site)),delta,limit,
                            events.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),final.ctypes.data_as(ctypes.POINTER(Site)),
                            summary.ctypes.data_as(ctypes.POINTER(ctypes.c_int)))
                        assert status==summary[0]
                        row=dict(b=b,width=width,delta=delta,flags=flags,status=status,
                            steps=int(summary[1]),max_wrong_GF=int(summary[2]),max_Flag1=int(summary[3]),
                            last_counts=events[summary[1]].tolist())
                        records.append(row)
                        if status!=0:
                            np.savez_compressed(out/f'nonrecover_b{b}_w{width}_d{delta}_f{flags}.npz',
                                initial=initial,events=events,final=final)
    result=dict(name='GAWN13 sparse native projection exploratory campaign',cases=len(records),
        Q=Q,U=U,first_fault_row=T0,no_later_errors=True,
        native_projection_justified_by_GAWN10=True,fullSF_evolution_performed=False,
        all_selected_recovered=all(r['status']==0 for r in records),
        universal_Address_termination_Gray_G17_iid_or_bit_failure_proved=False,
        rule_ROM_constants_G17_changed=False,source_sha256={str(p.relative_to(ROOT)):sha(p) for p in
            (Path(__file__),HERE/'gawn13_sparse_native_probe.c',HERE.parent/'unregistered_gawn10/gawn10_two_offset_projection.c')},
        records=records,elapsed=time.perf_counter()-started)
    path=out/'GAWN13_sparse_native_probe.json';assert not path.exists()
    path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='records'}))

if __name__=='__main__':main()
