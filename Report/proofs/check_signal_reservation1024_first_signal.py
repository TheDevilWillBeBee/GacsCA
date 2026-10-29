#!/usr/bin/env python3
"""Exact SP30 first-signal interfaces; physical proof in SP30_FIRST_SIGNAL.md.

The full-circuit cofactors leave unmentioned inputs free. This checks
source geometry and identities, not sampled whole-period trajectories.
"""
from pathlib import Path
import hashlib,json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,Compiled,w_eq_const,w_in_range
import proposed_sparse_signal_reservation1024 as proposed
import check_distant_epoch1024_full_address_island as quiet


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    started=time.monotonic();p=proposed.parameters();out=ROOT/'figs/robustness'
    encoded=json.loads((out/'SP30_encoded_certificate.json').read_text())
    assert encoded['non_Info_output_function_equalities']==757
    assert encoded['non_Info_changed_history_outputs']==80
    assert encoded['complete_encoded_noiseless_and_all_period_E0_simulation_proved']
    a=128*p.Q-512;b=144*p.Q;strips=((127*p.Q,a),(b-512,b))
    source=proposed.generated_source(p)
    for line in (
        "        mr = n.AND(mr, n.NOT(f1_new))           # Gray: Mailbox cleared where Flag1\n",
        "        ml = n.AND(ml, n.OR(n.NOT(f1_new), protected_flag2_courier))\n",
        "    keep = n.NOT(wipe)\n",
        "    sig = age_is(p.T_sig)\n",
        "            h1n = n.MUX(caps[0], passing, h1)\n",
        "            h1n = n.MUX(caps[2], maj3(n, h1, h2, passing), h1n)\n",
        "            h2n = n.MUX(caps[1], passing, h2)\n",
    ):assert source.count(line)==1,line
    candidate=proposed.load_artifact()
    programme=json.loads((out/'SP30_symbolic_schedule.json').read_text())
    assert programme['proposed_candidate_sha256']==candidate.digest()
    assert programme['early_flag_equalities']==2 and programme['final_hold_equalities']==842
    assert max(programme['early_flag_store_ages'].values())<min(p.courier_ticks()[1:])
    assert p.courier_ticks()[2]+1+p.Q-3-(p.hi-1)==p.T_sig==p.T_wf-1
    assert proposed.proposed_build()[1]==quiet.proposed.proposed_build()[1]
    refine_cases,native_cases,native_sha=quiet.quiet_cofactors(p)

    # Legal quiet-clock guard: all service births/epoch forces and WF1
    # sources are closed before TF, independently of their spatial votes.
    n=Net();age=[n.input(('age',bit)) for bit in range(p.m)]
    n.set_output(('birth_clock',),w_eq_const(n,age,p.age_code(p.T_wf)))
    n.set_output(('force_clock',),w_in_range(n,age,p.age_code(p.T_wf),p.age_code(p.T_wf+2048)))
    n.set_output(('WF1_clock',),w_in_range(n,age,p.age_code(p.T_wf),p.age_code(p.T_wf+2*p.Q-1)+1))
    codes=np.array([p.age_code(t) for t in range(p.T_wf)],dtype=np.uint32)
    got=Compiled(n).evaluate({('age',bit):((codes>>bit)&1).astype(bool) for bit in range(p.m)},bool)
    assert all(not value.any() for value in got.values())

    # Literal majority fold after a per-holder gate, allowing incoherent
    # old mail copies as well as all holder gate masks.
    fold_cases=0
    for old in range(32):
        common=int(old.bit_count()>=3)
        for gates in range(32):
            new=[common*((gates>>i)&1) for i in range(5)]
            assert int(sum(new)>=3)==common*int(gates.bit_count()>=3)
            fold_cases+=1
    def f1(x):return int(any(lo<=x<hi for lo,hi in strips))
    gate_cases=0
    for edge in [v for pair in strips for v in pair]:
        for x in range(edge-3,edge+4):
            assert int(sum(not f1(x+s) for s in range(-2,3))>=3)==1-f1(x)
            gate_cases+=1

    table=proposed.dependency_table(p);byphase={r['address']:r for r in table}
    gf_rows=[r for r in table if r['field']=='addr'];routes=[]
    assert len(gf_rows)==10
    for r in gf_rows:
        phase=(r['address']-512)%p.Q;real=byphase[phase]
        assert r['address']==59+r['bit'] and phase==571+r['bit']
        assert (real['field'],real['bit'])==('h2',139+r['bit'])
        routes.append(dict(bit=r['bit'],virtual_phase=r['address'],physical_phase=phase,
                           true_field='h2',true_bit=real['bit']))
    class ZeroGF(Net):
        def input(self,key):
            if isinstance(key,tuple) and len(key)==4 and key[0]=='x' and key[2]=='addr':return 0
            return super().input(key)
    zero,_=proposed.full_net(p,ZeroGF)
    assert zero.outputs['y','f1',0]==1
    assert all(zero.outputs['y','addr',bit]==0 for bit in range(p.k))

    geometry_cases=0;true_cases=[];true_ones=[]
    def blocked(j,d,phase):
        lo,hi=sorted((j*p.Q+phase,(j+d)*p.Q+phase))
        interval=any(max(lo,l)<=min(hi,r-1) for l,r in strips)
        progression=any(lo+8*max(0,(l-lo+7)//8)<=min(hi,r-1) for l,r in strips)
        assert interval==progression
        return progression
    for j in range(90,182):
        if 127<=j<144:continue # These true frames straddle/use wrong phase.
        raw_words={}
        for row in gf_rows:
            for d in (0,*row['offsets']):
                value=blocked(j,d,row['address'])
                assert value==blocked(j,d,59)
                geometry_cases+=1
                word=0 if value else (j+d)%p.Q
                raw_words.setdefault(d,0)
                raw_words[d]|=((word>>row['bit'])&1)<<row['bit']
        class Captured(Net):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,f,bit=key
                    if f=='addr' and d in raw_words:return (raw_words[d]>>bit)&1
                    if f in ('age','f1','f2','wf1','wf2','packet_valid','service_valid','backward_pressure'):return 0
                return super().input(key)
        net,_=proposed.full_net(p,Captured);flag=net.outputs['y','f1',0]
        assert flag in (0,1),(j,flag)
        assert flag==int(j in (124,125,126,144,145,146))
        true_cases.append(dict(colony=j,Flag1=flag))
        if flag:true_ones.append(j)
    # Outside this finite range no requested path meets either strip.
    assert (89+37)*p.Q+68<strips[0][0]
    assert (182-37)*p.Q+59>=strips[-1][1]
    # The only complete foreign frames are origins jQ-512, j128..143.
    assert a==(128*p.Q-512) and (144*p.Q-512)<b<145*p.Q-512
    dependencies=('SP30_program_build.json','SP30_symbolic_schedule.json','SP30_native_certificate.json',
        'SP30_front_certificate.json','SP30_encoded_certificate.json',
        'SP28_full_Address_island_certificate.json')
    receipt=dict(proposal='SP30',scope='J191 first signal from a stationary prepared native template and complete underlying encoding; no later-period replenishment/eroder/iid theorem',
        proposed_rule_change=False,additional_rule_change=False,active_G17_modified=False,
        checker_sha256=digest(__file__),proposal_source_sha256=digest(proposed.__file__),
        written_proof_sha256=digest(ROOT/'Report/proofs/SP30_FIRST_SIGNAL.md'),
        inherited_first_signal_checker_sha256=digest(ROOT/'Report/proofs/check_short_force1024_first_signal.py'),
        new_layout_and_own_programme_rechecked_not_old_damaged_history_transferred=True,
        quiet_checker_sha256=digest(quiet.__file__),quiet_written_proof_sha256=digest(ROOT/'Report/proofs/SP28_FULL_ADDRESS_ISLAND.md'),
        native_maintenance_source_sha256=native_sha,
        full_generated_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        Q=p.Q,U=p.U,T_wf=p.T_wf,initial_native_GF_interval=[a,b],initial_Flag1_intervals=[list(v) for v in strips],
        quiet_refinement_cofactors=refine_cases,quiet_native_cofactors=native_cases,
        legal_pre_TF_clock_guard_cases=len(codes),mail_copy_gate_fold_cases=fold_cases,
        fixed_Flag1_gate_boundary_cases=gate_cases,virtual_GF_zero_full_circuit_Flag1_constant=1,
        zero_virtual_GF_gives_all_zero_computed_GF=True,
        zero_virtual_GF_all_other_inputs_symbolically_free=True,foreign_GF_source_routes=routes,
        true_capture_bit_route_geometry_cases=geometry_cases,
        true_frame_full_circuit_cofactor_cases=len(true_cases),true_frame_cofactor_results=true_cases,
        first_ghost_MF509_one_colonies=list(range(128,144)),first_true_MF1021_one_colonies=true_ones,
        exact_first_signal_physical_history_proved=True,
        initial_underlying_upper_GF_canonical_Age_zero_private_zero_required=True,
        lower_native_template_prepared_by_one_17Q_error_row=True,no_subsequent_errors_required=True,
        all_initial_upper_Info_payloads_allowed=True,
        later_period_signal_replenishment_proved=False,general_width_or_phase_eroder_proved=False,
        higher_error_map_or_iid_rate_established=False,global_reliability_established=False,
        numerical_CA_trajectories_used=False,seconds=time.monotonic()-started,
        receipt_dependencies_sha256={name:digest(out/name) for name in dependencies})
    (out/'SP30_first_signal_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ('quiet_native_cofactors','true_frame_full_circuit_cofactor_cases',
        'first_ghost_MF509_one_colonies','first_true_MF1021_one_colonies','seconds','global_reliability_established')}),flush=True)


if __name__=='__main__':main()
