"""Transcription/arithmetic supplements to the universal written GAWN16 proof."""
from pathlib import Path
import ctypes,hashlib,json,random,subprocess,sys,tempfile
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
OUT=ROOT/'figs/gray_counterexamples/unregistered_gawn16'
sys.path.insert(0,str(HERE.parent/'unregistered_gawn10'))
import check_gawn10_two_offset_projection as c
Q=c.k.Q;PAIRS=[(-8,8),(-6,8),(-3,8),(-1,1),(1,1),(4,1)]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def geometry_and_reachability():
    ds=np.arange(1,Q,dtype=np.int32);bounds=hashlib.sha256();small=hashlib.sha256()
    counts=[0,0,0];small_pairs=[];maximum=-1;max_GF=-1;arg=None;lowrecords=[]
    for b in range(Q):
        r=(b-3+ds)%Q;ell=np.where(r<=5,b-3-r,b-3);s=Q-ds
        low=(ell<=0)&(r<=5)
        assert np.all(ell[low]==-ds[low]);assert np.all((3<=b+ds[low])&(b+ds[low]<=8))
        assert np.all(((ell==s)|(r>=6)|low))
        counts[0]+=int(np.count_nonzero(ell>=1))
        counts[1]+=int(np.count_nonzero((ell<=0)&~low));counts[2]+=int(np.count_nonzero(low))
        effective=np.where(low,ell+6,ell)
        assert np.all((effective==s)|(effective<s)|(effective>=s+6))
        assert np.all(((effective+ds)%Q>=6)|(effective==s))
        H=(np.maximum(0,s-effective)+2)//3
        G=np.where(effective>=s+6,(Q-effective+2)//3,H+np.maximum(1,ds-2)+(ds+2)//3)
        N=Q-b+4+G+Q//2
        rows=np.column_stack((ds,r,ell,effective,s,G,N)).astype('<i4')
        bounds.update(np.array([b],dtype='<i4').tobytes());bounds.update(rows.tobytes())
        j=int(N.argmax());max_GF=max(max_GF,int(G.max()))
        if int(N[j])>maximum:
            maximum=int(N[j]);arg=dict(b=b,delta=int(ds[j]),ell=int(ell[j]),r=int(r[j]),
                effective_prefix=int(effective[j]),s=int(s[j]),Flag2_deadline=Q-b+4,
                GF_further_deadline=int(G[j]),native_deadline=maximum)
        for delta in ds[low].tolist():
            small_pairs.append([b,delta]);assert 1<=delta<=8 and 0<=b<=7
            for width in range(1,105):
                assert b+width<=Q
                for D in range(104):
                    ell0=-delta;R0=b+width+3*D;T=R0-ell0;W=max(T,10-b-delta)
                    upper=R0+3*(W+2);margin=(Q-delta)-upper
                    front=b-3+W-1;N2=Q-b+4
                    assert 1<=T<=421 and T<=W<=421
                    assert margin>=2406 and front>=ell0+6
                    assert W+2<=423<N2 and (Q-delta-(ell0+6)+2)//3==1364
                    row=[b,delta,width,D,R0,T,W,upper,margin,front,N2]
                    lowrecords.append(row)
                    small.update(np.array(row,dtype='<i4').tobytes())
    assert counts==[16756730,16357,33] and len(small_pairs)==33 and len(lowrecords)==356928
    assert sum(counts)==Q*(Q-1)==16773120 and maximum==11608 and max_GF==5460
    assert c.T0+103+maximum==421313 and 4*Q-103-maximum==4673
    return dict(all_geometry_pairs=sum(counts),positive_ell_pairs=counts[0],
        nonpositive_ordinary_phase_pairs=counts[1],nonpositive_low_phase_pairs=counts[2],
        low_phase_pairs=small_pairs,small_boundary_b_delta_width_D_cases=len(lowrecords),
        maximum_tag_fill=max(v[5] for v in lowrecords),maximum_wait=max(v[6] for v in lowrecords),
        maximum_short_window_end=max(v[6]+2 for v in lowrecords),
        minimum_foreign_right_boundary_margin=min(v[8] for v in lowrecords),
        minimum_local_Flag2_front_surplus=min(v[9]-(-v[1]+6) for v in lowrecords),
        minimum_N2_minus_crossing_time=min(v[10]-v[6]-2 for v in lowrecords),
        maximum_GF_further_deadline=max_GF,maximum_native_deadline=maximum,maximizer=arg,
        latest_native_quiet=421313,slack_to_first_fault4Q=4673,
        all_geometry_bound_rows_sha256=bounds.hexdigest(),small_reachability_rows_sha256=small.hexdigest())

def compute(issue=False):
    with tempfile.TemporaryDirectory(prefix='gawn16_tags_') as tmp:
        binary=Path(tmp)/'tags.so'
        subprocess.run(['gcc','-O3','-std=c11','-fPIC','-shared',str(HERE/'gawn16_arbitrary_flag2_tags.c'),
            '-o',str(binary)],check=True)
        lib=ctypes.CDLL(str(binary));fn=lib.gawn16_tag_table
        fn.argtypes=[ctypes.POINTER(ctypes.c_uint8)];fn.restype=ctypes.c_int
        values=np.zeros(6*32*32*64*64*2,dtype=np.uint8)
        assert fn(values.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)))==len(values)
        table=values.reshape(6,32,32,64,64,2);tagged=prefix=front=0
        for right in range(32):
            for flags in range(64):
                if not(right&~flags):
                    entries=table[:,:,right,flags,:,:]
                    assert np.all(((entries&1)==0)|((entries&2)!=0));tagged+=entries.size
                    for left in range(32):
                        if left.bit_count()<3:
                            row=table[:,left,right,flags,:,:];mask=(row&4)==0
                            assert not np.any(row[mask]&1);prefix+=int(mask.sum())
        for f2 in(0,32):
            entries=table[:,:,:,:,f2,0];assert not np.any(entries&4);front+=entries.size
        native,native_binary=c.library(tmp);rng=random.Random(0x4741574e313601);dig=hashlib.sha256()
        ages=(c.T0,c.T0+103,c.T0+423,c.T0+4100,c.k.U-1)
        for index in range(480):
            k=index%6;x,delta=PAIRS[k]
            left=rng.randrange(32);right=rng.randrange(32);flags=rng.randrange(64)
            f2=rng.randrange(64);ws=rng.randrange(2)
            rows=[[0,rng.randrange(2),rng.randrange(2),ws,ws] for _ in range(17)]
            rows[8][1]=(flags>>5)&1;rows[8][2]=(f2>>5)&1
            for j in range(1,6):
                rows[8-j][0]=(left>>(j-1))&1;rows[8+j][0]=(right>>(j-1))&1
                rows[8+j][1]=(flags>>(j-1))&1;rows[8-j][2]=(f2>>(j-1))&1
            got=c.actual_check(native,rng,x,delta,ages[(index//6)%5],rows,dig)
            expected=int(table[k,left,right,flags,f2,ws])
            assert got[0]==(x+delta*(expected&1))%Q and got[2]==((expected>>1)&1)
            assert got[3]==((expected>>2)&1) and got[4:]==[0,0]
        path=OUT/'GAWN16_arbitrary_Flag2_tag_table.npz'
        if issue:
            assert not path.exists();np.savez_compressed(path,native=values)
        else:
            with np.load(path,allow_pickle=False) as saved:
                assert saved.files==['native'] and np.array_equal(saved['native'],values)
        metrics=dict(exhaustive_native_cofactors=len(values),phase_pairs=[list(p) for p in PAIRS],
            left_GF_patterns=32,right_GF_patterns=32,self_right_Flag1_patterns=64,
            self_left_Flag2_patterns=64,raw_Workspace_modes=2,
            five_right_tagged_cofactors=tagged,tagged_canonical_left_zero_computed_Flag2_cofactors=prefix,
            all_zero_left_Flag2_prefix_cofactors=front,
            all_tag_and_local_front_implications_checked=True,
            native_table_sha256=hashlib.sha256(values.tobytes()).hexdigest(),
            full_kernel_comparisons=480,full_kernel_inputs_outputs_sha256=dig.hexdigest(),
            full_kernel_ages=list(ages),C_shared_object_sha256=sha(binary),
            inherited_native_C_shared_object_sha256=sha(native_binary))
    sources=(Path(__file__),HERE/'gawn16_arbitrary_flag2_tags.c',HERE/'GAWN16_ALL_LATE_TWO_OFFSET_NATIVE_REPAIR.md',
        HERE/'validate_gawn16_all_late_native.py',
        HERE.parent/'unregistered_gawn10/gawn10_two_offset_projection.c',
        HERE.parent/'unregistered_gawn10/check_gawn10_two_offset_projection.py',
        HERE.parent/'unregistered_gawn2/small_rule_gawn2.py',
        HERE.parent/'unregistered_gawn2/small_compositional_cost.py')
    return dict(name='GAWN16 every stated late adaptive two-offset native burst repairs',passed=True,
        Q=Q,U=c.k.U,lambda_original=24,error_separation=104,first_fault_row=c.T0,
        unchanged_GAWN2_all_Gray_departures_required=True,
        all_J279_actual_H2_late_adaptive104site104row_correctAge_two_fixed_offsets_required=True,
        no_other_errors_required=True,all_four_flags_all13SF_arbitrary=True,
        positive_ell_nativequiet_requirement_removed=True,
        three_site_GF_support_cone_through_faults_proved=True,
        arbitrary_Flag2_Workspace_five_right_tag_proved=True,
        all33_low_phase_small_burst_reachability_crossing_persistence_proved=True,
        universal_stated_GF_and_full_native_deadline11608_proved=True,
        actual_U_encoding_for_all_stated_bursts_by_proved_confinement=True,
        positive_ell_complete2U_all_later_equality_by_proved_pair_composition=True,
        nonpositive_ell_actual_upper_triple_boundary_reduction_proved=True,
        nonpositive_ell_upper_triple_complete_or_eventual_repair_proved=False,
        general_clocks_offsets_earlier_E0_higher_iid_proved=False,
        actual_admitted_burst_Gray_G17_iid_or_bitfailure_counterexample_proved=False,
        fullSF_evolution_or_fullperiod_physical_simulation_performed=False,
        rule_ROM_constants_G17_changed=False,native=metrics,geometry=geometry_and_reachability(),
        source_sha256={str(p.relative_to(ROOT)):sha(p) for p in sources},
        array_sha256={str(path.relative_to(ROOT)):sha(path)})
