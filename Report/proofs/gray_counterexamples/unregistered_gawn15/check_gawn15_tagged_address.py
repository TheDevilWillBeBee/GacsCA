"""Supplement and replay for the written universal positive-ell burst proof."""
from pathlib import Path
import ctypes,hashlib,json,random,subprocess,sys,tempfile
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
OUT=ROOT/'figs/gray_counterexamples/unregistered_gawn15'
sys.path.insert(0,str(HERE.parent/'unregistered_gawn10'))
import check_gawn10_two_offset_projection as c
Q=c.k.Q
PAIRS=[(Q-1,1),(Q-2,2),(1,Q-1),(5,Q-1),(Q-6,Q-1),
       (Q-3,Q-1),(Q-1,Q-1),(Q-104,104),(Q-100,104),(Q-6,104)]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def geometry():
    ds=np.arange(1,Q,dtype=np.int32);dig=hashlib.sha256();count=0;maximum=-1;arg=None
    types=[0,0,0];max_G=0
    for b in range(Q):
        r=(b-3+ds)%Q;ell=np.where(r<=5,b-3-r,b-3);s=Q-ds;keep=ell>=1
        classification=np.where(ell==s,0,np.where(ell<s,1,2))
        assert np.all(((ell==s)|(ell<s)|(ell>=s+6))[keep])
        assert np.all(((r>=6)|(ell==s))[keep])
        assert np.all(((r==ell+ds)|(ell>=s))[keep])
        H=(np.maximum(0,s-ell)+2)//3;T=np.maximum(1,ds-2)
        G=np.where(ell>=s+6,(Q-ell+2)//3,H+T+(ds+2)//3)
        N=Q-b+4+G+Q//2
        rows=np.column_stack((ds[keep],ell[keep],s[keep],r[keep],G[keep],N[keep])).astype('<i4')
        dig.update(np.array([b,len(rows)],dtype='<i4').tobytes());dig.update(rows.tobytes())
        count+=len(rows)
        for t in range(3):types[t]+=int(np.count_nonzero(keep&(classification==t)))
        if len(rows):
            index=np.argmax(np.where(keep,N,-1));value=int(N[index]);max_G=max(max_G,int(G[keep].max()))
            if value>maximum:
                maximum=value;arg=dict(b=b,delta=int(ds[index]),ell=int(ell[index]),
                    s=int(s[index]),r=int(r[index]),Flag2_deadline=Q-b+4,
                    GF_further_deadline=int(G[index]),native_deadline=value)
    assert count==16756730 and Q*(Q-1)-count==16390 and maximum==11602
    latest=c.T0+103+maximum;assert latest==421307 and c.T0+4*Q-latest==4679
    return dict(all_geometry_pairs=Q*(Q-1),positive_ell_pairs=count,excluded_nonpositive_ell_pairs=16390,
        classification_counts=types,maximum_GF_further_deadline=max_G,maximum_native_deadline=maximum,
        maximizer=arg,latest_native_quiet=latest,slack_to_first_fault4Q=4679,
        all_geometry_bound_rows_sha256=dig.hexdigest())

def compute():
    with tempfile.TemporaryDirectory(prefix='gawn15_tags_') as tmp:
        binary=Path(tmp)/'tags.so'
        subprocess.run(['gcc','-O3','-std=c11','-fPIC','-shared',str(HERE/'gawn15_tag_table.c'),
            '-o',str(binary)],check=True)
        lib=ctypes.CDLL(str(binary));fn=lib.gawn15_tag_table
        fn.argtypes=[ctypes.POINTER(ctypes.c_uint8)];fn.restype=ctypes.c_int
        values=np.zeros(10*32*32*64,dtype=np.uint8)
        assert fn(values.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)))==len(values)
        table=values.reshape(10,32,32,64);tagged=prefix=seed=0
        for k,(x,delta) in enumerate(PAIRS):
            assert Q-delta<=x<Q
            mask=(1<<min(5,Q-1-x))-1
            for left in range(32):
                for right in range(32):
                    g=right&mask
                    for flags in range(64):
                        gf,f1=int(table[k,left,right,flags]&1),int(table[k,left,right,flags]>>1)
                        if not(g&~(flags>>1)):
                            assert not gf or f1;tagged+=1
                            if left.bit_count()<3:assert not gf;prefix+=1
                        if x>=Q-3:assert not gf or f1;seed+=1
        native,native_binary=c.library(tmp);rng=random.Random(0x4741574e313501);dig=hashlib.sha256()
        ages=(c.T0,c.T0+103,c.T0+4100,c.T0+11602,c.k.U-1)
        for index in range(400):
            k=index%len(PAIRS);x,delta=PAIRS[k]
            left=rng.randrange(32);right=rng.randrange(32);flags=rng.randrange(64)
            rows=[[0,rng.randrange(2),0,0,0] for _ in range(17)];rows[8][1]=flags&1
            for j in range(1,6):
                rows[8-j][0]=left>>(j-1)&1
                rows[8+j]=[right>>(j-1)&1,flags>>j&1,0,0,0] if x+j<Q else [0,0,0,0,0]
            got=c.actual_check(native,rng,x,delta,ages[(index//10)%5],rows,dig)
            expected=int(table[k,left,right,flags]);assert got[0]==(x+delta*(expected&1))%Q
            assert got[2]==(expected>>1) and got[3:]==[0,0,0]
        metrics=dict(exhaustive_native_cofactors=len(values),phase_pairs=[list(v) for v in PAIRS],
            five_right_tagged_cofactors=tagged,tagged_canonical_left_cofactors=prefix,
            rightmost3_seed_cofactors=seed,all_tag_seed_and_prefix_implications_checked=True,
            native_table_sha256=hashlib.sha256(values.tobytes()).hexdigest(),
            full_kernel_comparisons=400,full_kernel_inputs_outputs_sha256=dig.hexdigest(),
            full_kernel_ages=list(ages),C_shared_object_sha256=sha(binary),
            inherited_native_C_shared_object_sha256=sha(native_binary))
    sources=(Path(__file__),HERE/'gawn15_tag_table.c',HERE/'GAWN15_TAGGED_ADDRESS_PAIR_REPAIR.md',
        HERE/'validate_gawn15_tagged_address.py',
        HERE.parent/'unregistered_gawn10/gawn10_two_offset_projection.c',
        HERE.parent/'unregistered_gawn10/check_gawn10_two_offset_projection.py',
        HERE.parent/'unregistered_gawn2/small_rule_gawn2.py',
        HERE.parent/'unregistered_gawn2/small_compositional_cost.py')
    return dict(name='GAWN15 actual tagged Address positive-ell universal mixed-burst pair repair',passed=True,
        Q=Q,U=c.k.U,lambda_original=24,error_separation=104,first_fault_row=c.T0,
        unchanged_GAWN2_all_Gray_departures_required=True,
        all_J279_actual_H2_late_adaptive104site104row_correctAge_two_fixed_offsets_required=True,
        positive_ell_required=True,no_other_errors_required=True,all_four_flags_all13SF_arbitrary=True,
        five_right_tags_and_actual_suffix_deadline_proved=True,
        universal_positive_ell_GF_and_full_native_deadline_proved=True,
        actual_U_encoding_complete2U_all_later_equality_by_proved_pair_composition=True,
        native_quiet_premise_removed_for_positive_ell=True,
        nonpositive_ell_triple_general_burst_higher_iid_proved=False,
        actual_admitted_burst_Gray_G17_iid_or_bitfailure_counterexample_proved=False,
        fullSF_evolution_or_fullperiod_physical_simulation_performed=False,
        rule_ROM_constants_G17_changed=False,geometry=geometry(),native=metrics,
        source_sha256={str(p.relative_to(ROOT)):sha(p) for p in sources})
