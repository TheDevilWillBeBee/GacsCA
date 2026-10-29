"""Finite supplements for the written common-clock/many-offset lemma.

Neither native recovery on all Address patterns nor complete SF/iid repair
is certified by this checker. The exact projection is proved in the text.
"""
import argparse, hashlib, json, random, sys, tempfile, time
from pathlib import Path
import numpy as np
import explore_gawn25 as e

HERE=e.HERE; ROOT=e.ROOT; Q=e.Q; U=e.U; T0=e.T0
OUT=ROOT/'figs/gray_counterexamples/unregistered_gawn25'
PARENT=ROOT/'figs/gray_counterexamples/unregistered_gawn24/GAWN24_standalone_assets.json'
from gacsca.gray_errors import classify

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def add(d,x):d.update((json.dumps(x,separators=(',',':'))+'\n').encode())
def rows(a):return [[int(v[n]) for n in e.DT.names] for v in a]

def error_classes():
    result=[]
    for b in (0,Q-52):
        for duration in (1,104):
            E={(b+i,T0+s) for i in range(104) for s in range(duration)}
            got=classify(E,E,Q=Q,U=U,exact_limit=1,sep=104)
            assert got['level0']==0 and got['candidate_level1'] and got['level1']
            assert got['method']=='window' and got['extent']==(104,duration)
            result.append(dict(b=b,width=104,duration=duration,
                actual_declared_error_points=len(E),classification=got))
    # Canonical JSON avoids the classifier's tuple/list serialization issue.
    return json.loads(json.dumps(result))

def flag_fronts(lib):
    d=hashlib.sha256();n=0
    import ctypes
    for phase in range(Q):
        for count in (0,1):
            for field in ('f1','f2'):
                a=(e.Site*11)()
                if field=='f1':
                    a[5].f1=1
                    for j in range(-5,6):a[5+j].f2=1
                    if count and phase+1<Q:a[6].f1=1
                else:
                    a[5].f2=1
                    for j in range(-5,0):
                        # All out-of-colony flags are allowed to be 1;
                        # they are masked when newFlag1=0.
                        if phase+j<0 or (count and j==-1):a[5+j].f2=1
                got=e.Site()
                assert lib.gawn25_local(a,phase,T0,ctypes.byref(got))==0
                assert getattr(got,field)==0 and got.offset==0
                add(d,[phase,count,field,[[getattr(v,f) for f in e.DT.names] for v in a],
                    [getattr(got,f) for f in e.DT.names]])
                n+=1
    assert n==4*Q
    return dict(selected_front_kernels=n,all4096_Address_phases_checked=True,
        eligible_source_count_zero_or_one=True,inputs_outputs_sha256=d.hexdigest(),
        universal_front_and_Q_deadline_proof_is_written_not_exhaustive_histories=True)

def campaign(lib,write):
    records=[];assets={};rng=random.Random(0x4741574e323502)
    dig=hashlib.sha256();evolving=0
    for b in (0,Q-52):
        for label,offsets in e.profiles(b).items():
            for duration in (1,104):
                for flags in (0,3,12,15):
                    forcing=np.zeros((duration,104),dtype=e.DT)
                    forcing['offset']=offsets
                    for bit,name in enumerate(('f1','f2','wf1','wf2')):
                        forcing[name]=(flags>>bit)&1
                    rec,trace,native=e.run(lib,forcing,b,4*Q)
                    rec.pop('elapsed')
                    assert rec['status']==0 and rec['steps']<4*Q
                    assert not any(np.any(native[n]) for n in e.DT.names)
                    gf_wrong=trace[:,1]>0
                    gfquiet=int(trace[gf_wrong,0].max()+1) if np.any(gf_wrong) else 0
                    rec.update(b=b,width=104,profile=label,duration=duration,flags=flags,
                        Address_quiet_step=gfquiet,
                        no_quorum_input_updates=int(trace[:,10].sum()),
                        periodic_source3_updates=int(trace[:,11].sum()),
                        distinct_input_offsets=sorted(map(int,np.unique(offsets))),
                        trace_sha256=hashlib.sha256(trace.tobytes()).hexdigest(),
                        forcing_sha256=hashlib.sha256(forcing.tobytes()).hexdigest(),
                        final_sha256=hashlib.sha256(native.tobytes()).hexdigest())
                    name=f'GAWN25_b{b}_{label}_d{duration:03d}_f{flags:02d}.npz'
                    path=OUT/name
                    arrays=dict(forcing=forcing,events=trace,final=native)
                    if write:np.savez_compressed(path,**arrays)
                    else:
                        with np.load(path) as old:
                            assert set(old.files)==set(arrays),name
                            for key,value in arrays.items():
                                assert np.array_equal(old[key],value),(name,key)
                    assets[str(path.relative_to(ROOT))]=sha(path)
                    records.append(rec)
                    if duration==104 and flags in (0,15):
                        for checkpoint in (1,14,104):
                            short,prefix,snapshot=e.run(lib,forcing,b,checkpoint)
                            assert np.array_equal(prefix,trace[:short['steps']+1])
                            for x in (b-3,b+52,b+106):
                                i=x-short['base'];assert 8<=i<len(snapshot)-8
                                e.actual_check(lib,rows(snapshot[i-8:i+9]),x,
                                    (T0+short['steps'])%U,rng,dig)
                                evolving+=1
                    if len(records)%16==0:
                        print(json.dumps(dict(cases=len(records),all_native_recovered_so_far=True,
                            max_native_quiet=max(r['steps'] for r in records),
                            source3_updates=sum(r['periodic_source3_updates'] for r in records))),flush=True)
    assert len(records)==128 and evolving==288
    return dict(cases=128,all_selected_native_recovered=True,
        maximum_measured_Address_quiet_step=max(r['Address_quiet_step'] for r in records),
        maximum_measured_native_quiet_step=max(r['steps'] for r in records),
        total_no_quorum_input_updates=sum(r['no_quorum_input_updates'] for r in records),
        total_periodic_source3_updates=sum(r['periodic_source3_updates'] for r in records),
        evolving_native_full_kernel_comparisons=evolving,
        evolving_kernel_inputs_outputs_sha256=dig.hexdigest(),records=records,asset_sha256=assets)

def compute(write):
    with tempfile.TemporaryDirectory(prefix='gawn25_checked_') as tmp:
        lib=e.library(tmp)
        kernels=e.cofactors(lib,count=768)
        fronts=flag_fronts(lib)
        classes=error_classes()
        histories=campaign(lib,write)
    sources=(Path(__file__),HERE/'explore_gawn25.py',HERE/'gawn25_many_offset_native.c',
        HERE/'GAWN25_MANY_OFFSET_COMMON_CLOCK_PROJECTION.md',
        HERE.parent/'unregistered_gawn2/small_rule_gawn2.py',
        HERE.parent/'unregistered_gawn2/small_compositional_cost.py',
        ROOT/'gacsca/gray_errors.py',PARENT)
    return dict(name='GAWN25 unchanged GAWN2 common-clock arbitrary-Address closed-Workspace native projection',
        passed=True,Q=Q,U=U,lambda_original=24,error_separation=104,
        unchanged_GAWN2_all_Gray_departures_required=True,
        universal_projection_all_legal_GF_and_four_flags_all_SF_proved=True,
        correct_common_Age_and_closed_actual_computed_Workspace_guard_required=True,
        fixed_two_offset_or_existence_of_GF_majority_assumed=False,
        all_native_offsets_copied_from_old_offsets_or_faults_proved=True,
        exact_radius5_native_causal_cone_proved=True,
        Address_correct_global_row_implies_native_quiet_within_Qplus1_proved=True,
        conditional_deadline_requires_no_further_faults_and_closed_guard=True,
        actual_H2_first_fault_after_row=T0,
        declared_finite_error_sets_classified_exactly=True,
        full_SF_or_physical_U2U_trajectory_simulated=False,
        universal_arbitrary_GF_termination_or_exterior_bound_proved=False,
        arbitrary_Age_open_guard_multiple_E0_higher_iid_memory_proved=False,
        faithful_Gray_G17_refutation_or_minimum_sufficient_fix_proved=False,
        global_reliability_proved=False,rule_ROM_constants_CURRENT_changed=False,
        selected_kernel_supplements=kernels,conditional_front_supplements=fronts,
        finite_error_set_classes=classes,selected_native_histories=histories,
        source_sha256={str(p.relative_to(ROOT)):sha(p) for p in sources})

def main():
    p=argparse.ArgumentParser();p.add_argument('--issue',action='store_true');args=p.parse_args()
    start=time.perf_counter();OUT.mkdir(parents=True,exist_ok=True)
    parent=json.loads(PARENT.read_text());assert len(parent['assets_sha256'])==780
    for path,value in parent['assets_sha256'].items():assert sha(ROOT/path)==value,path
    cp=OUT/'GAWN25_many_offset_certificate.json';mp=OUT/'GAWN25_standalone_assets.json'
    if args.issue:
        assert not cp.exists() and not mp.exists()
        result=compute(True);cp.write_text(json.dumps(result,indent=2)+'\n')
        assets=dict(parent['assets_sha256'])
        assets.update(result['source_sha256']);assets.update(result['selected_native_histories']['asset_sha256'])
        assets[str(cp.relative_to(ROOT))]=sha(cp)
        manifest=dict(name=result['name'],inherited_assets=780,assets_sha256=assets,
            common_clock_many_offset_closed_native_projection_proved=True,
            universal_Address_termination_proved=False,global_reliability_proved=False,
            rule_ROM_constants_CURRENT_changed=False)
        mp.write_text(json.dumps(manifest,indent=2)+'\n')
    else:
        manifest=json.loads(mp.read_text())
        for path,value in parent['assets_sha256'].items():assert manifest['assets_sha256'][path]==value,path
        for path,value in manifest['assets_sha256'].items():assert sha(ROOT/path)==value,path
        result=compute(False)
        assert result==json.loads(cp.read_text()),'Fresh finite supplements differ'
    for path,value in manifest['assets_sha256'].items():assert sha(ROOT/path)==value,path
    print(json.dumps(dict(passed=True,issued=args.issue,readonly=not args.issue,
        assets=len(manifest['assets_sha256']),inherited_assets=780,
        all_new_finite_supplements_recomputed=True,
        common_clock_many_offset_closed_native_projection_proved=True,
        universal_Address_termination_proved=False,global_reliability_proved=False,
        rule_ROM_constants_CURRENT_changed=False,certificate_sha256=sha(cp),
        manifest_sha256=sha(mp),elapsed=time.perf_counter()-start)),flush=True)
if __name__=='__main__':main()
