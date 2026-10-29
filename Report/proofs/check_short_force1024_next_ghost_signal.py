#!/usr/bin/env python3
"""Exact first-boundary zero-GF and next foreign-signal interfaces, J169."""
from itertools import product
from pathlib import Path
from types import FunctionType
import hashlib
import json
import sys
import time
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,Compiled,const_word,w_eq_const,w_in_range
from gacsca import rule_g
import proposed_sparse_short_force1024 as proposed
import check_distant_epoch1024_encoded as encoded


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    start=time.monotonic();p=proposed.parameters();out=ROOT/'figs/robustness'
    candidate=proposed.load_artifact()
    first=json.loads((out/'SP29_first_signal_certificate.json').read_text())
    pulse=json.loads((out/'SP29_first_pulse_certificate.json').read_text())
    assert first['exact_first_signal_physical_history_proved']
    assert pulse['actual_first_period_supplied_signal_pulse_proved']
    assert candidate.digest()==first['proposed_candidate_sha256']
    old_a,old_b=130560,147456
    a,b=124416,139264
    settled=p.T_wf+6144
    assert pulse['final_native_GF_interval']==[a,b] and settled==284545

    # The changed endpoint has the same edge phases and widely disjoint
    # radius37 neighbourhoods. These are symbolic common-clock cofactors.
    def template(x):
        return int(a<=x<b),int(a-512<=x<a or b-512<=x<b)
    native,native_source=proposed.proposed_build()
    refine_cases=native_cases=0
    for edge in (a,b):
        for x in range(edge-40,edge+41):
            n=Net();age=[n.input(('common_clock',k)) for k in range(p.m)]
            cells={j:dict(addr=const_word((x+j+512*template(x+j)[0])%p.Q,p.k),age=age)
                   for j in range(-32,33)}
            got,_=proposed.local.refine_one(n,cells,p,0)
            assert got['addr']==cells[0]['addr'] and got['age']==age
            refine_cases+=1
    for x in sorted(set(range(a-p.Q-40,a+p.Q+41))|set(range(b-p.Q-40,b+p.Q+41))):
        n=Net();age=[n.input(('common_clock',k)) for k in range(p.m)]
        cells={j:dict(addr=const_word((x+j+512*template(x+j)[0])%p.Q,p.k),age=age,
            f1=template(x+j)[1],f2=0,wf1=0,wf2=0) for j in range(-5,9)}
        got=native(n,cells,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,service_force=0)
        assert got['addr']==cells[0]['addr'] and got['age_now']==age
        assert got['f1']==template(x)[1] and got['f2']==0
        native_cases+=1
    assert (refine_cases,native_cases)==(162,4258)
    assert (a-old_a,b-old_b)==(-6*p.Q,-8*p.Q)

    guard=Net();age=[guard.input(('age',bit)) for bit in range(p.m)]
    guard.set_output(('birth',),w_eq_const(guard,age,p.age_code(p.T_wf)))
    guard.set_output(('force',),w_in_range(guard,age,p.age_code(p.T_wf),p.age_code(p.T_wf+2048)))
    guard.set_output(('WF1',),w_in_range(guard,age,p.age_code(p.T_wf),p.age_code(p.T_wf+2*p.Q-1)+1))
    clocks=np.concatenate((np.arange(settled,p.U),np.arange(p.T_wf)))
    codes=np.array([p.age_code(int(t)) for t in clocks],dtype=np.uint32)
    observed=Compiled(guard).evaluate({('age',bit):((codes>>bit)&1).astype(bool) for bit in range(p.m)},bool)
    assert len(clocks)==468992 and all(not values.any() for values in observed.values())

    # Reuse the all-raw refined-GF commit cofactor, binding it to SP29.
    namespace=dict(encoded.__dict__,proposed=proposed)
    commit=FunctionType(encoded.commit_interfaces.__code__,namespace,'commit_interfaces')
    reset_bits,info_identities=commit(p)
    assert (reset_bits,info_identities)==(807,5)

    listing_path=out/'SP29_program_listing.json'
    listing=json.loads(listing_path.read_text())
    table=proposed.dependency_table(p)
    phases=list(range(59,69))+list(range(571,581))
    issues=[];rom_keys=0
    for phase in phases:
        found=[row for row in listing if row[4]==phase and row[6]==rule_g.K_HOLD]
        assert len(found)==1,(phase,found)
        row=found[0]
        expected_column=row[1]+(row[3]<<p.logNP)
        holding_columns=np.flatnonzero(((candidate.rom[phase]>>2)&3)==rule_g.K_HOLD).tolist()
        assert holding_columns==[expected_column]
        issue=p.E0+row[1]*p.PL+row[2]
        issues.append(dict(phase=phase,sequence=row[0],page=row[1],tick=row[2],front=row[3],
                           ROM_column=expected_column,input_issue_age=issue,materialized_state_age=issue+2))
        rom_keys+=candidate.rom.shape[1]
    assert rom_keys==81920
    gf_issues=issues[:10];h2_issues=issues[10:]
    assert (min(row['input_issue_age'] for row in gf_issues),max(row['input_issue_age'] for row in gf_issues))==(276520,278398)
    assert (min(row['input_issue_age'] for row in h2_issues),max(row['input_issue_age'] for row in h2_issues))==(352116,360605)
    assert max(row['materialized_state_age'] for row in gf_issues)<p.T_wf
    assert min(row['materialized_state_age'] for row in h2_issues)>settled
    differences={(i-j)*p.delta%p.Q for i,j in product(range(p.fronts),repeat=2)}
    assert 512 not in differences and (p.fronts,p.delta,p.mux_front,p.sel_front)==(5,5,True,0)
    assert p.MP not in {row['page'] for row in issues}

    pending_cases=0
    for destination in range(5):
        for mask in range(32):
            presence=[(mask>>j)&1 for j in range(5)]
            voted_presence=int(sum(presence)>=3)
            kinds=[destination if present else 0 for present in presence]
            voted_kind=sum(int(sum((kind>>bit)&1 for kind in kinds)>=3)<<bit for bit in range(p.PK))
            assert not voted_presence or voted_kind==destination
            assert bool(voted_presence and voted_kind==0)==bool(voted_presence and destination==0)
            pending_cases+=1
    assert pending_cases==160

    targets=[];initial_true=initial_foreign=0
    for j in range(121,136):
        for bit in range(10):
            y=j*p.Q+571+bit
            assert a<=y-2 and y+2<b
            if y<old_a:
                assert j<=126 and y+2<old_a
                origin=None;initial_true+=1
            else:
                origin=(j+1)*p.Q-512
                assert old_a<=origin and origin+p.Q<=old_b
                assert y-origin==59+bit
                initial_foreign+=1
            targets.append(dict(primary=y,true_phase=571+bit,bit=bit,initial_foreign_origin=origin))
    assert (initial_true,initial_foreign,len(targets))==(60,90,150)
    zero_primaries={row['primary'] for row in targets}

    # Exact arithmetic-progression routes, including all sparse ranks.
    strips=((a-512,a),(b-512,b))
    routes=inside=blocked=direct=0
    for h in range(122,136):
        for row in (entry for entry in table if entry['field']=='addr'):
            for gather in p.gathers_q:
                y=h*p.Q-512+row['address']
                assert y in zero_primaries and 59<=y-(h*p.Q-512)<=68
                for d in (0,*row['offsets']):
                    source=y+d*p.Q
                    lo,hi=sorted((source,y))
                    crosses=any(lo+8*max(0,(left-lo+7)//8)<=min(hi,right-1) for left,right in strips)
                    if a<=source<b:
                        assert source in zero_primaries
                        inside+=1
                    else:
                        assert crosses,(h,row['bit'],d,source)
                        blocked+=1
                    if d==0:
                        direct+=1
                    else:
                        capture=gather*p.Q+abs(d)*(p.Q//8)+1
                        assert capture<p.E0 and 8*(capture-gather*p.Q-1)==abs(d)*p.Q
                    routes+=1
    assert (routes,direct)==(27300,420) and inside+blocked==routes
    gate_boundary_cases=0
    for edge in (a-512,a,b-512,b):
        for y in range(edge-3,edge+4):
            flagged=lambda x:any(left<=x<right for left,right in strips)
            assert int(sum(not flagged(y+s) for s in range(-2,3))>=3)==int(not flagged(y))
            gate_boundary_cases+=1
    assert gate_boundary_cases==28
    class ZeroGF(Net):
        def input(self,key):
            if isinstance(key,tuple) and len(key)==4 and key[0]=='x' and key[2]=='addr':
                return 0
            return super().input(key)
    zero,_=proposed.full_net(p,ZeroGF)
    assert zero.outputs['y','f1',0]==1 and all(zero.outputs['y','addr',bit]==0 for bit in range(p.k))
    dependencies=('SP29_first_signal_certificate.json','SP29_first_pulse_certificate.json',
        'SP29_program_build.json','SP29_symbolic_schedule.json','SP29_native_certificate.json',
        'SP29_front_certificate.json','SP29_encoded_certificate.json','SP29_encoding_family_certificate.json')
    result=dict(proposal='SP29',scope='J169 actual first boundary zero-GF code and next fourteen complete foreign signals, same J167 initial error/no later errors; no second full signal or shrinking/eroder/iid theorem',
        checker_sha256=digest(__file__),written_proof_sha256=digest(ROOT/'Report/proofs/SP29_NEXT_GHOST_SIGNAL.md'),
        proposal_source_sha256=digest(proposed.__file__),proposed_candidate_sha256=candidate.digest(),
        proposed_netlist_sha256=candidate.comp.digest,listing_sha256=digest(listing_path),
        source_helpers_sha256={name:digest(ROOT/name) for name in ('gacsca/rule.py','gacsca/rule_g.py',
            'gacsca/netlist.py','Report/proofs/check_distant_epoch1024_encoded.py')},
        actual_maintenance_source_sha256=hashlib.sha256(native_source.encode()).hexdigest(),
        full_generated_source_sha256=hashlib.sha256(proposed.generated_source(p).encode()).hexdigest(),
        Q=p.Q,U=p.U,T_wf=p.T_wf,force_duration=2048,initial_native_GF_interval=[old_a,old_b],
        first_pulse_endpoint=settled,first_boundary_native_GF_interval=[a,b],
        quiet_refinement_cofactors=refine_cases,quiet_native_cofactors=native_cases,
        closed_legal_clock_guard_cases=len(clocks),literal_commit_reset_bits=reset_bits,
        literal_forwarded_Hold_Info_mask_identities=info_identities,
        raw_twenty_phase_ROM_keys_checked=rom_keys,Hold_issue_records=issues,
        one_kind_pending_presence_cases=pending_cases,comb_phase_difference=512,
        comb_tooth_differences_modQ=sorted(differences),first_boundary_zero_primary_records=targets,
        initial_true_zero_Hold_primaries=initial_true,initial_complete_foreign_GF_zero_primaries=initial_foreign,
        first_boundary_zero_GF_primaries=len(targets),first_boundary_zero_GF_Info_copies=5*len(targets),
        next_complete_foreign_frame_colonies=list(range(122,136)),next_ghost_MF509_one_colonies=list(range(122,136)),
        next_GF_route_cases=routes,next_actual_capture_path_cases=routes-direct,
        next_direct_source_checks=direct,inside_zero_GF_route_cases=inside,
        outside_Flag1_blocked_route_cases=blocked,fixed_gate_boundary_cases=gate_boundary_cases,
        all_other_Info_payloads_at_first_boundary_allowed=True,
        first_native_boundary_and_zero_GF_code_proved=True,
        actual_next_complete_foreign_GF_zero_and_Flag1_signal_proved=True,
        one_kind_pending_argument_required=True,initial_pending_arbitrary_allowed=False,
        full_second_MF509_or_MF1021_track_proved=False,second_actual_shrinking_pulse_proved=False,
        complete_upper_data_restoration_proved=False,general_eroder_or_higher_map_or_iid_rate_proved=False,
        numerical_whole_CA_trajectories_used=False,additional_rule_change=False,
        active_G17_modified=False,global_reliability_established=False,
        receipt_dependencies_sha256={name:digest(out/name) for name in dependencies},
        seconds=time.monotonic()-start)
    (out/'SP29_next_ghost_signal_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ('quiet_native_cofactors','literal_commit_reset_bits',
        'first_boundary_zero_GF_Info_copies','next_ghost_MF509_one_colonies',
        'next_GF_route_cases','seconds','global_reliability_established')}),flush=True)


if __name__=='__main__':
    main()
