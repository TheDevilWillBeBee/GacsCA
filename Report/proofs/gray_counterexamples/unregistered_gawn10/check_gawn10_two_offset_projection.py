"""Native projection transcriptions and selected actual late native histories.

No SF trajectory, complete2U simulation, universal Address repair or iid proof.
The written projection proves independence of SF for this common-clock class.
"""
from pathlib import Path
import argparse,ctypes,hashlib,json,random,subprocess,sys,tempfile,time
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(HERE.parent/'unregistered_gawn2'))
import small_rule_gawn2 as k
import small_compositional_cost as own
T0=100*k.Q+2;LIMIT=4*k.Q;OFFSET=-k.Q-16;N=2*k.Q+32
SF=('heads','mem','out','info','scratch','program','courier_l','courier_r',
    'mail_l','mail_r','history1','history2','history3')
WIDTHS=dict(heads=k.HEAD_BITS,mem=17*k.WORD,history1=17*k.WORD,
            history2=17*k.WORD,history3=17*k.WORD)
class Site(ctypes.Structure):
    _fields_=[(name,ctypes.c_uint8) for name in ('foreign','f1','f2','wf1','wf2')]
class Result(ctypes.Structure):
    _fields_=[(name,ctypes.c_int) for name in ('steps','gf_quiet','native_quiet',
        'max_gf','min_gf','max_gf_x','max_f1','max_f2','snapshots','status')]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def add(d,value):d.update((json.dumps(value,separators=(',',':'))+'\n').encode())
def library(directory):
    path=Path(directory)/'gawn10.so'
    subprocess.run(['gcc','-std=c11','-O2','-fPIC','-shared',str(HERE/'gawn10_two_offset_projection.c'),'-o',str(path)],check=True)
    lib=ctypes.CDLL(str(path));lib.gawn10_cofactor.argtypes=[ctypes.POINTER(Site),ctypes.c_int,ctypes.c_int,ctypes.POINTER(Site)]
    lib.gawn10_cofactor.restype=ctypes.c_int
    lib.gawn10_campaign.argtypes=[ctypes.c_int]*6+[ctypes.POINTER(ctypes.c_int),ctypes.POINTER(Site),
        ctypes.POINTER(Site),ctypes.POINTER(ctypes.c_int),ctypes.POINTER(Result)]
    lib.gawn10_campaign.restype=ctypes.c_int
    return lib,path
def geometry():
    delta=np.arange(1,k.Q,dtype=np.int32);d=hashlib.sha256();count=low=negative=0
    for b in range(k.Q):
        r=(b-3+delta)%k.Q;ell=np.where(r<=5,b-3-r,b-3).astype(np.int16)
        assert np.all(ell>=b-8) and np.all(ell<=b-3)
        assert np.all((ell[r<=5]+delta[r<=5])%k.Q==0)
        d.update(ell.tobytes());count+=len(delta);low+=int(np.count_nonzero(r<=5));negative+=int(np.count_nonzero(ell<0))
    assert (count,low,negative)==(16773120,24570,12300)
    return dict(all_legal_b_delta_pairs=count,low_phase_extended_bound_pairs=low,
        conservative_left_neighbor_allowance_pairs=negative,min_ell_minus_b=-8,max_ell_minus_b=-3,
        all_b_delta_bound_formula_checked=True,ell_array_sha256=d.hexdigest())
def actual_check(lib,rng,x,delta,age,rows,dig):
    cells={};raw=(Site*17)()
    for j in range(-8,9):
        v=rows[j+8];raw[j+8]=Site(*map(int,v))
        native=dict(addr=(x+j+delta*int(v[0]))%k.Q,age=age,
            **{name:int(v[h+1]) for h,name in enumerate(('f1','f2','wf1','wf2'))})
        cells[j]=k.Cell(**native,**{name:tuple(rng.getrandbits(WIDTHS.get(name,k.WORD)) for _ in k.SLOTS) for name in SF})
    result=Site();assert lib.gawn10_cofactor(raw,x,delta,ctypes.byref(result))==0
    actual=k.local_transition(cells,own.ROM)
    got=[getattr(actual,name) for name in k.NATIVE_NAMES]
    expected=[(x+delta*result.foreign)%k.Q,(age+1)%k.U,result.f1,result.f2,0,0]
    assert got==expected,(x,delta,age,got,expected)
    add(dig,[x,delta,age,[[hex(v) for v in k.cell_words(cells[j])] for j in range(-8,9)],got])
    return got
def random_cofactors(lib):
    rng=random.Random(0x4741574e313001);d=hashlib.sha256()
    ages=(T0,T0+103,T0+4100,k.U-1)
    phases=(-k.Q-1,-k.Q,-8,-3,-1,0,1,2,3,4,5,17,k.Q-6,k.Q-3,k.Q-1,k.Q,k.Q+1)
    shifts=(1,3,5,8,104,2048,k.Q-1)
    for index in range(640):
        x=phases[index%len(phases)];delta=shifts[index%len(shifts)] if index<320 else rng.randrange(1,k.Q)
        rows=[[rng.randrange(2) for _ in range(5)] for _ in range(17)]
        actual_check(lib,rng,x,delta,ages[index%len(ages)],rows,d)
    return dict(selected_full_physical_kernel_comparisons=640,all13_SF_arbitrary_selected=True,
        common_clocks_retained=True,arbitrary_binary_offset_label_and_four_flag_patterns_selected=True,
        inputs_outputs_sha256=d.hexdigest())
def campaigns(lib,out,write):
    rng=random.Random(0x4741574e313002);dig=hashlib.sha256();records=[];assets={};snap_checks=0
    positions=np.arange(OFFSET,OFFSET+N,dtype=np.int32)
    for b in (0,k.Q-104):
        for burst_rows in (1,104):
            for flags in range(16):
                delta=(3-b+flags)%k.Q if flags<6 else (1,104,2048,k.Q-1)[flags%4]
                assert delta
                events=np.zeros((burst_rows+LIMIT,10),dtype=np.int32)
                final=(Site*N)();snaps=(Site*(8*N))();snap_rows=(ctypes.c_int*8)();result=Result()
                status=lib.gawn10_campaign(b,104,delta,flags,burst_rows,LIMIT,
                    events.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),final,snaps,snap_rows,ctypes.byref(result))
                assert status>=0,(b,delta,flags,burst_rows,status,result.steps)
                trace=events[:result.steps+1].copy()
                labels=np.frombuffer(final,dtype=np.uint8).reshape(N,5).copy()
                snapshots=np.frombuffer(snaps,dtype=np.uint8).reshape(8,N,5)[:result.snapshots].copy()
                snapshot_steps=np.asarray(list(snap_rows)[:result.snapshots],dtype=np.int32)
                r=(b-3+delta)%k.Q;ell=b-3-r if r<=5 else b-3
                native=np.column_stack(((positions+delta*labels[:,0])%k.Q,
                    np.full(N,T0+result.steps,dtype=np.uint32),labels[:,1:])).astype(np.uint32)
                # These checks concern the whole saved native rows. No SF future tape is supplied.
                for snapshot,step in zip(snapshots,snapshot_steps):
                    assert not np.any(snapshot[positions<ell,0]) and not np.any(snapshot[positions>=k.Q,0])
                    assert not np.any(snapshot[positions<b-3,2]) and not np.any(snapshot[positions>=k.Q,2])
                    assert not np.any(snapshot[(positions<-k.Q)|(positions>=k.Q),1])
                    if step>=burst_rows:assert not np.any(snapshot[:,3:])
                    for x in (ell,b if int(step)%2 else k.Q-1):
                        i=x-OFFSET
                        actual_check(lib,rng,x,delta,T0+int(step),snapshot[i-8:i+9],dig);snap_checks+=1
                elapsed=trace[:,0]-(burst_rows-1)
                assert not np.any(trace[elapsed>=1,6:8])
                assert not np.any(trace[elapsed>=k.Q-b+4,5])
                if status==0:
                    assert result.gf_quiet>0 and result.native_quiet>0
                    assert np.array_equal(native[:,0],positions%k.Q) and not np.any(native[:,2:])
                    assert result.native_quiet<=max(result.gf_quiet,k.Q-b+4)+k.Q//2
                name=f'GAWN10_b{b}_rows{burst_rows}_flags{flags:02d}_native.npz'
                arrays=dict(events=trace,final_native=native,native_snapshots=snapshots,snapshot_steps=snapshot_steps)
                path=out/name
                if write:np.savez_compressed(path,**arrays)
                else:
                    with np.load(path) as old:
                        assert set(old.files)==set(arrays),name
                        for key,value in arrays.items():assert np.array_equal(old[key],value),(name,key)
                assets[str(path.relative_to(ROOT))]=sha(path)
                records.append(dict(b=b,width=104,delta=delta,flags=flags,burst_rows=burst_rows,ell=ell,
                    **{name:getattr(result,name) for name,_ in result._fields_},
                    events_sha256=hashlib.sha256(trace.tobytes()).hexdigest(),
                    final_native_sha256=hashlib.sha256(native.tobytes()).hexdigest(),
                    snapshots_sha256=hashlib.sha256(snapshots.tobytes()+snapshot_steps.tobytes()).hexdigest()))
                print(json.dumps(dict(case=len(records),b=b,delta=delta,flags=flags,rows=burst_rows,
                    status=status,gf_quiet=result.gf_quiet,native_quiet=result.native_quiet)),flush=True)
    assert len(records)==64
    return dict(cases=64,all64_full_native_recovery_measured=all(r['status']==0 for r in records),
        max_measured_Address_quiet=max(r['gf_quiet'] for r in records),
        max_measured_full_native_quiet=max(r['native_quiet'] for r in records),
        max_wrong_Address_count=max(r['max_gf'] for r in records),
        min_measured_wrong_Address_x=min(r['min_gf'] for r in records),
        max_measured_wrong_Address_x=max(r['max_gf_x'] for r in records),
        selected_evolving_native_snapshot_full_kernel_comparisons=snap_checks,
        snapshot_inputs_outputs_sha256=dig.hexdigest(),records=records,asset_sha256=assets)
def compute(out,write=False):
    with tempfile.TemporaryDirectory(prefix='gawn10_projection_') as tmp:
        lib,binary=library(tmp);g=geometry();c=random_cofactors(lib);p=campaigns(lib,out,write)
        binary_sha=sha(binary)
    sources=(Path(__file__),HERE/'gawn10_two_offset_projection.c',HERE/'GAWN10_TWO_OFFSET_NATIVE_EXTERIOR.md',
        HERE.parent/'unregistered_gawn2/small_rule_gawn2.py',HERE.parent/'unregistered_gawn2/small_compositional_cost.py')
    return dict(name='GAWN10 unchanged GAWN2 late common-clock/two-offset native projection',passed=True,
        Q=k.Q,U=k.U,lambda_original=24,error_separation=104,first_fault_row=T0,max_width=104,max_rows=104,
        one_true_colony_support_required=True,retained_correct_Age_required=True,
        fixed_global_two_Address_offsets_required=True,all_four_flags_all13_SF_arbitrary_legal=True,
        no_other_errors=True,computed_Workspace_guard_actually_closed=True,
        universal_native_projection_and_exterior_proved=True,wrong_Address_left_allowance=8,
        conditional_Address_correct_row_implies_full_native_repair_proved=True,
        conditional_full_native_deadline_within_current_U_required=True,
        universal_Workspace_zero_after_last_fault=1,universal_Flag2_zero_after_last_fault_at_most=4100,
        universal_Address_termination_for_this_class_proved=False,
        full_SF_confinement_completeU_2U_or_iid_proved=False,
        general_arbitrary_GF_clock_E0_surroundings_higher_iid_proved=False,
        faithful_Gray_G17_refutation_shorterU_or_minimum_proved=False,
        full_SF_evolution_or_complete2U_physical_simulation_performed=False,
        rule_ROM_constants_G17_changed=False,geometry=g,random_full_kernel=c,selected_native_histories=p,
        C_shared_object_sha256=binary_sha,
        C_compiler_version=subprocess.check_output(['gcc','--version'],text=True).splitlines()[0],
        source_sha256={str(path.relative_to(ROOT)):sha(path) for path in sources})
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    out=ROOT/'figs/gray_counterexamples/unregistered_gawn10';out.mkdir(parents=True,exist_ok=True)
    start=time.perf_counter();certificate=compute(out,args.write)
    path=out/'GAWN10_two_offset_native_certificate.json'
    if args.write:path.write_text(json.dumps(certificate,indent=2)+'\n')
    else:assert certificate==json.loads(path.read_text()),'Fresh finite transcriptions differ from receipt'
    print(json.dumps(dict(passed=True,cases=64,all_native_recovery_measured=certificate['selected_native_histories']['all64_full_native_recovery_measured'],
        geometry_pairs=certificate['geometry']['all_legal_b_delta_pairs'],
        random_full_kernel=640,evolving_snapshot_kernel=certificate['selected_native_histories']['selected_evolving_native_snapshot_full_kernel_comparisons'],
        max_measured_GFquiet=certificate['selected_native_histories']['max_measured_Address_quiet'],
        max_measured_nativequiet=certificate['selected_native_histories']['max_measured_full_native_quiet'],
        universal_GFtermination=False,full_reliability=False,elapsed=time.perf_counter()-start)),flush=True)
if __name__=='__main__':main()
