#!/usr/bin/env python3
"""Exact duration-family native obstruction; no new self-programme/iid claim."""
from pathlib import Path
import hashlib,json,subprocess,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,Compiled,const_word
from check_g17_schedule import Terms
import proposed_sparse_distant_epoch1024 as baseline
import proposed_sparse_epoch_duration_family as family


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def full_native_cofactor(comp,p,t):
    terms=Terms();nodes=[0,1]
    zeros={'f1','f2','wf1','wf2','packet_valid','service_valid','backward_pressure'}
    for name in comp.inputs:
        if name[0]=='x':
            _,off,field,bit=name
            if field=='addr':value=((off%p.Q)>>bit)&1
            elif field=='age':value=(p.age_code(t)>>bit)&1
            elif field in zeros:value=0
            else:value=terms.var(name)
        else:value=terms.var(name)
        nodes.append(value)
    for op,a,b in comp.gates:nodes.append(terms.op(op,nodes[a],nodes[b]))
    return {field:[nodes[comp.outputs['y',field,b]] for b in range(width)]
            for field,width in (('addr',p.k),('age',p.m),('f1',1),('f2',1))}


def main():
    started=time.monotonic();out=ROOT/'figs/robustness';p=baseline.parameters()
    durations=list(range(3,190));legal=np.arange(p.U,dtype=np.int64)
    codes=np.array([p.age_code(int(t)) for t in legal],dtype=np.int64)
    clock_window_checks=0;compiled_helper_clock_checks=0;graph_rows=[];full_cofactors=0
    for m in durations:
        end=p.T_wf+m*p.Q;tail_end=end+2*p.Q
        assert tail_end<p.U
        actual=(p.age_code(p.T_wf)<=codes)&(codes<p.age_code(end))
        assert np.array_equal(actual,(p.T_wf<=legal)&(legal<end))
        clock_window_checks+=len(legal)
    for m in (3,4,189):
        n=Net();age=[n.input(('common_age',b)) for b in range(p.m)]
        cells={j:dict(addr=const_word((3+j)%p.Q,p.k),age=age) for j in range(6)}
        helper=family.epoch_helper(m*p.Q)(n,cells,p)
        assert helper['addr']==const_word(3,p.k) and helper['age']==age
        n.set_output(('force',),helper['force']);n.set_output(('birth',),helper['birth'])
        comp=Compiled(n);values={name:((codes>>name[1])&1).astype(bool) for name in comp.inputs}
        got=comp.evaluate(values,bool)
        assert np.array_equal(got['force',],(p.T_wf<=legal)&(legal<p.T_wf+m*p.Q))
        assert np.array_equal(got['birth',],legal==p.T_wf)
        compiled_helper_clock_checks+=len(legal)
        net,source=family.full_net(p,m);whole=Compiled(net)
        if m==4:assert whole.digest==baseline.cached(p)[1].digest
        times=sorted(set((p.T_wf+3*p.Q-1,p.T_wf+3*p.Q,p.T_wf+4*p.Q,
                          p.T_wf+m*p.Q-1,p.T_wf+m*p.Q,p.T_wf+(m+2)*p.Q-1)))
        for t in times:
            row=full_native_cofactor(whole,p,t)
            force=int(p.T_wf<=t<p.T_wf+m*p.Q)
            assert row['addr']==[0]*p.k
            assert row['age']==[(p.age_code((t+1)%p.U)>>b)&1 for b in range(p.m)]
            assert row['f1']==[0] and row['f2']==[force],(m,t,row)
            full_cofactors+=1
        graph_rows.append(dict(m=m,duration=m*p.Q,netlist_sha256=whole.digest,
            gates=len(whole.gates),inputs=len(whole.inputs),outputs=len(whole.outputs),
            shared_generated_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
            exact_native_free_private_cofactor_clocks=times))
    source=ROOT/'Report/proofs/native_address_epoch_duration_cycle.c'
    executable=Path('/tmp/SP28_epoch_duration_cycle_certificate')
    subprocess.run(['cc','-O3','-std=c11',str(source),'-o',str(executable)],check=True)
    run=subprocess.run([str(executable)],capture_output=True,text=True)
    log=out/'SP28_epoch_duration_cycle_run.jsonl';log.write_text(run.stdout)
    if run.returncode:
        (out/'SP28_epoch_duration_cycle_failure.json').write_text(json.dumps(dict(
            returncode=run.returncode,stderr=run.stderr,C_source_sha256=digest(source),
            run_log_sha256=digest(log),seconds=time.monotonic()-started),indent=2)+'\n')
    assert run.returncode==0,(run.returncode,run.stdout,run.stderr)
    rows=[json.loads(line) for line in run.stdout.splitlines()]
    stages=('initial','prefix3Q','prefix4Q','quiet6Q');N=256*p.Q
    frames={name:np.fromfile('/tmp/SP28_epoch_duration_'+name+'.bin',dtype=np.uint8).reshape(6,N)
            for name in stages}
    assert all(set(np.unique(a))<={0,1} for a in frames.values())
    initial,P,PQ,quiet=(frames[name] for name in stages)
    assert np.array_equal(P[1],P[2]) and np.all(P[3:5]==1) and not np.any(P[5])
    assert np.array_equal(PQ,np.roll(P,-3*p.Q,axis=1))
    assert np.array_equal(quiet,np.roll(initial,-12*p.Q,axis=1))
    assert [(r['left'],r['right_exclusive']) for r in rows[:-1]]==[
        (128*p.Q-512,144*p.Q),(119*p.Q-512,135*p.Q),
        (116*p.Q-512,132*p.Q),(116*p.Q-512,132*p.Q)]
    assert [r['distinct_quorums'] for r in rows[:-1]]==[0,36864,49152,73728]
    assert all(r['wrong_Addresses']==16896 for r in rows[:-1])
    assert rows[-1]['force_on_Q_row_translation_cycle'] and rows[-1]['tail_returns_quiet_template']
    # Full-period canonical native reference is Q-periodic; this column
    # lies outside the basis pulse's48Q influence interval.
    bulk=slice(16*p.Q,17*p.Q)
    assert not np.any(initial[:,bulk]) and not np.any(quiet[:,bulk])
    assert not np.any(P[[0,1,2,5],bulk]) and np.all(P[3:5,bulk]==1)
    old=json.loads((out/'SP28_full_Address_island_certificate.json').read_text())
    with np.load(out/'SP28_full_Address_island_states.npz') as asset:
        assert np.array_equal(initial,asset['initial']) and np.array_equal(quiet,asset['period'])
    states=out/'SP28_epoch_duration_cycle_states.npz';np.savez_compressed(states,**frames)
    dependencies=('SP28_full_Address_island_certificate.json','SP28_full_clock_island_certificate.json',
        'SP28_auxiliary_lifetime_certificate.json','SP28_native_certificate.json',
        'SP28_encoding_family_certificate.json')
    result=dict(name='Duration-only SP28 interface family still has a travelling Address island',
        Q=p.Q,U=p.U,T_wf=p.T_wf,min_m=3,max_m=189,durations_proved=len(durations),
        largest_tail_endpoint=p.T_wf+191*p.Q,Address_displacement=512,
        wrong_Address_sites_each_boundary=16896,native_translation_per_period_formula='-3*m*Q',
        family_source_sha256=digest(family.__file__),baseline_proposal_source_sha256=digest(baseline.__file__),
        written_proof_sha256=digest(Path(__file__).with_name('SP28_EPOCH_DURATION_OBSTRUCTION.md')),
        checker_sha256=digest(__file__),C_source_sha256=digest(source),C_executable_sha256=digest(executable),
        projection_source_sha256=digest(ROOT/'Report/proofs/native_address_island_auxiliary_bounds.c'),
        term_library_sha256=digest(ROOT/'Report/proofs/check_g17_schedule.py'),
        netlist_library_sha256=digest(ROOT/'gacsca/netlist.py'),
        receipt_dependencies_sha256={name:digest(out/name) for name in dependencies},
        exact_all_duration_legal_clock_window_checks=clock_window_checks,
        compiled_helper_legal_clock_cases=compiled_helper_clock_checks,
        full_graph_identity_at_m4_proved=True,full_graph_checks=graph_rows,
        exact_full_native_free_private_cofactors=full_cofactors,
        exhaustive_basis_pulse_rows=6*p.Q,periodic_basis_cells=N,
        force_on_cycle_rows=p.Q,force_on_cycle_translation=-3*p.Q,force_off_tail_rows=2*p.Q,
        basis_frame_summaries=rows,all_six_plane_cycle_and_tail_equalities_proved=True,
        native_GF_Flag1_bounds_collapsed_by3Q=True,cycle_WF1_zero_and_Flag2_one_proved=True,
        infinite_line_basis_influence_margin=48*p.Q,
        parametric_all_duration_all_period_native_orbit_proved=True,
        canonical_native_full_period_reference_proved_with_arbitrary_private_fields=True,
        one_dense17Q_GF_Flag1_only_physical_row_at_U_realization_proved=True,
        physical_error_classification=old['physical_error_classification'],
        same_own_programme_for_changed_durations_claimed=False,
        changed_duration_own_programme_or_noiseless_self_simulation_proved=False,
        original_SP28_sources_modified=False,active_G17_modified=False,
        duration_family_is_explicit_rule_revision=True,
        durations_below3Q_or_nonmultiples_decided=False,
        smallest_sufficient_reliability_change_proved=False,iid_failure_proved=False,
        global_reliability_established=False,measured_only=False,
        state_asset_sha256=digest(states),run_log_sha256=digest(log),
        retained_initial_wrapper_failure_sha256=digest(out/'SP28_epoch_duration_initial_wrapper_failure.json'),
        exploratory_receipt_sha256=digest(out/'SP28_epoch_duration_cycle_exploratory.json'),
        seconds=time.monotonic()-started,
        scope='Exact native/interface constant-family obstruction; actual own programmes for m!=4 and iid conclusions unproved')
    receipt=out/'SP28_epoch_duration_obstruction_certificate.json'
    receipt.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('durations_proved','exact_full_native_free_private_cofactors',
        'parametric_all_duration_all_period_native_orbit_proved','global_reliability_established','seconds')}),flush=True)


if __name__=='__main__':main()
