#!/usr/bin/env python3
"""Conditional SP29 GF-bank closure and actual fourth foreign sources."""
from itertools import product
from pathlib import Path
from types import FunctionType
import hashlib,json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,const_word
from gacsca import rule_g
import proposed_sparse_short_force1024 as proposed
import check_distant_epoch1024_encoded as encoded
from check_short_force1024_protected_scratch import blocked


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def quiet(p,L,R):
    a=L*p.Q-512;b=R*p.Q
    def template(x):return int(a<=x<b),int(a-512<=x<a or b-512<=x<b)
    native,_=proposed.proposed_build();refine=natives=0
    for edge in (a,b):
        for x in range(edge-40,edge+41):
            n=Net();age=[n.input(('common_clock',k)) for k in range(p.m)]
            cells={d:dict(addr=const_word((x+d+512*template(x+d)[0])%p.Q,p.k),age=age)
                for d in range(-32,33)}
            got,_=proposed.local.refine_one(n,cells,p,0)
            assert got['addr']==cells[0]['addr'] and got['age']==age;refine+=1
    for x in sorted(set(range(a-p.Q-40,a+p.Q+41))|set(range(b-p.Q-40,b+p.Q+41))):
        n=Net();age=[n.input(('common_clock',k)) for k in range(p.m)]
        cells={d:dict(addr=const_word((x+d+512*template(x+d)[0])%p.Q,p.k),age=age,
            f1=template(x+d)[1],f2=0,wf1=0,wf2=0) for d in range(-5,9)}
        got=native(n,cells,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,service_force=0)
        assert got['addr']==cells[0]['addr'] and got['age_now']==age
        assert got['f1']==template(x)[1] and got['f2']==0;natives+=1
    boundaries=(a-512,a,b-512,b)
    assert min(y-x for x,y in zip(boundaries,boundaries[1:]))>=512
    gates=0
    for edge in boundaries:
        for y in range(edge-3,edge+4):
            flagged=lambda x:template(x)[1]
            assert int(sum(not flagged(y+s) for s in range(-2,3))>=3)==int(not flagged(y));gates+=1
    return dict(L=L,R=R,interval=[a,b],refinement_cofactors=refine,native_cofactors=natives,
        quiet_gate_cofactors=gates,minimum_boundary_spacing=512)


def routes(p,L,R):
    a=L*p.Q-512;b=R*p.Q;strips=((a-512,a),(b-512,b))
    bank={j*p.Q+phase for j in range(L-1,R) for phase in range(571,581)}
    table=[r for r in proposed.dependency_table(p) if r['field']=='addr']
    total=direct=inside=erased=0;signature=hashlib.sha256()
    for h,row,gather in product(range(L,R),table,p.gathers_q):
        phase=row['address'];assert 59<=phase<=68
        y=h*p.Q-512+phase;assert y in bank
        for d in (0,*row['offsets']):
            source=y+d*p.Q
            if a<=source<b:assert source in bank;inside+=1
            else:assert blocked(strips,h-1,d,phase+512,p.Q);erased+=1
            if d==0:direct+=1
            else:
                capture=gather*p.Q+abs(d)*(p.Q//8)+1
                assert capture<p.E0 and 8*(capture-gather*p.Q-1)==abs(d)*p.Q
            signature.update(f'{h},{phase},{gather},{d},{source};'.encode());total+=1
    return dict(L=L,R=R,complete_foreign_frames=list(range(L,R)),routes=total,
        direct_checks=direct,inside_zero_bank_routes=inside,outside_cleared_routes=erased,
        route_signature_sha256=signature.hexdigest())


def main():
    start=time.monotonic();p=proposed.parameters();out=ROOT/'figs/robustness';candidate=proposed.load_artifact()
    old=json.loads((out/'SP29_protected_scratch_certificate.json').read_text())
    pulse=json.loads((out/'SP29_third_domain_pulse_certificate.json').read_text())
    previous=json.loads((out/'SP29_next_ghost_signal_certificate.json').read_text())
    assert pulse['actual_third_pulse_on_Z_proved'] and pulse['all_8192_masks_have_same_native_endpoint']
    assert pulse['final_native_singleton_quiet_template_proved'] and pulse['all_update_rows_GF_and_header_code_exact']
    assert pulse['initial_wrong_GF_interval']==[116*p.Q-512,128*p.Q]
    assert pulse['final_wrong_GF_interval']==[110*p.Q-512,120*p.Q]
    assert old['third_foreign_MF509_one_colonies']==list(range(116,128))
    assert old['second_boundary_GF_zero_copy_count']==650
    assert old['second_boundary_GF_zero_primaries']==[j*p.Q+phase for j in range(115,128) for phase in range(571,581)]
    assert previous['one_kind_pending_argument_required'] and not previous['initial_pending_arbitrary_allowed']
    assert candidate.digest()==previous['proposed_candidate_sha256']
    listing_path=out/'SP29_program_listing.json';listing=json.loads(listing_path.read_text())
    issues=[];keys=0
    for phase in (*range(59,69),*range(571,581)):
        found=[r for r in listing if r[4]==phase and r[6]==rule_g.K_HOLD];assert len(found)==1
        row=found[0];column=row[1]+(row[3]<<p.logNP)
        assert np.flatnonzero(((candidate.rom[phase]>>2)&3)==rule_g.K_HOLD).tolist()==[column]
        issue=p.E0+row[1]*p.PL+row[2]
        issues.append(dict(phase=phase,ROM_column=column,input_issue_age=issue,materialized_age=issue+2));keys+=candidate.rom.shape[1]
    assert keys==81920
    gf,h2=issues[:10],issues[10:];S=p.T_wf+6144
    assert (min(r['input_issue_age'] for r in gf),max(r['input_issue_age'] for r in gf))==(276520,278398)
    assert (min(r['input_issue_age'] for r in h2),max(r['input_issue_age'] for r in h2))==(352116,360605)
    assert max(r['materialized_age'] for r in gf)<p.T_wf
    assert min(r['materialized_age'] for r in h2)>S
    differences=sorted({(i-j)*p.delta%p.Q for i,j in product(range(p.fronts),repeat=2)})
    assert 512 not in differences and (p.fronts,p.delta,p.mux_front,p.sel_front)==(5,5,True,0)
    pending=0
    for kind,mask in product(range(5),range(32)):
        present=[(mask>>j)&1 for j in range(5)];words=[kind if v else 0 for v in present]
        vote=sum(int(sum((w>>b)&1 for w in words)>=3)<<b for b in range(p.PK))
        assert sum(present)<3 or vote==kind;pending+=1
    assert pending==160
    namespace=dict(encoded.__dict__,proposed=proposed)
    reset,forward=FunctionType(encoded.commit_interfaces.__code__,namespace,'commit_interfaces')(p)
    assert (reset,forward)==(807,5)
    geometry=[quiet(p,0,1),quiet(p,110,120)]
    route_checks=[routes(p,0,1),routes(p,0,2),routes(p,110,120)]
    assert route_checks[-1]['routes']==19500 and route_checks[-1]['direct_checks']==300
    class ZeroGF(Net):
        def input(self,key):
            if isinstance(key,tuple) and len(key)==4 and key[0]=='x' and key[2]=='addr':return 0
            return super().input(key)
    zero,_=proposed.full_net(p,ZeroGF)
    assert zero.outputs['y','f1',0]==1 and all(zero.outputs['y','addr',b]==0 for b in range(p.k))
    targets=[];initial_true=initial_foreign=0
    for j,bit in product(range(109,120),range(10)):
        y=j*p.Q+571+bit;a,b=pulse['final_wrong_GF_interval']
        assert a<=y-2-37 and y+2+37<b
        assert 58<=59+bit<901
        if j<115:origin=None;initial_true+=1
        else:
            origin=(j+1)*p.Q-512
            assert 116*p.Q-512<=origin and origin+p.Q<=128*p.Q
            assert y-origin==59+bit;initial_foreign+=1
        targets.append(dict(primary=y,bit=bit,initial_complete_foreign_origin=origin))
    assert (initial_true,initial_foreign,len(targets))==(60,50,110)
    dependencies=('SP29_next_ghost_signal_certificate.json','SP29_protected_scratch_certificate.json',
        'SP29_third_domain_pulse_certificate.json','SP29_first_signal_certificate.json',
        'SP29_front_certificate.json','SP29_encoded_certificate.json','SP29_encoding_family_certificate.json',
        'SP29_program_build.json','SP29_symbolic_schedule.json')
    result=dict(proposal='SP29',scope='J187 conditional bank induction across certified binary-phase pulses; actual ten fourth complete foreign sources only, no full fourth mask/pulse/eroder/iid',
        Q=p.Q,U=p.U,T_wf=p.T_wf,settled_local_age=S,
        checker_sha256=digest(__file__),written_proof_sha256=digest(ROOT/'Report/proofs/SP29_GF_BANK_CLOSURE.md'),
        proposal_source_sha256=digest(proposed.__file__),proposed_candidate_sha256=candidate.digest(),
        proposed_netlist_sha256=candidate.comp.digest,listing_sha256=digest(listing_path),
        source_helpers_sha256={name:digest(ROOT/name) for name in ('gacsca/rule.py','gacsca/rule_g.py','gacsca/netlist.py',
            'Report/proofs/check_distant_epoch1024_encoded.py','Report/proofs/check_short_force1024_protected_scratch.py')},
        receipt_dependencies_sha256={name:digest(out/name) for name in dependencies},
        retained_initial_checker_failure_assets_sha256={name:digest(out/name) for name in
            ('SP29_GF_bank_closure_initial_checker.py.txt','SP29_GF_bank_closure_initial_checker_failure.txt')},
        quiet_geometry_cofactors=geometry,route_classes=route_checks,
        legal_closed_clock_guard_cases_reused=previous['closed_legal_clock_guard_cases'],
        raw_twenty_phase_ROM_keys_checked=keys,Hold_issue_records=issues,
        one_kind_pending_presence_cases=pending,comb_tooth_differences_modQ=differences,
        literal_commit_reset_bits=reset,literal_forwarded_Hold_Info_mask_identities=forward,
        universal_conditional_zero_GF_bank_closure_proved=True,
        pulse_displacement_and_binary_clock_premises_required_at_each_iteration=True,
        arbitrary_pulse_or_error_histories_satisfy_premises_proved=False,
        third_boundary_computed_time=3*p.U,fourth_source_computed_time=3*p.U+p.T_wf,
        actual_old_template_L_R=[116,128],actual_new_template_L_R=[110,120],
        third_boundary_zero_primary_records=targets,initial_true_target_primaries=initial_true,
        initial_complete_old_foreign_target_primaries=initial_foreign,
        third_boundary_zero_GF_primaries=len(targets),third_boundary_zero_GF_Info_copies=5*len(targets),
        fourth_complete_foreign_MF509_one_colonies=list(range(110,120)),
        actual_fourth_complete_foreign_sources_proved=True,
        full_fourth_signal_or_pulse_or_complete_upper_data_proved=False,
        general_eroder_higher_map_or_positive_iid_rate_proved=False,
        arbitrary_pending_seeds_or_fresh_errors_allowed=False,numerical_whole_CA_trajectory_used=False,
        active_G17_modified=False,rule_programme_or_constant_change=False,global_reliability_established=False,
        seconds=time.monotonic()-start)
    path=out/'SP29_GF_bank_closure_certificate.json';path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ('quiet_geometry_cofactors','third_boundary_zero_GF_Info_copies',
        'fourth_complete_foreign_MF509_one_colonies','seconds','global_reliability_established')}),flush=True)


if __name__=='__main__':main()
