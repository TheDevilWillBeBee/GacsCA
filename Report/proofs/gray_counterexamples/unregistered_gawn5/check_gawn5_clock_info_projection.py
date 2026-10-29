"""Replay an actual-source, native-changing GAWN2 real1 family.

This is a finite family of16 experiments plus an exact written projection
argument. It is not an arbitrary-real1 or continuing-noise proof.
"""
from pathlib import Path
from dataclasses import replace
import argparse,ctypes,hashlib,json,subprocess,sys,time
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(HERE.parent/'unregistered_gawn2'))
import small_rule_gawn2 as k
import small_compositional_cost as own
from gacsca import gray_errors
T=100*k.Q+2;A=96*k.Q-1;LIMIT=4*k.Q
NATIVE=('addr','age','f1','f2','wf1','wf2')
class Site(ctypes.Structure):
    _fields_=[('gf',ctypes.c_uint16),('age',ctypes.c_uint32)]+[(n,ctypes.c_uint8) for n in NATIVE[2:]]
class Result(ctypes.Structure):
    _fields_=[(n,ctypes.c_int) for n in ('steps','age_quiet','flags_quiet',
        'max_age_count','max_age_span','min_age_x','max_age_x','max_flag_count','source_updates')]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def library(out):
    path=out/'gawn5_clock_info_projection.so'
    subprocess.run(['gcc','-std=c11','-O2','-fPIC','-shared',str(HERE/'gawn5_clock_info_projection.c'),'-o',str(path)],check=True)
    lib=ctypes.CDLL(str(path));lib.gawn5_cofactor.argtypes=[ctypes.POINTER(Site),ctypes.c_int,ctypes.POINTER(Site)]
    lib.gawn5_cofactor.restype=ctypes.c_int
    lib.gawn5_campaign.argtypes=[ctypes.c_int,ctypes.c_int,ctypes.POINTER(ctypes.c_int),ctypes.POINTER(Site),ctypes.POINTER(Result)]
    lib.gawn5_campaign.restype=ctypes.c_int
    return lib,path
def cofactor_checks(lib):
    rng=np.random.default_rng(0x4741574e35);checks=[]
    phases=(0,1,2,3,4,5,6,17,k.Q-6,k.Q-5,k.Q-4,k.Q-3,k.Q-2,k.Q-1)
    for index in range(420):
        x=phases[index%len(phases)]+((index//len(phases))%3-1)*k.Q
        cells={};array=(Site*17)()
        for j in range(-8,9):
            flags=int(rng.integers(0,16));age=(A,T)[int(rng.integers(0,2))]
            info=tuple((int(rng.integers(0,1<<60))<<1)|int(x+j+s==3) for s in k.SLOTS)
            native=dict(addr=(x+j)%k.Q,age=age,**{n:(flags>>h)&1 for h,n in enumerate(NATIVE[2:])})
            # Arbitrary legal SF tracks; the projected native update must be
            # independent of their values in the admitted clock classes.
            cells[j]=k.Cell(**native,info=info,
                heads=tuple(int(rng.integers(0,1<<60)) for _ in k.SLOTS),
                out=tuple(int(rng.integers(0,1<<60)) for _ in k.SLOTS),
                courier_l=tuple(int(rng.integers(0,1<<60)) for _ in k.SLOTS),
                courier_r=tuple(int(rng.integers(0,1<<60)) for _ in k.SLOTS))
            array[j+8]=Site(native['addr'],native['age'],*[native[n] for n in NATIVE[2:]])
        actual=k.local_transition(cells,own.ROM);expected=Site()
        assert lib.gawn5_cofactor(array,x,ctypes.byref(expected))==0
        got=[getattr(actual,n) for n in NATIVE]
        want=[expected.gf,expected.age]+[getattr(expected,n) for n in NATIVE[2:]]
        assert got==want,(index,x,got,want)
        checks.append([x,[[getattr(cells[j],n) for n in NATIVE] for j in range(-8,9)],got])
    return checks
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--outdir',type=Path,
        default=ROOT/'figs/gray_counterexamples/unregistered_gawn5');args=parser.parse_args()
    out=args.outdir;out.mkdir(parents=True,exist_ok=True);start=time.monotonic()
    lib,path=library(out);cofactors=cofactor_checks(lib)
    support={(x,T) for x in range(104)}
    cl=gray_errors.classify(support,support,Q=k.Q,U=k.U,sep=104)
    assert cl['level0']==0 and cl['level1'] and cl['extent']==(104,1)
    assert 0<A<A+LIMIT<80*k.Q-1+k.U and A>80*k.Q-1
    assert T+LIMIT<k.U and A+LIMIT<k.U
    records=[];assets={}
    for flags in range(16):
        events=np.zeros((LIMIT,8),dtype=np.int32);final=(Site*(6*k.Q))();res=Result()
        status=lib.gawn5_campaign(flags,LIMIT,events.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),final,ctypes.byref(res))
        assert status==0,(flags,status,res.steps)
        rows=events[:res.steps].copy()
        assert res.age_quiet and res.flags_quiet==res.steps and res.steps<LIMIT
        assert rows[-1,1]==rows[-1,4]==0
        native=np.asarray([[s.gf,s.age,s.f1,s.f2,s.wf1,s.wf2] for s in final],dtype=np.uint32)
        assert np.array_equal(native[:,0],np.arange(-3*k.Q,3*k.Q)%k.Q)
        assert np.all(native[:,1]==T+res.steps) and not np.any(native[:,2:])
        p=out/f'GAWN5_flags{flags:02d}_native_trace.npz'
        np.savez_compressed(p,events=rows,final_native=native);assets[p.name]=sha(p)
        records.append(dict(flags=flags,status=status,**{n:getattr(res,n) for n,_ in res._fields_},
            event_rows_sha256=hashlib.sha256(rows.tobytes()).hexdigest()))
        print(json.dumps(records[-1]),flush=True)
    assert all(r['min_age_x']==0 and r['max_age_x']<k.Q for r in records)
    source_paths=[Path(__file__),HERE/'gawn5_clock_info_projection.c',
        HERE/'GAWN5_NATIVE_CLOCK_INFO_AND_REPAIR_REDUCTION.md',
        HERE.parent/'unregistered_gawn2/small_rule_gawn2.py',
        HERE.parent/'unregistered_gawn2/small_compositional_cost.py',ROOT/'gacsca/gray_errors.py']
    receipt=dict(name='GAWN5 actual Info-supplied native-clock real1 finite family',
        passed=True,Q=k.Q,U=k.U,error_lambda=24,error_separation=104,
        actual_fault_row=T,uniform_replacement_Age=A,width=104,flags_cases=16,
        logical_Info_primary3_forced_to1_by_its_five_actual_holder_bits=True,
        only_Age_and_four_native_flags_plus_these_Info_bits_replaced=True,
        actual_current_GAWN2_native_Info_projection_proved_in_companion_text=True,
        geometry_retained=True,projection_horizon=LIMIT,
        two_actual_clock_classes_avoid_commit_and_special_Info_write=True,
        future_WF_externally_selected=False,classification=cl,measured_cases=records,
        actual_full_kernel_cofactor_checks=len(cofactors),
        cofactor_inputs_outputs_sha256=hashlib.sha256(json.dumps(cofactors,separators=(',',':')).encode()).hexdigest(),
        all16_native_repair_instances_measured=True,
        complete_U_boundary_and_2U_repair_reduction_proved_under_native_history_hypotheses=True,
        full2U_physical_simulation_performed=False,
        maximum_Age_quiet=max(r['age_quiet'] for r in records),
        maximum_all_native_quiet=max(r['flags_quiet'] for r in records),
        arbitrary_GF_changing_real1_or_continuing_higher_or_iid_proved=False,
        full_SF_period_repair_or_decoder_proved=False,Gray_or_G17_counterexample=False,
        new_rule_or_constants_changed=False,
        source_sha256={str(p.relative_to(ROOT)):sha(p) for p in source_paths},
        library_sha256=sha(path),asset_sha256=assets)
    (out/'GAWN5_actual_clock_Info_probe.json').write_text(json.dumps(receipt,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(passed=True,cases=16,cofactor_checks=len(cofactors),
        Age_quiet_by=receipt['maximum_Age_quiet'],native_quiet_by=receipt['maximum_all_native_quiet'],
        elapsed=time.monotonic()-start,full_reliability=False)),flush=True)
if __name__=='__main__':main()
