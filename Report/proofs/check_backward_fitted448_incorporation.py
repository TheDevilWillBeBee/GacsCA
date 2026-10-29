#!/usr/bin/env python3
"""J122: SP22 own-rule, native reconstruction and complete E0 encoding.

Full induction is written in ROBUSTNESS. Actual startup/window gates are
rechecked at NPe65/MP75; generic copy/capture/front arguments are pinned.
No damage confinement, mixed-island upper map or iid threshold follows.
"""
from dataclasses import asdict
from pathlib import Path
from types import FunctionType,SimpleNamespace
import hashlib,inspect,json,sys,time
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,Compiled
import proposed_sparse_backward_fitted448 as proposed
import proposed_sparse_epoch448 as previous
import check_right_epoch_starter as epoch
import check_commit_reset448_incorporation as reset


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def controller_cut(p,free_captures=False):
    n=Net()
    def controller(net,*a,**kw):
        return dict(addr=[net.input(('proof_controller','GF',b)) for b in range(p.k)],
            age_now=[net.input(('proof_controller','Age_now',b)) for b in range(p.m)],
            age=[net.input(('proof_controller','Age_next',b)) for b in range(p.m)],
            f1=net.input(('proof_controller','F1')),f2=net.input(('proof_controller','F2')))
    def captures(net,p,age,address,rank,table):
        return [net.input(('proof_capture',tuple(address),rank,g)) for g in range(3)],\
               net.input(('proof_direction',tuple(address),rank))
    def build(module):
        fn=module.full_net
        if free_captures:
            env=dict(fn.__globals__)
            env['transport']=SimpleNamespace(**dict(env['transport'].__dict__,sparse_controls=captures))
            fn=FunctionType(fn.__code__,env,fn.__name__,fn.__defaults__)
        return fn(p,net_class=lambda:n,maintenance=controller)[0]
    old=build(previous)
    before=dict(old.outputs)
    n.outputs={}
    new=build(proposed)
    changed=[key for key in before if before[key]!=new.outputs[key]]
    assert set(new.outputs)-set(before)=={('y','backward_pressure',0)}
    if free_captures:
        assert changed==[('y','info',b) for b in range(5)]
        assert len(before)-len(changed)==331
    else:
        expected=[('y','info',b) for b in range(5)]
        expected += [( 'y',f,b) for f in ('h1','h2') for b in range(60) if b%12<5]
        assert changed==expected
        assert len(before)-len(changed)==281
    return len(before)-len(changed),len(changed)


def observed_net(p,observe=False,**kw):
    n,source=proposed.full_net(p,**kw)
    if observe:
        cells={j:{f:[n.input(('x',j,f,b)) for b in range(w)] for f,w in proposed.schema(p)}
               for j in range(-12,13)}
        mode=epoch.dominant_majority if kw.get('symbolic') else epoch.proposed.majority_word
        e=proposed.base.starter.epoch(n,cells,p,mode)
        n.set_output(('proof','epoch_force'),e['force'])
        n.set_output(('proof','birth'),e['birth'])
    return n,source


def actual_startup_and_clock(p):
    env=dict(epoch.__dict__,proposed=SimpleNamespace(**dict(proposed.__dict__,
        full_net=observed_net,epoch=proposed.base.starter.epoch)))
    functions={name:FunctionType(getattr(epoch,name).__code__,env,name,getattr(epoch,name).__defaults__)
               for name in ('startup_case','birth_geometry','WF1_identities')}
    startup=0
    for reader in range(7):
        for faults in epoch.STARTUP_PAIRS:
            functions['startup_case'](p,reader,faults)
            startup+=1
        print(json.dumps(dict(startup_cofactors=startup)),flush=True)
    birth=functions['birth_geometry'](p)
    wf=functions['WF1_identities'](p)
    # Reuse the exact finite clock proof, replacing only its obsolete numbers.
    source=inspect.getsource(epoch.timing)
    marker='assert (T,increments,excluded) == (38719,38719,37822)'
    assert source.count(marker)==1
    source=source.replace(marker,'assert (T,increments,excluded) == (p.U-p.T_wf,p.U-p.T_wf,p.U-p.T_wf-897)')
    exec(compile(source,'<J122 epoch clock proof with parameterized counts>','exec'),env)
    timing=env['timing'](p)
    assert (startup,birth,wf)==(637,(330,275,49),5)
    return startup,birth,wf,timing


def commit_identities(p):
    source=inspect.getsource(reset.commit_identities)
    marker='assert zeros == 283'
    assert source.count(marker)==1
    env=dict(reset.__dict__,proposed=proposed)
    exec(compile(source.replace(marker,'assert zeros == 284'),'<J122 literal reset/Info checker>','exec'),env)
    return env['commit_identities'](p)


def encoding_arithmetic(p):
    primaries=set(proposed.layout(p).tolist())|{p.lo,p.hi-1}
    assert primaries==set(range(p.lo,p.lo+318))|{p.hi-1}
    allowed=0
    for phase in range(p.Q):
        for slot in range(-2,3):
            if (phase+slot)%p.Q in primaries:
                assert 0<=phase+slot<p.Q
                allowed+=1
    assert (len(primaries),allowed,p.Q*5-allowed)==(319,1595,645)
    assert min(primaries)-2>=0 and max(primaries)+2<p.Q
    assert p.T_wf+1150<p.T_wf+1793<p.T_wf+1794<p.E0+p.NP*p.PL<p.U-1
    return dict(allowed_Info_primaries=319,Info_phase_slot_checks=p.Q*5,
        allowed_Info_copy_slots=1595,unused_Info_copy_slots_zero=645,
        source_birth_clock=p.T_wf+1,all_C_Flag1_quiet_E0_clock=p.T_wf+1150,
        packet_code_empty_clock=p.T_wf+1793,pressure_empty_clock=p.T_wf+1794,
        evaluation_end_input_clock=p.E0+p.NP*p.PL,commit_input_clock=p.U-1)


def main():
    started=time.monotonic()
    out=ROOT/'figs/robustness'
    candidate=proposed.load_artifact()
    p=candidate.p
    assert asdict(p)==dict(asdict(proposed.local.parameters()),NPe=65,MP=75)
    n,source=proposed.actual_net(p)
    assert Compiled(n).digest==candidate.comp.digest==proposed.local.cached(p)[1].digest
    assert source==proposed.local.generated_source(p)
    actual=controller_cut(p)
    symbolic=controller_cut(p,free_captures=True)
    startup,birth,wf,timing=actual_startup_and_clock(p)
    zeros,info=commit_identities(p)
    assert (zeros,info)==(284,5)
    schedule=json.loads((out/'SP22_symbolic_schedule.json').read_text())
    build=json.loads((out/'SP22_program_build.json').read_text())
    native=json.loads((out/'SP22_backward_native_certificate.json').read_text())
    assert schedule['proposed_candidate_sha256']==build['proposed_candidate_sha256']==candidate.digest()
    assert native['module_raw_netlist_sha256']==candidate.comp.digest
    assert (schedule['key_equalities'],schedule['early_flag_equalities'],schedule['final_hold_equalities'],
            schedule['history_ranks_checked'],schedule['counts']['hold_writes'])==(19,2,317,12,319)
    assert max(schedule['early_flag_store_ages'].values())<min(p.courier_ticks()[1:])
    assert build['build_complete'] and build['random_replay_mismatches']==0
    dependencies={key:digest(out/name) for key,name in (
        ('build_receipt_sha256','SP22_program_build.json'),
        ('programme_receipt_sha256','SP22_symbolic_schedule.json'),
        ('front_receipt_sha256','SP22_front_certificate.json'),
        ('native_receipt_sha256','SP22_backward_native_certificate.json'),
        ('epoch_receipt_sha256','right_epoch_starter_certificate.json'),
        ('SP18_incorporation_receipt_sha256','SP18_incorporation_encoded_certificate.json'),
        ('quiet_native_receipt_sha256','SP16_quiet_region_certificate.json'),
        ('period_native_receipt_sha256','SP16_period_barrier_certificate.json'),
        ('encoded_receipt_sha256','SP16_encoded_certificate.json'))}
    result=dict(proposal='SP22',proposed_rule_change=True,active_G17_modified=False,SP18_modified=False,
        J121_local_module_modified=False,primitive_parameter_changes={'NPe':[50,65],'MP':[73,75]},
        Q=p.Q,U=p.U,width=candidate.W,radius=12,initial_epoch_clock=p.T_wf,
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        checker_sha256=digest(Path(__file__)),proposal_source_sha256=digest(Path(proposed.__file__)),
        local_module_source_sha256=digest(Path(proposed.local.__file__)),
        epoch_checker_source_sha256=digest(Path(epoch.__file__)),
        commit_checker_source_sha256=digest(Path(reset.__file__)),
        helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
        full_generated_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        actual_maintenance_source_sha256=hashlib.sha256(proposed.proposed_build()[1].encode()).hexdigest(),
        **dependencies,**encoding_arithmetic(p),timing=timing,
        actual_native_controller_cut_shared_outputs=actual[0],actual_controller_cut_changed_outputs=actual[1],
        common_native_and_capture_control_cut_shared_outputs=symbolic[0],common_cut_changed_Info_outputs=symbolic[1],
        new_history_capture_controls_rechecked_by_own_all_twelve_rank_certificate=True,
        actual_full_changed_pressure_startup_cofactors=startup,
        RF_birth_geometry_cofactors=list(birth),WF1_full_output_identities=wf,
        literal_commit_native_Flag2_component_and_workspace_zero_bits=zeros,
        literal_commit_forwarded_Hold_Info_mask_identities=info,
        full_raw_transition_identical_to_J121_local_equations_at_revised_parameters=True,
        initial_positive_epoch_GF_Age_required_for_native_reconstruction=True,
        native_reconstruction_state=449,native_quiet_state=1150,
        arbitrary_I_native_proof_applies_to_actual_own_ROM=True,
        complete_encoded_noiseless_and_all_period_E0_simulation_proved=True,
        full_boundary_encoding_identity_before_current_overwrites=True,
        raw_boundary_five_copy_decoder_exact_under_current_E0=True,
        intact_noiseless_infinite_hierarchy_exists=True,
        left_damage_confinement_or_finite_island_erosion_established=False,
        general_mixed_island_full_upper_error_map_established=False,
        iid_threshold_established=False,minimal_sufficient_global_reliability_change_established=False,
        global_reliability_established=False,seconds=time.monotonic()-started,
        scope='ROBUSTNESS J122: own SP22 at Q448/U67584/NPe65/MP75; actual native reconstruction and complete-encoding E0 closure; no left confinement, general upper island map or iid threshold')
    (out/'SP22_incorporation_encoded_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(candidate=candidate.digest(),non_Info_common_cut=symbolic[0],
        commit_zeros=zeros,complete_E0_encoding=True,iid=False)),flush=True)


if __name__=='__main__':
    main()
