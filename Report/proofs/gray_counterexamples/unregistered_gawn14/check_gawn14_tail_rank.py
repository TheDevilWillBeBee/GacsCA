"""Exhaustive native-tail rank certificate, not an iid reliability theorem."""
from pathlib import Path
import ctypes,hashlib,json,random,subprocess,sys,tempfile,time
import numpy as np

HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
OUT=ROOT/'figs/gray_counterexamples/unregistered_gawn14'
sys.path.insert(0,str(HERE.parent/'unregistered_gawn10'))
import check_gawn10_two_offset_projection as c
assert sys.byteorder=='little','Receipts explicitly use little-endian arrays'
PC=np.array([x.bit_count() for x in range(32)],dtype=np.uint32)
class TailResult(ctypes.Structure):
    _fields_=[(name,ctypes.c_uint32) for name in
        ('states','max_rank','maximizer','nonzero_cycles','cycle_state','cycle_length')]+[
        ('native_comparisons',ctypes.c_uint64)]
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest(a):return hashlib.sha256(a.tobytes()).hexdigest()

def literal_next(states,delta):
    """Separate vectorized transcription of every displayed scalar equation."""
    g=states&((1<<delta)-1);f=states>>delta
    ng=np.zeros(len(states),dtype=np.uint32);nf=np.zeros_like(ng)
    for p in range(delta):
        k=min(p,5);a=PC[(g>>(p-k))&((1<<k)-1)]
        b=PC[(g>>(p+1))&31];h=PC[(f>>(p+1))&31]
        left=a>=3;right=b>=3
        mismatch=np.where(right,k-a>=3,a>=3)
        flag=mismatch|(h>=3)|(((f>>p)&1).astype(bool)&(h>=2))
        ng|=np.where(flag,left,right).astype(np.uint32)<<p
        nf|=flag.astype(np.uint32)<<p
    return ng|(nf<<delta)

def compare_literal_and_rank(successor,rank,delta,status):
    for start in range(0,len(successor),1<<19):
        stop=min(len(successor),start+(1<<19))
        state=np.arange(start,stop,dtype=np.uint32)
        assert np.array_equal(literal_next(state,delta),successor[start:stop]),(delta,start)
        if status==0:
            active=state!=0;r=rank[start:stop].astype(np.uint32)
            assert np.all(r[active]>0)
            assert np.all(r[active]==1+rank[successor[start:stop][active]].astype(np.uint32))
    if status==0:assert rank[0]==0 and successor[0]==0

def full_kernel(native):
    rng=random.Random(0x4741574e313401);dig=hashlib.sha256();comparisons=0
    ages=(c.T0,c.T0+103,c.T0+4100,c.k.U-1)
    for delta in range(1,13):
        for index in range(32):
            state=([0,(1<<(2*delta))-1,(1<<delta)-1,((1<<delta)-1)<<delta][index]
                if index<4 else rng.randrange(1<<(2*delta)))
            p=index%delta;x=c.k.Q-delta+p;g=state&((1<<delta)-1);f=state>>delta
            rows=[]
            for j in range(-8,9):
                q=p+j
                rows.append([int(g>>q&1) if 0<=q<delta else 0,
                    int(f>>q&1) if 0<=q<delta else rng.randrange(2) if q<0 else 0,0,0,0])
            got=c.actual_check(native,rng,x,delta,ages[index%4],rows,dig)
            expected=int(literal_next(np.array([state],dtype=np.uint32),delta)[0])
            assert got[0]==(x+delta*(expected>>p&1))%c.k.Q
            assert got[2]==(expected>>(delta+p)&1) and got[3:]==[0,0,0]
            comparisons+=1
    return dict(selected_arbitrarySF_literal_full_kernel_comparisons=comparisons,
        ages=list(ages),arbitrary_left_Flag1_included=True,all13_SF_arbitrary_selected=True,
        inputs_outputs_sha256=dig.hexdigest())

def pulse_arithmetic():
    # This finite check supplements, rather than replaces, the interval proof.
    records=[]
    for d in range(17,c.k.Q-7):
        n=(d+2)//3;width=d+3-2*n
        assert width>=8
        a=d;b=d+2
        for step in range(n):
            assert b-a+1>=3
            a=max(0,a-3);b-=2
        assert a==0 and b+1==width
        assert b-2>=5
        records.append([d,n,width])
    raw=json.dumps(records,separators=(',',':')).encode()
    return dict(checked_initial_triple_distances=len(records),min_d=17,max_d=c.k.Q-8,
        minimum_arrival_width=min(v[2] for v in records),minimum_next_row_end=5,
        arithmetic_sha256=hashlib.sha256(raw).hexdigest(),
        actual_triple_existence_for_universal_admitted_bursts_proved=False)

def compute(issue=False):
    assert OUT.exists();records=[];array_assets={};cycles=[]
    with tempfile.TemporaryDirectory(prefix='gawn14_tail_') as tmp:
        binary=Path(tmp)/'tail.so'
        subprocess.run(['gcc','-std=c11','-O3','-fPIC','-shared',str(HERE/'gawn14_tail_rank.c'),
            '-o',str(binary)],check=True)
        lib=ctypes.CDLL(str(binary));fn=lib.gawn14_tail_graph
        fn.argtypes=[ctypes.c_uint,ctypes.POINTER(ctypes.c_uint32),ctypes.POINTER(ctypes.c_uint16),
            ctypes.POINTER(TailResult)];fn.restype=ctypes.c_int
        for delta in range(1,13):
            start=time.perf_counter();n=1<<(2*delta)
            successor=np.zeros(n,dtype='<u4');rank=np.zeros(n,dtype='<u2');result=TailResult()
            status=fn(delta,successor.ctypes.data_as(ctypes.POINTER(ctypes.c_uint32)),
                rank.ctypes.data_as(ctypes.POINTER(ctypes.c_uint16)),ctypes.byref(result))
            assert status in(0,1),(delta,status)
            compare_literal_and_rank(successor,rank,delta,status)
            if status==0:
                assert not result.nonzero_cycles and result.max_rank==int(rank.max())
                assert result.states==n and rank[result.maximizer]==result.max_rank
                trajectory=[int(result.maximizer)]
                while trajectory[-1]:trajectory.append(int(successor[trajectory[-1]]))
                assert len(trajectory)==result.max_rank+1
            else:
                assert result.nonzero_cycles==1;trajectory=[int(result.cycle_state)]
                for _ in range(result.cycle_length):trajectory.append(int(successor[trajectory[-1]]))
                assert trajectory[0]==trajectory[-1] and all(trajectory)
                cycles.append(dict(delta=delta,cycle=trajectory))
            trajectory=np.array(trajectory,dtype='<u4')
            path=OUT/f'GAWN14_tail_delta{delta:02d}.npz'
            if issue:
                assert not path.exists(),'Never overwrite a saved finite certificate'
                np.savez_compressed(path,successor=successor,rank=rank,trajectory=trajectory)
            else:
                with np.load(path,allow_pickle=False) as saved:
                    assert set(saved.files)=={'successor','rank','trajectory'}
                    for name,values in [('successor',successor),('rank',rank),('trajectory',trajectory)]:
                        assert np.array_equal(saved[name],values),(delta,name)
            array_assets[str(path.relative_to(ROOT))]=sha(path)
            row=dict(delta=delta,states=n,status=status,all_states_absorb_at_zero=status==0,
                maximum_rank=int(result.max_rank) if status==0 else None,
                maximizer=int(result.maximizer) if status==0 else None,
                nonzero_cycle=trajectory.tolist() if status==1 else None,
                frozen_native_C_comparisons=int(result.native_comparisons),
                successor_sha256=digest(successor),rank_sha256=digest(rank),
                trajectory_sha256=digest(trajectory),array_path=str(path.relative_to(ROOT)))
            records.append(row)
            print(json.dumps(dict(delta=delta,states=n,status=status,
                max_rank=row['maximum_rank'],native_comparisons=row['frozen_native_C_comparisons'],
                seconds=time.perf_counter()-start)),flush=True)
        native,native_binary=c.library(tmp);kernels=full_kernel(native)
        binary_sha=sha(binary);native_sha=sha(native_binary)
    sources=(Path(__file__),HERE/'gawn14_tail_rank.c',HERE/'GAWN14_COUPLED_BOUNDARY_TAIL.md',
        HERE/'validate_gawn14_tail_rank.py',
        HERE.parent/'unregistered_gawn10/gawn10_two_offset_projection.c',
        HERE.parent/'unregistered_gawn10/check_gawn10_two_offset_projection.py',
        HERE.parent/'unregistered_gawn2/small_rule_gawn2.py',
        HERE.parent/'unregistered_gawn2/small_compositional_cost.py')
    return dict(name='GAWN14 exact coupled GF Flag1 right-end finite tails',passed=True,
        Q=c.k.Q,U=c.k.U,lambda_original=24,error_separation=104,first_fault_row=c.T0,
        original_unchanged_GAWN2_and_all_Gray_departures_required=True,
        common_correct_late_clock_zeroFlag2_Workspaces_no_later_errors_required=True,
        GF_canonical_left_of_Q_minus_delta_and_right_of_Q_required=True,
        right_Flag1_exterior_zero_left_Flag1_arbitrary=True,
        complete_finite_successor_arrays_and_all_rank_equalities_checked=True,
        all_delta1_through12_finite_tail_absorption_proved=not cycles,
        exact_nonzero_native_tail_cycles=cycles,
        exhaustive_states=sum(r['states'] for r in records),records=records,
        native_comparisons=sum(r['frozen_native_C_comparisons'] for r in records),
        complete_GF_Flag1_tail_rank_not_random_histories=True,
        full_kernel=kernels,pulse_arithmetic=pulse_arithmetic(),
        Flag1_packet_and_triple_conditioned_boundary_crossing_proved=True,
        universal_actual_triple_existence_general_boundary_Address_termination_proved=False,
        actual_admitted_burst_Gray_G17_iid_or_bitfailure_proved=False,
        fullSF_evolution_or_fullperiod_physical_simulation_performed=False,
        rule_ROM_constants_G17_changed=False,C_shared_object_sha256=binary_sha,
        inherited_native_C_shared_object_sha256=native_sha,
        source_sha256={str(p.relative_to(ROOT)):sha(p) for p in sources},array_sha256=array_assets)
