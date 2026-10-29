"""Finite supplements and replay of GAWN13's separately scoped proof."""
from pathlib import Path
import argparse,ctypes,hashlib,json,random,subprocess,sys,tempfile,time
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(HERE.parent/'unregistered_gawn10'))
import check_gawn10_two_offset_projection as c
Q=c.k.Q;OUT=ROOT/'figs/gray_counterexamples/unregistered_gawn13'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def encoded(value):return json.dumps(value,separators=(',',':')).encode()

def graph():
    def successors(state):
        z=lambda p:(state>>p)&1 if 0<=p<10 else 0
        forced=free=0
        for p in range(10):
            left=sum(z(p-j) for j in range(1,6))>=3
            forced|=int(left)<<p
            if p>=5:continue
            right=sum(z(p+j) for j in range(1,6))>=3
            mismatch=sum(1-z(p-j) for j in range(1,p+1))>=3
            if right and not left and not mismatch:free|=1<<p
        bits=[1<<p for p in range(5) if free>>p&1]
        return sorted(forced|sum(v for j,v in enumerate(bits) if mask>>j&1)
                      for mask in range(1<<len(bits)))
    full={s:successors(s) for s in range(1024)}
    states=[s for s in full if not(s&(s>>1)&(s>>2))]
    adj={s:[t for t in full[s] if not(t&(t>>1)&(t>>2))] for s in states}
    seen=set();finished=[]
    def dfs(v):
        seen.add(v)
        for t in adj[v]:
            if t not in seen:dfs(t)
        finished.append(v)
    for s in states:
        if s not in seen:dfs(s)
    reverse={s:[] for s in states}
    for s,targets in adj.items():
        for t in targets:reverse[t].append(s)
    seen=set();components=[]
    def dfs2(v,component):
        seen.add(v);component.append(v)
        for t in reverse[v]:
            if t not in seen:dfs2(t,component)
    for s in reversed(finished):
        if s not in seen:
            component=[];dfs2(s,component);components.append(sorted(component))
    cycles=sorted(v for v in components if len(v)>1 or v[0] in adj[v[0]])
    nonzero=[v for v in cycles if v!=[0]]
    assert len(states)==504 and sum(map(len,adj.values()))==831
    assert len(nonzero)==7 and sum(map(len,nonzero))==14
    assert [341,682] in nonzero and all(len(v)==2 for v in nonzero)
    return dict(full_GF_states=1024,full_overapproximation_edges=sum(map(len,full.values())),
        no111_states=504,no111_edges=831,nonzero_two_cycles=nonzero,
        nonzero_cyclic_states=14,zero_self_loop=True,
        full_graph_sha256=hashlib.sha256(encoded(list(full.items()))).hexdigest(),
        no111_graph_sha256=hashlib.sha256(encoded(list(adj.items()))).hexdigest(),
        actual_Flag1_evolution_or_CA_cycle_reachability_proved=False)

def sparse_replay(lib):
    fn=lib.gawn13_run
    fn.argtypes=[ctypes.POINTER(c.Site),ctypes.c_int,ctypes.c_int,
        ctypes.POINTER(ctypes.c_int),ctypes.POINTER(c.Site),ctypes.POINTER(ctypes.c_int)]
    fn.restype=ctypes.c_int
    old=json.loads((OUT/'GAWN13_sparse_native_probe.json').read_text());records=[]
    dig=hashlib.sha256();limit=12000
    for b in (0,1,5,64,3992):
        for width in (9,10,31,64,104):
            for delta in sorted({1,2,3,8,(Q-b)%Q or Q-1,Q//2,Q-1}):
                for flags in (0,1,2,3,8,15):
                    initial=np.zeros((c.N,5),dtype=np.uint8)
                    initial[b-c.OFFSET:b+width-c.OFFSET:2,0]=1
                    for k in range(4):initial[b-c.OFFSET:b+width-c.OFFSET,k+1]=(flags>>k)&1
                    events=np.zeros((limit+1,6),dtype=np.int32)
                    final=np.zeros_like(initial);summary=np.zeros(4,dtype=np.int32)
                    status=fn(initial.ctypes.data_as(ctypes.POINTER(c.Site)),delta,limit,
                        events.ctypes.data_as(ctypes.POINTER(ctypes.c_int)),
                        final.ctypes.data_as(ctypes.POINTER(c.Site)),
                        summary.ctypes.data_as(ctypes.POINTER(ctypes.c_int)))
                    assert status==summary[0]==0 and not np.any(final)
                    row=dict(b=b,width=width,delta=delta,flags=flags,status=status,
                        steps=int(summary[1]),max_wrong_GF=int(summary[2]),max_Flag1=int(summary[3]),
                        last_counts=events[summary[1]].tolist())
                    records.append(row)
                    dig.update(encoded(row));dig.update(initial.tobytes())
                    dig.update(events[:summary[1]+1].tobytes());dig.update(final.tobytes())
    assert records==old['records'] and len(records)==990
    assert old['all_selected_recovered'] and not old['fullSF_evolution_performed']
    assert not old['universal_Address_termination_Gray_G17_iid_or_bit_failure_proved']
    assert not old['rule_ROM_constants_G17_changed']
    for path,value in old['source_sha256'].items():assert sha(ROOT/path)==value,path
    return dict(cases=990,all_selected_recovered=True,all990_initial_record_values_recomputed=True,
        max_measured_full_native_quiet=max(r['steps'] for r in records),
        max_measured_wrong_GF=max(r['max_wrong_GF'] for r in records),
        native_events_initial_final_and_records_sha256=dig.hexdigest(),
        initial_receipt_sha256=sha(OUT/'GAWN13_sparse_native_probe.json'))

def compute():
    with tempfile.TemporaryDirectory(prefix='gawn13_majority_') as tmp:
        binary=Path(tmp)/'majority.so'
        subprocess.run(['cc','-O3','-std=c99','-fPIC','-shared',str(HERE/'gawn13_majority_table.c'),'-o',str(binary)],check=True)
        table_lib=ctypes.CDLL(str(binary));table_lib.gawn13_majority_table.argtypes=[ctypes.POINTER(ctypes.c_uint8)]
        table_lib.gawn13_majority_table.restype=ctypes.c_int
        values=np.zeros(4*1024*64*2,dtype=np.uint8)
        assert table_lib.gawn13_majority_table(values.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)))==len(values)
        expected=np.array([int((s&31).bit_count()>=3) for s in range(1024)],dtype=np.uint8)
        assert np.all((values.reshape(4,1024,64,2)&1)==expected[None,:,None,None])
        assert not np.any(values&28)
        majority=dict(exhaustive_native_cofactors=len(values),GF_voter_patterns=1024,
            old_Flag1_self_and_right_patterns=64,raw_Workspace1_patterns=2,phase_pairs=4,
            phase_pair_values=[[5,1],[5,Q-6],[Q-1,6],[Q-1,Q-6]],
            all_GF_equal_left_majority=True,all_Flag2_computed_Workspaces_zero=True,
            computed_Flag1_positive=int(np.count_nonzero(values&2)),
            native_table_sha256=hashlib.sha256(values.tobytes()).hexdigest(),
            C_shared_object_sha256=sha(binary))
        native,binary_native=c.library(tmp);rng=random.Random(0x4741574e313301);dig=hashlib.sha256()
        for index in range(320):
            x,delta=majority['phase_pair_values'][index%4]
            age=(c.T0,c.T0+103,c.T0+4100,c.k.U-1)[(index//4)%4]
            rows=[[rng.randrange(2),rng.randrange(2),0,rng.randrange(2),0] for j in range(17)]
            got=c.actual_check(native,rng,x,delta,age,rows,dig)
            left=int(sum(rows[8-j][0] for j in range(1,6))>=3)
            assert got[0]==(x+delta*left)%Q and got[3:]==[0,0,0]
        majority.update(selected_arbitrarySF_full_kernel_comparisons=320,
            full_kernel_inputs_outputs_sha256=dig.hexdigest(),
            inherited_native_C_shared_object_sha256=sha(binary_native))
        sparse_binary=Path(tmp)/'sparse.so'
        subprocess.run(['cc','-O3','-std=c99','-fPIC','-shared',str(HERE/'gawn13_sparse_native_probe.c'),'-o',str(sparse_binary)],check=True)
        sparse=sparse_replay(ctypes.CDLL(str(sparse_binary)))
    exceptions=[]
    for delta in range(1,Q):
        sites={x for start in (0,-delta,Q-delta) for x in range(start,start+5) if -8<=x<Q}
        assert len(sites)<=15
        exceptions.append([delta,sorted(sites)])
    assert max(len(v[1]) for v in exceptions)==15
    sources=(Path(__file__),HERE/'GAWN13_NATIVE_MAJORITY_REDUCTION.md',HERE/'gawn13_majority_table.c',
        HERE/'gawn13_sparse_native_probe.c',HERE/'check_sparse_native_probe.py',
        HERE.parent/'unregistered_gawn10/gawn10_two_offset_projection.c',
        HERE.parent/'unregistered_gawn10/check_gawn10_two_offset_projection.py',
        HERE.parent/'unregistered_gawn2/small_rule_gawn2.py',
        HERE.parent/'unregistered_gawn2/small_compositional_cost.py')
    return dict(name='GAWN13 unchanged GAWN2 ordinary native majority reduction',passed=True,
        Q=Q,U=c.k.U,lambda_original=24,error_separation=104,first_fault_row=c.T0,
        local_two_offsets_common_clock_zeroFlag2_Workspace2_required=True,
        ordinary_GF_exact_left_five_majority_proved=True,
        all_local_Flag1_Workspace1_allSF_arbitrary_admitted=True,
        J279_envelope_at_most15_exceptions_proved=True,ordinary_clean_prefix_speed3_proved=True,
        all4095_offsets_exception_geometry_checked=True,
        exception_geometry_sha256=hashlib.sha256(encoded(exceptions)).hexdigest(),
        native=majority,boundary_overapproximation=graph(),sparse_native=sparse,
        universal_actual_boundary_crossing_or_Address_termination_proved=False,
        actual_CA_cycle_admitted_burst_Gray_G17_iid_or_bitfailure_proved=False,
        fullSF_evolution_or_fullperiod_physical_simulation_performed=False,
        rule_ROM_constants_G17_changed=False,
        source_sha256={str(p.relative_to(ROOT)):sha(p) for p in sources})

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    start=time.perf_counter();result=compute()
    if args.write:
        path=OUT/'GAWN13_majority_reduction_certificate.json';assert not path.exists()
        path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,native_cofactors=result['native']['exhaustive_native_cofactors'],
        full_kernel_comparisons=320,exceptions_at_most=15,abstract_two_cycles=7,sparse_histories=990,
        measured_max_nativequiet=result['sparse_native']['max_measured_full_native_quiet'],
        universal_Address_termination=False,full_reliability=False,elapsed=time.perf_counter()-start)))
if __name__=='__main__':main()
