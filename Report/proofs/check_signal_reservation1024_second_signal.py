#!/usr/bin/env python3
"""Actual SP30 second signal, two restricted pulses and next zero-GF bank.

Finite contracts supplement the source/physical inductions in the proof.
This is not an arbitrary-error eroder or a numerical whole-CA trajectory.
"""
from itertools import product
from pathlib import Path
from types import FunctionType
import hashlib,json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,Compiled,const_word,w_eq_const
from gacsca import rule_g
import proposed_sparse_signal_reservation1024 as proposed
import check_commit_reset448_incorporation as reset
import check_short_force1024_GF_bank_closure as inherited_bank


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def blocked(strips,j,d,phase,Q):
    lo,hi=sorted((j*Q+phase,(j+d)*Q+phase))
    return any(lo+8*max(0,(left-lo+7)//8)<=min(hi,right-1) for left,right in strips)


def alias_carry_identity(p,slot):
    # Both actual partial primaries have virtual phase509. Pin only the
    # correct native GF interface; clock/Info/private/flags/I stay free.
    gf=(509-slot)%p.Q
    class CanonicalGF(Net):
        def input(self,key):
            if isinstance(key,tuple) and len(key)==4 and key[0]=='x' and key[2]=='addr':
                return (((gf+key[1])%p.Q)>>key[3])&1
            return super().input(key)
    def controller(n,cells,*args,**kwargs):
        assert cells[0]['addr']==const_word(gf,p.k)
        return dict(addr=cells[0]['addr'],
            age_now=[n.input(('proof','clock',i)) for i in range(p.m)],
            age=[n.input(('proof','next_clock',i)) for i in range(p.m)],
            f1=n.input(('proof','F1')),f2=n.input(('proof','F2')))
    namespace=dict(proposed.legacy.__dict__,schema=proposed.schema,width=proposed.width,
        previous=proposed.previous,dependency_table=proposed.dependency_table,
        service_build=proposed.service_build,generated_source=proposed.generated_source,
        proposed_build=lambda:(controller,'conditional correct native GF interface'))
    fn=proposed.legacy.full_net
    n,_=FunctionType(fn.__code__,namespace,fn.__name__,fn.__defaults__)(p,CanonicalGF)
    clock=[n.input(('proof','clock',i)) for i in range(p.m)]
    old=rule_g.maj5(n,[n.input(('x',slot-s,'info',s+2)) for s in proposed.SLOTS])
    commit=w_eq_const(n,clock,p.age_code(p.U-1))
    expected=n.AND(n.NOT(commit),n.MUX(commit,reset.forwarded_hold(n,p,0,slot),old))
    normal=reset.normalized(n)
    assert normal[n.outputs['y','info',slot+2]]==normal[expected],slot
    for committing,hold,value in product((0,1),repeat=3):
        assert (1-committing)*(hold if committing else value)==(1-committing)*value
    return dict(Info_slot=slot,holder_virtual_GF=gf,virtual_primary=509,
        every_raw_clock_and_other_private_Info_flag_instruction_input_free=True,
        carry_old_majority_except_zero_at_commit=True)


def first_boundary_words(p,c,out):
    table=proposed.dependency_table(p);phase_at={(r['field'],r['bit']):r['address'] for r in table}
    old_strips=((127*p.Q,128*p.Q-512),(144*p.Q-512,144*p.Q))
    records=[]
    for j in range(90,182):
        if 127<=j<=143:continue
        class FirstCaptured(Net):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,field,bit=key
                    if field=='addr':
                        word=0 if blocked(old_strips,j,d,phase_at[field,bit],p.Q) else (j+d)%p.Q
                        return (word>>bit)&1
                    if field in ('age','f1','f2','wf1','wf2','packet_valid','service_valid','backward_pressure'):
                        return 0
                return super().input(key)
        n,_=proposed.full_net(p,FirstCaptured)
        expected=dict(addr=j%p.Q,age=p.age_code(1),f1=int(j in (124,125,126,144,145,146)),wf1=0)
        equalities=0
        for field,value in expected.items():
            for bit in range(dict(c.schema)[field]):
                assert n.outputs['y',field,bit]==(value>>bit)&1,(j,field,bit)
                equalities+=1
        records.append(dict(colony=j,GF=expected['addr'],Age=expected['age'],
            Flag1=expected['f1'],WF1=0,constant_output_bit_equalities=equalities,
            netlist_sha256=Compiled(n).digest))
    assert len(records)==75
    rows=[json.loads(line) for line in (out/'SP29_refined_wipe_2048_mode1.jsonl').read_text().splitlines() if '"row"' in line]
    assert len(rows)==6145
    hull=(min(r['left'] for r in rows),max(r['right_exclusive'] for r in rows))
    assert hull==(123456,147456)
    protected=[120*p.Q+phase+holder for phase in (*range(59,69),88) for holder in range(-2,3)]
    assert max(protected)+32<hull[0]
    assert 119*p.Q+1022<hull[0] and 144*p.Q+1>=hull[1]
    listing=json.loads((out/'SP30_program_listing.json').read_text());issues=[]
    for phase,shift in product((*range(59,69),88),(0,512)):
        actual=phase+shift
        selected=[r for r in listing if r[4]==actual and r[6]==rule_g.K_HOLD]
        assert len(selected)==1
        row=selected[0];column=row[1]+(row[3]<<p.logNP);age=p.E0+row[1]*p.PL+row[2]
        assert np.flatnonzero(((c.rom[actual]>>2)&3)==rule_g.K_HOLD).tolist()==[column]
        assert age+2<p.T_wf if shift==0 else age>p.T_wf+6144
        issues.append(dict(normal_phase=phase,phase_shift=shift,actual_phase=actual,
            input_issue_age=age,materialized_age=age+2,ROM_column=column))
    assert next(r['input_issue_age'] for r in issues if r['actual_phase']==88)==259870
    assert next(r['input_issue_age'] for r in issues if r['actual_phase']==600)==357660
    recovered=[]
    for j,phase in product(range(136,144),(*range(59,69),88)):
        y=j*p.Q+phase
        assert 130560<=y-2 and y+2<147456 and y-2>=139264
        recovered.append(dict(colony=j,normal_phase=phase,primary=y,initial_final_phases=[phase+512,phase]))
    return records,protected,issues,recovered,hull


def second_cofactors(p):
    table=proposed.dependency_table(p);phase_at={(r['field'],r['bit']):r['address'] for r in table}
    strips=((121*p.Q,122*p.Q-512),(136*p.Q-512,136*p.Q));records=[];route_checks=0
    for j in (*range(83,121),*range(136,184)):
        left=j<=120
        for row in table:
            if row['field'] not in ('addr','age','f1','wf1'):continue
            for d in (0,*row['offsets']):
                erased=blocked(strips,j,d,row['address'],p.Q)
                assert erased==blocked(strips,j,d,59,p.Q)
                assert erased or (j+d<=120 if left else j+d>=136)
                route_checks+=1
        class Captured(Net):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,field,bit=key;col=j+d
                    if field in ('addr','age','f1','wf1'):
                        if blocked(strips,j,d,phase_at[field,bit],p.Q):return 0
                        if field=='addr':return (((col%p.Q) if left or col>=144 else 0)>>bit)&1
                        if field=='f1':return 0 if left else int(col in (144,145,146))
                        free=(col==120 if left else col<=143)
                        if field=='age':return super().input(('upper_Age',col,bit)) if free else ((p.age_code(1)>>bit)&1)
                        if field=='wf1':return super().input(('upper_WF1',col,bit)) if free else 0
                return super().input(key)
        n,_=proposed.full_net(p,Captured);node=n.outputs['y','f1',0]
        value=node if node in (0,1) else None
        expected=None if j==117 else int(j in (118,119,120) or 136<=j<=146)
        assert value==expected,(j,value,expected)
        records.append(dict(colony=j,side='left' if left else 'right',Flag1_constant=value,
            all_unmentioned_fields_and_I_free=True,netlist_sha256=Compiled(n).digest))
    assert 82+37<120 and 184-37>146
    return records,route_checks


def main():
    started=time.monotonic();p=proposed.parameters();c=proposed.load_artifact();out=ROOT/'figs/robustness'
    first=json.loads((out/'SP30_first_signal_certificate.json').read_text())
    pulse=json.loads((out/'SP30_native_pulse_certificate.json').read_text())
    bank=json.loads((out/'SP30_GF_bank_closure_certificate.json').read_text())
    assert first['exact_first_signal_physical_history_proved'] and pulse['new_actual_first_pulse_on_Z_proved']
    assert bank['actual_first_boundary_zero_bank_and_next_complete_foreign_sources_proved']
    assert c.digest()==first['proposed_candidate_sha256']==pulse['proposed_candidate_sha256']==bank['proposed_candidate_sha256']
    mask=(set(range(58,901))-{509,515})|{901,902,965};aliases=(3,509,515,1021);alias_checks=0
    for phase,shift,slot in product(aliases,(0,512),proposed.SLOTS):
        assert ((phase-slot+shift)%p.Q+slot)%p.Q not in mask;alias_checks+=1
    carry=[alias_carry_identity(p,s) for s in proposed.SLOTS]
    support=[]
    for j,phase in product(range(110,154),(509,1021)):
        y=j*p.Q+phase;labels=[int(124416<=y-s<139264) for s in proposed.SLOTS]
        assert len(set(labels))==1
        virtual=(phase+512*labels[0])%p.Q
        assert virtual in (509,1021)
        active=virtual==1021
        assert active==((122<=j<=135) if phase==509 else (j<=120 or j>=136))
        support.append(dict(colony=j,physical_phase=phase,virtual_primary=virtual,special_write=active))
    assert [r['virtual_primary'] for r in support if (r['colony'],r['physical_phase']) in ((121,509),(135,1021))]==[509,509]
    words,protected,issues,recovered,hull=first_boundary_words(p,c,out)
    cofactors,gate_routes=second_cofactors(p)
    probes=json.loads((out/'SP29_second_pulse_case_probe.json').read_text())
    assert probes['unknown_bits']==['MF509(121)','MF1021(117)','MF1021(135)']
    selected=[case for case in probes['cases'] if case['mask'] in (0,2)]
    assert [r['mask'] for r in selected]==[0,2]
    GF_sites=background_sites=0;logs={}
    with np.load(out/'SP29_second_pulse_case_final_states.npz',allow_pickle=False) as states:
        for case in selected:
            m=case['mask'];path=out/case['log_name'];assert digest(path)==case['log_sha256']
            rows=[json.loads(line) for line in path.read_text().splitlines()];summary=rows.pop()
            assert summary==case['exhaustive_checks'] and summary['certificate_complete']
            assert summary['GF_support_sites_checked']==1610874880 and summary['background_site_equalities']==1113215910
            assert [r['row'] for r in rows]==list(range(6145))
            for row in rows:
                assert row['background_lo']==117*p.Q-8*(row['row']+1)-37
                assert row['background_hi']==148*p.Q+8*(row['row']+1)+37
            assert (rows[-1]['background_lo'],rows[-1]['background_hi'])==(70611,200749)
            assert (case['final']['left'],case['final']['right_exclusive'],case['final_width'])==(118272,131072,12800)
            assert case['native_quiet_template_final'] and case['width_decrease']==2048
            assert (case['noninterval_rows'],case['maximum_holes'])==(2,2)
            native=states[f'case{m}_native'];code=states[f'case{m}_code'];info=states[f'case{m}_Info']
            assert np.flatnonzero(native[0]).tolist()==list(range(118272,131072))
            flag=np.zeros(262144,dtype=np.uint8);flag[117760:118272]=1;flag[130560:131072]=1
            assert np.array_equal(native[1],flag) and not native[2:].any() and not code.any()
            for suffix in ('native','code','Info'):assert np.array_equal(states['case0_'+suffix],states[f'case{m}_'+suffix])
            GF_sites+=summary['GF_support_sites_checked'];background_sites+=summary['background_site_equalities'];logs[path.name]=digest(path)
        info509=np.flatnonzero(states['case0_Info'][np.arange(509,262144,1024)]).tolist()
        info1021=np.flatnonzero(states['case0_Info'][np.arange(1021,262144,1024)]).tolist()
    assert GF_sites==3221749760 and background_sites==2226431820
    assert (116<=122,128<=136-1)==(True,True)
    targets=[];true=foreign=0
    for j,bit in product(range(115,128),range(10)):
        y=j*p.Q+571+bit
        assert 118272<=y-2-37 and y+2+37<131072
        if j<121:origin=None;true+=1
        else:
            origin=(j+1)*p.Q-512
            assert 124416<=origin and origin+p.Q<=139264 and y-origin==59+bit;foreign+=1
        targets.append(dict(primary=y,bit=bit,previous_complete_foreign_origin=origin))
    assert (len(targets),true,foreign)==(130,60,70)
    namespace=dict(inherited_bank.__dict__,proposed=proposed)
    route=FunctionType(inherited_bank.routes.__code__,namespace,'routes')(p,116,128)
    assert (route['routes'],route['direct_checks'])==(23400,360)
    dependencies=('SP30_first_signal_certificate.json','SP30_native_pulse_certificate.json',
        'SP30_GF_bank_closure_certificate.json','SP30_encoded_certificate.json','SP30_front_certificate.json',
        'SP30_symbolic_schedule.json','SP30_program_build.json','SP29_second_pulse_case_probe.json',
        'SP29_refined_wipe_certificate.json','SP28_short_epoch_enclosure_gap_certificate.json')
    result=dict(proposal='SP30',scope='J197 actual one-bit second-signal enclosure, second shrinking native/Info pulse on Z, next zero-GF bank and twelve third complete foreign sources; no general eroder/iid',
        proposed_rule_change=False,additional_rule_change=False,active_G17_modified=False,
        Q=p.Q,U=p.U,T_wf=p.T_wf,force_duration=2048,
        checker_sha256=digest(__file__),written_proof_sha256=digest(ROOT/'Report/proofs/SP30_SECOND_SIGNAL.md'),
        proposal_source_sha256=digest(proposed.__file__),proposed_candidate_sha256=c.digest(),proposed_netlist_sha256=c.comp.digest,
        full_generated_source_sha256=hashlib.sha256(proposed.generated_source(p).encode()).hexdigest(),
        listing_sha256=digest(out/'SP30_program_listing.json'),
        source_dependencies_sha256={name:digest(ROOT/name) for name in ('gacsca/rule_g.py','gacsca/netlist.py',
            'Report/proofs/check_commit_reset448_incorporation.py','Report/proofs/check_short_force1024_GF_bank_closure.py',
            'Report/proofs/check_signal_reservation1024_native_pulse.py','Report/proofs/check_signal_reservation1024_encoded.py')},
        receipt_dependencies_sha256={name:digest(out/name) for name in dependencies},
        retained_initial_checker_failure_assets_sha256={name:digest(out/name) for name in
            ('SP30_second_signal_initial_checker.py.txt','SP30_second_signal_initial_checker_failure.log')},
        reused_finite_log_hashes=logs,reused_first_pulse_log_sha256=digest(out/'SP29_refined_wipe_2048_mode1.jsonl'),
        reused_final_state_asset_sha256=digest(out/'SP29_second_pulse_case_final_states.npz'),
        reused_factor_source_sha256=digest(out/'SP29_refined_wipe_factor_generated.c'),
        reused_wrapper_source_sha256=digest(out/'SP29_second_pulse_cases_generated.c'),
        universal_two_phase_commit_alias_zero_cases=alias_checks,actual_partial_alias_carry_identities=carry,
        physical_alias_special_write_classes=support,
        actual_first_boundary_all_alias_Info_copies_zero_proved=True,
        first_boundary_true_word_cofactors=words,first_boundary_true_word_constant_equalities=sum(r['constant_output_bit_equalities'] for r in words),
        first_pulse_all_row_GF_support_hull=list(hull),protected_upper120_GF_Flag1_holders=protected,
        new_actual_twenty_two_phase_Hold_ROM_key_checks=22*c.rom.shape[1],new_actual_Hold_issue_records=issues,
        recovered_GF_Flag1_zero_primary_records=recovered,
        full_new_second_Flag1_cofactors=cofactors,new_second_native_capture_gate_routes=gate_routes,
        second_MF509_one_colonies=list(range(122,136)),second_MF509_unspecified_colonies=[],
        second_MF1021_fixed_one_colonies=[118,119,120,*range(136,147)],second_MF1021_unspecified_colonies=[117],
        partial_MF509_121_and_MF1021_135_exact_zero_proved=True,
        complete_actual_second_signal_one_bit_enclosure_proved=True,one_free_bit='MF1021(117)',
        actual_free_bit_value_or_independence_proved=False,
        actual_source_words_and_new_own_programme_physical_bridge_rechecked=True,
        old_full_private_history_or_late_suffix_transfer_used=False,
        restricted_projection_identity_and_conditional_finite_cases_reused=True,reused_case_masks=[0,2],
        all6145_reused_rows_equal_new_actual_projected_history_by_induction=True,
        second_exact_GF_support_site_checks=GF_sites,second_exact_background_equalities=background_sites,
        second_final_protected_infinite_line_interval=[70611,200749],
        second_pulse_computed_start_time=p.U+p.T_wf,second_pulse_computed_endpoint_time=p.U+p.T_wf+6144,
        second_pulse_final_native_GF_interval=[118272,131072],second_pulse_width_decrease=2048,
        second_pulse_endpoint_template_L_R=[116,128],second_pulse_all_other_native_auxiliaries_and_codes_zero=True,
        second_final_MF509_one_colonies=info509,second_final_MF1021_one_colonies=info1021,
        actual_second_shrinking_native_Info_pulse_on_Z_proved=True,
        second_boundary_computed_time=2*p.U,second_boundary_zero_primary_records=targets,
        second_boundary_zero_GF_Info_copies=650,second_boundary_initially_true_primaries=true,second_boundary_old_foreign_primaries=foreign,
        third_complete_foreign_source_routes=route,third_source_computed_time=2*p.U+p.T_wf,
        third_complete_foreign_MF509_one_colonies=list(range(116,128)),
        actual_second_boundary_and_third_complete_foreign_sources_proved=True,
        third_full_signal_or_pulse_or_full_upper_data_proved=False,
        general_phase_width_clock_faults_or_continuing_E0_eroder_proved=False,
        higher_error_map_or_positive_iid_threshold_or_globally_minimal_fix_proved=False,
        numerical_whole_CA_trajectory_used=False,global_reliability_established=False,
        seconds=time.monotonic()-started)
    path=out/'SP30_second_signal_certificate.json';path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ('complete_actual_second_signal_one_bit_enclosure_proved',
        'actual_second_shrinking_native_Info_pulse_on_Z_proved','second_pulse_computed_endpoint_time',
        'second_boundary_zero_GF_Info_copies','third_complete_foreign_MF509_one_colonies','seconds',
        'global_reliability_established')}),flush=True)


if __name__=='__main__':main()
