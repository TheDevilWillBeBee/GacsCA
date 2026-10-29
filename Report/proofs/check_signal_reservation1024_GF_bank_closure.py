#!/usr/bin/env python3
"""SP30 rechecked conditional GF-bank closure and actual first instantiation."""
from itertools import product
from pathlib import Path
from types import FunctionType
import hashlib,json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net
from gacsca import rule_g
import proposed_sparse_signal_reservation1024 as proposed
import check_signal_reservation1024_encoded as encoded
import check_short_force1024_GF_bank_closure as inherited


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    started=time.monotonic();p=proposed.parameters();c=proposed.load_artifact();out=ROOT/'figs/robustness'
    pulse=json.loads((out/'SP30_native_pulse_certificate.json').read_text())
    first=json.loads((out/'SP30_first_signal_certificate.json').read_text())
    assert pulse['new_actual_first_pulse_on_Z_proved'] and pulse['all6145_reused_rows_equal_new_projected_history_by_induction']
    assert pulse['proposed_candidate_sha256']==first['proposed_candidate_sha256']==c.digest()
    assert pulse['initial_wrong_GF_interval']==[128*p.Q-512,144*p.Q]
    assert pulse['final_wrong_GF_interval']==[122*p.Q-512,136*p.Q]
    listing_path=out/'SP30_program_listing.json';listing=json.loads(listing_path.read_text());issues=[];keys=0
    for phase in (*range(59,69),*range(571,581)):
        rows=[r for r in listing if r[4]==phase and r[6]==rule_g.K_HOLD];assert len(rows)==1
        row=rows[0];column=row[1]+(row[3]<<p.logNP)
        assert np.flatnonzero(((c.rom[phase]>>2)&3)==rule_g.K_HOLD).tolist()==[column]
        issue=p.E0+row[1]*p.PL+row[2]
        issues.append(dict(phase=phase,ROM_column=column,input_issue_age=issue,materialized_age=issue+2));keys+=c.rom.shape[1]
    assert keys==81920
    gf,h2=issues[:10],issues[10:];S=p.T_wf+6144
    assert (min(r['input_issue_age'] for r in gf),max(r['input_issue_age'] for r in gf))==(276520,278398)
    assert (min(r['input_issue_age'] for r in h2),max(r['input_issue_age'] for r in h2))==(345734,358739)
    assert max(r['materialized_age'] for r in gf)<p.T_wf and min(r['materialized_age'] for r in h2)>S
    differences=sorted({(i-j)*p.delta%p.Q for i,j in product(range(p.fronts),repeat=2)})
    assert 512 not in differences and (p.fronts,p.delta,p.mux_front,p.sel_front)==(5,5,True,0)
    pending=0
    for kind,mask in product(range(5),range(32)):
        present=[(mask>>j)&1 for j in range(5)];words=[kind if v else 0 for v in present]
        vote=sum(int(sum((w>>b)&1 for w in words)>=3)<<b for b in range(p.PK))
        assert sum(present)<3 or vote==kind;pending+=1
    zeros,forward=encoded.commit(p);assert (zeros,forward)==(807,5)
    namespace=dict(inherited.__dict__,proposed=proposed)
    quiet=FunctionType(inherited.quiet.__code__,namespace,'quiet')
    routes=FunctionType(inherited.routes.__code__,namespace,'routes')
    geometry=[quiet(p,0,1),quiet(p,122,136)]
    route_checks=[routes(p,0,1),routes(p,0,2),routes(p,122,136)]
    assert route_checks[-1]['routes']==27300 and route_checks[-1]['direct_checks']==420
    class ZeroGF(Net):
        def input(self,key):
            if isinstance(key,tuple) and len(key)==4 and key[0]=='x' and key[2]=='addr':return 0
            return super().input(key)
    zero,_=proposed.full_net(p,ZeroGF)
    assert zero.outputs['y','f1',0]==1 and all(zero.outputs['y','addr',bit]==0 for bit in range(p.k))
    byphase={r['address']:r for r in proposed.dependency_table(p)}
    assert [(byphase[571+bit]['field'],byphase[571+bit]['bit']) for bit in range(10)]==[('h2',139+bit) for bit in range(10)]
    initial_bank=[j*p.Q+phase for j in range(127,144) for phase in range(571,581)]
    targets=[];true=foreign=0
    for j,bit in product(range(121,136),range(10)):
        y=j*p.Q+571+bit;a,b=pulse['final_wrong_GF_interval']
        assert a<=y-2-37 and y+2+37<b and 59+bit in c.layout
        if j<127:origin=None;true+=1
        else:
            origin=(j+1)*p.Q-512
            assert 128*p.Q-512<=origin and origin+p.Q<=144*p.Q
            assert y-origin==59+bit;foreign+=1
        targets.append(dict(primary=y,bit=bit,initial_complete_old_foreign_origin=origin))
    assert (len(initial_bank),true,foreign,len(targets))==(170,60,90,150)
    dependencies=('SP30_first_signal_certificate.json','SP30_native_pulse_certificate.json',
        'SP30_encoded_certificate.json','SP30_front_certificate.json','SP30_native_certificate.json',
        'SP30_program_build.json','SP30_symbolic_schedule.json','SP29_next_ghost_signal_certificate.json')
    result=dict(proposal='SP30',scope='J195 new-ROM conditional zero-GF bank closure, actual first boundary and fourteen next complete foreign signals; no full next mask/pulse/general eroder/iid',
        proposed_rule_change=False,additional_rule_change=False,active_G17_modified=False,
        Q=p.Q,U=p.U,T_wf=p.T_wf,settled_local_age=S,
        checker_sha256=digest(__file__),written_proof_sha256=digest(ROOT/'Report/proofs/SP30_GF_BANK_CLOSURE.md'),
        proposal_source_sha256=digest(proposed.__file__),proposed_candidate_sha256=c.digest(),proposed_netlist_sha256=c.comp.digest,
        full_generated_source_sha256=hashlib.sha256(proposed.generated_source(p).encode()).hexdigest(),listing_sha256=digest(listing_path),
        inherited_checker_sha256=digest(inherited.__file__),inherited_proof_sha256=digest(ROOT/'Report/proofs/SP29_GF_BANK_CLOSURE.md'),
        source_dependencies_sha256={name:digest(ROOT/name) for name in ('gacsca/rule_g.py','gacsca/netlist.py',
            'Report/proofs/check_signal_reservation1024_encoded.py','Report/proofs/check_short_force1024_protected_scratch.py')},
        receipt_dependencies_sha256={name:digest(out/name) for name in dependencies},
        new_twenty_phase_ROM_keys_checked=keys,Hold_issue_records=issues,new_true_H2_issue_range=[345734,358739],
        old_damaged_private_trajectory_transferred=False,new_own_programme_and_physical_interfaces_rechecked=True,
        quiet_geometry_cofactors=geometry,route_classes=route_checks,one_kind_pending_presence_cases=pending,
        comb_tooth_differences_modQ=differences,literal_commit_reset_bits=zeros,literal_forwarded_Hold_Info_mask_identities=forward,
        universal_conditional_zero_GF_bank_closure_proved=True,
        binary_GF_common_clock_and_displacement_premises_required_at_each_iteration=True,
        arbitrary_pulses_satisfy_closure_premises_proved=False,
        initial_template_L_R=[128,144],actual_first_endpoint_template_L_R=[122,136],initial_zero_GF_primaries=initial_bank,
        initial_bank_zero_from_intact_upper_private_H2_required=True,
        first_boundary_computed_time=p.U,first_boundary_zero_primary_records=targets,
        initially_true_target_primaries=true,initial_complete_foreign_target_primaries=foreign,
        first_boundary_zero_GF_primaries=len(targets),first_boundary_zero_GF_Info_copies=5*len(targets),
        next_source_computed_time=p.U+p.T_wf,next_complete_foreign_MF509_one_colonies=list(range(122,136)),
        actual_first_boundary_zero_bank_and_next_complete_foreign_sources_proved=True,
        full_next_signal_mask_or_pulse_or_complete_upper_data_proved=False,
        general_clock_phase_width_fault_eroder_or_continuing_E0_proved=False,
        higher_error_map_or_positive_iid_rate_or_globally_minimal_repair_proved=False,
        arbitrary_pending_seeds_or_fresh_errors_allowed=False,numerical_whole_CA_trajectory_used=False,
        global_reliability_established=False,seconds=time.monotonic()-started)
    (out/'SP30_GF_bank_closure_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ('new_true_H2_issue_range','first_boundary_zero_GF_Info_copies',
        'next_complete_foreign_MF509_one_colonies','global_reliability_established','seconds')}),flush=True)


if __name__=='__main__':main()
