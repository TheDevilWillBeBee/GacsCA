#!/usr/bin/env python3
"""F31 specified-history GF bank/source proof certificate; no rule change."""
from collections import Counter
from itertools import product
from pathlib import Path
import hashlib, json, sys, time
import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,const_word
from gacsca import rule_g
import proposed_native_command1024 as proposed
import check_native_command1024_first_pulse as first
import check_native_command1024_encoded as encoded

OUT=ROOT/'figs/robustness'
PROOF=Path(__file__).with_name('SP31_ONE_EXCEPTION_BANK.md')

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    started=time.monotonic();p=proposed.parameters();c=proposed.load_artifact()
    prior=json.loads((OUT/'SP31_first_pulse_certificate.json').read_text())
    assert prior['candidate_sha256']==c.digest()
    assert prior['same_actual_intact_start_single_error_row_first_pulse_proved']
    assert prior['all_initial_upper_Info_payloads_and_both_partial_Flag2_votes_allowed']
    assert prior['initial_native_template']==[128,143] and prior['endpoint_native_template']==[135,146]
    assert prior['computed_first_boundary_native_template_and807_reset_proved']
    assert prior['proof_sha256']==sha(first.PROOF)
    for row in prior['exact_four_runs']:
        assert row['endpoint_template']==[135,146] and row['updates']==6144
        assert row['trace_sha256']==sha(OUT/'SP31_two_sources'/('mask%d_trace.jsonl'%row['mask']))
    S=p.T_wf+6144;listing_path=OUT/'SP31_program_listing.json'
    listing=json.loads(listing_path.read_text());issues=[];keys=0
    for phase in (*range(59,69),*range(571,581)):
        rows=[r for r in listing if r[4]==phase and r[6]==rule_g.K_HOLD];assert len(rows)==1
        row=rows[0];column=row[1]+(row[3]<<p.logNP)
        assert np.flatnonzero(((c.rom[phase]>>2)&3)==rule_g.K_HOLD).tolist()==[column]
        issue=p.E0+row[1]*p.PL+row[2]
        issues.append(dict(phase=phase,ROM_column=column,input_issue_age=issue,materialized_age=issue+2))
        keys+=c.rom.shape[1]
    gf,h2=issues[:10],issues[10:]
    assert keys==81920
    assert [min(r['input_issue_age'] for r in gf),max(r['input_issue_age'] for r in gf)]==[257963,259827]
    assert [min(r['input_issue_age'] for r in h2),max(r['input_issue_age'] for r in h2)]==[360587,370671]
    assert max(r['materialized_age'] for r in gf)<p.T_wf and min(r['materialized_age'] for r in h2)>S
    differences=sorted({(i-j)*p.delta%p.Q for i,j in product(range(p.fronts),repeat=2)})
    assert 512 not in differences and (p.fronts,p.delta,p.mux_front,p.sel_front,p.PK,p.NH,p.S)==(5,5,True,0,3,1,4)
    pending=0
    for kind,mask in product(range(5),range(32)):
        present=[(mask>>i)&1 for i in range(5)];words=[kind if v else 0 for v in present]
        voted=sum(int(sum((w>>b)&1 for w in words)>=3)<<b for b in range(p.PK))
        assert sum(present)<3 or voted==kind
        pending+=1
    zeros,forward=encoded.commit(p);assert (zeros,forward)==(807,5)
    targets=[];counts=Counter();a,b=135*p.Q-512,146*p.Q
    for j,k in product(range(134,146),range(10)):
        y=j*p.Q+571+k
        assert a<=y-2-37 and y+2+37<b and 59+k in c.layout
        if j<=141:
            role='old_complete_foreign';origin=(j+1)*p.Q-512
            assert 128*p.Q-512<=origin and origin+1023<143*p.Q
            assert y-origin==59+k
        elif j==142:role='old_partial_foreign';origin=143*p.Q-512
        else:role='newly_entered_true';origin=None
        counts[role]+=1
        targets.append(dict(colony=j,bit=k,primary=y,provenance=role,old_origin=origin,
                            first_boundary_value='q_bit' if j==142 else 0))
    assert dict(counts)==dict(old_complete_foreign=80,old_partial_foreign=10,newly_entered_true=30)
    bank={r['primary'] for r in targets};strips=((134*p.Q,a),(b-512,b))
    table=[r for r in proposed.dependency_table(p) if r['field']=='addr']
    assert [r['address'] for r in table]==list(range(59,69))
    routes=direct=inside=inside_blocked=erased=exceptions=0;signature=hashlib.sha256();frames=[]
    for h in range(135,146):
        origin=h*p.Q-512
        assert a<=origin+1 and origin+1023<b
        assert all(not any(lo<=y<hi for lo,hi in strips) for y in (origin+1,origin+1023))
        ell=143-h;assert -2<=ell<=8
        frames.append(dict(virtual_colony=h,origin=origin,exception_raw_offset=ell,
                           Flag1=1,GF='q' if h==143 else 0,physical_MF509_primary=(h-1)*p.Q+509))
        for row,gather in product(table,p.gathers_q):
            phase=row['address'];y=origin+phase;assert y in bank
            for d in (0,*row['offsets']):
                source=y+d*p.Q
                crossed=first.blocked(strips,h-1,d,phase+512,p.Q)
                assert crossed==first.blocked(strips,h-1,d,571,p.Q)
                if a<=source<b:
                    assert source in bank
                    # Already-zero sources inside the right strip may
                    # be erased. The sole q source is interior.
                    if h+d==143:assert not crossed
                    inside+=1;inside_blocked+=int(crossed);exceptions+=int(h+d==143)
                else:assert crossed;erased+=1
                if d==0:direct+=1
                else:
                    capture=gather*p.Q+abs(d)*(p.Q//8)+1
                    assert capture<p.E0 and 8*(capture-gather*p.Q-1)==abs(d)*p.Q
                signature.update(f'{h},{phase},{gather},{d},{source},{crossed};'.encode());routes+=1
    assert (routes,direct)==(21450,330)
    vote_checks=0
    for at,q in product(range(5),range(p.Q)):
        raw=[0]*5;raw[at]=q
        adjusted=[(v-j)%p.Q for j,v in enumerate(raw)]
        assert max(Counter(adjusted).values())<=2;vote_checks+=1
    build,maintenance_source=proposed.proposed_build();cofactors=0;cofactor_sig=hashlib.sha256()
    for ell,q in product(range(-2,9),range(p.Q)):
        n=Net()
        cells={j:dict(addr=const_word(q if j==ell else 0,p.k),
            age=[n.input(('age',j,k)) for k in range(p.m)],
            **{f:n.input((f,j)) for f in ('f1','f2','wf1','wf2')}) for j in range(-5,9)}
        got=build(n,cells,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,service_force=0)
        assert got['f1']==1 and got['addr']==cells[0]['addr'],(ell,q)
        cofactor_sig.update(f'{ell},{q},1,{q if ell==0 else 0};'.encode());cofactors+=1
    assert cofactors==11264
    print(json.dumps(dict(actual_maintenance_all_q_cofactors=cofactors,all_non_GF_native_inputs_free=True)),flush=True)
    # Selected full functions supplement the universal counting/refinement
    # argument. No conclusion relies on sampling the unlisted q values.
    selected_q=(0,1,2,3,4,5,7,15,31,63,127,255,511,512,1022,1023)
    full=0;full_sig=hashlib.sha256()
    for ell,q in product(range(-2,9),selected_q):
        class Captured(Net):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x' and key[2]=='addr':
                    return ((q if key[1]==ell else 0)>>key[3])&1
                return super().input(key)
        n,_=proposed.full_net(p,Captured)
        assert n.outputs['y','f1',0]==1,(ell,q,'f1')
        assert [n.outputs['y','addr',k] for k in range(p.k)]==const_word(q if ell==0 else 0,p.k),(ell,q,'GF')
        full_sig.update(f'{ell},{q};'.encode());full+=1
    assert full==176
    assert proposed.flag_store_cells(p)==(965,58) and p.courier_ticks()==(278343,278344,278343)
    assert 278343+(1021-965)+2==p.T_wf
    dependencies=('SP31_first_pulse_certificate.json','SP31_encoded_certificate.json',
        'SP31_front_certificate.json','SP31_native_certificate.json','SP31_interface_certificate.json',
        'SP31_program_build.json','SP31_symbolic_schedule.json')
    result=dict(proposal='SP31',scope='J227 same actual first fault: one-exception GF bank and eleven next complete foreign Flag1 sources; no full second signal/pulse/general repair',
        Q=p.Q,U=p.U,T_wf=p.T_wf,settled_local_age=S,candidate_sha256=c.digest(),netlist_sha256=c.comp.digest,
        checker_sha256=sha(__file__),proof_sha256=sha(PROOF),proposal_source_sha256=sha(proposed.__file__),
        generated_source_sha256=hashlib.sha256(proposed.generated_source(p).encode()).hexdigest(),listing_sha256=sha(listing_path),
        maintenance_source_sha256=hashlib.sha256(maintenance_source.encode()).hexdigest(),
        source_dependencies_sha256={name:sha(ROOT/name) for name in ('gacsca/rule_g.py','gacsca/netlist.py',
            'Report/proofs/check_native_command1024_first_pulse.py','Report/proofs/proposed_distant_native448.py',
            'Report/proofs/check_native_command1024_encoded.py')},
        proof_dependencies_sha256={name:sha(PROOF.parent/name) for name in ('SP31_FIRST_PULSE.md','SP31_OWN_RULE.md')},
        receipt_dependencies_sha256={name:sha(OUT/name) for name in dependencies},
        actual_twenty_phase_ROM_keys=keys,Hold_issue_records=issues,
        GF_input_issue_range=[257963,259827],true_H2_input_issue_range=[360587,370671],
        one_kind_pending_presence_cases=pending,comb_tooth_differences_modQ=differences,
        literal_commit_reset_bits=zeros,literal_masked_Hold_Info_forwarding_identities=forward,
        actual_first_boundary_GF_bank_records=targets,bank_provenance_counts=dict(counts),
        first_boundary_GF_primaries=120,first_boundary_zero_GF_primaries=110,first_boundary_zero_GF_Info_copies=550,
        exceptional_GF_word_primary_colony=142,exceptional_GF_word_range=[0,p.Q],exceptional_GF_Info_copies=50,
        first_boundary_time=p.U,next_source_time=p.U+p.T_wf,
        next_complete_foreign_frames=frames,next_physical_MF509_one_colonies=list(range(134,145)),
        actual_GF_capture_routes=routes,direct_GF_reads=direct,inside_bank_routes=inside,
        inside_zero_bank_routes_also_erased=inside_blocked,outside_erased_routes=erased,
        single_exception_routes=exceptions,route_signature_sha256=signature.hexdigest(),
        universal_single_GF_exception_refinement_and_native_response_proved=True,
        primitive_all_q_vote_checks=vote_checks,actual_maintenance_all_q_cofactors=cofactors,
        maintenance_cofactor_signature_sha256=cofactor_sig.hexdigest(),
        selected_full_F31_cofactors=full,selected_full_F31_q_values=list(selected_q),
        selected_full_F31_signature_sha256=full_sig.hexdigest(),selected_full_F31_checks_measured_only=True,
        same_actual_J225_first_boundary_one_exception_bank_proved=True,
        all_initial_upper_Info_and_all_exception_words_and_other_captured_fields_allowed=True,
        actual_next_eleven_complete_foreign_Flag1_commands_proved=True,
        no_independent_future_tape_or_Workspace_prescribed=True,
        retained_initial_checker_failure_assets_sha256={name:sha(OUT/name) for name in
            ('SP31_one_exception_bank_initial_checker.py.txt','SP31_one_exception_bank_initial_failure.log')},
        additional_rule_change=False,active_G17_modified=False,numerical_whole_CA_trajectory_used=False,
        full_second_signal_or_Flag2_sources_or_pulse_proved=False,
        repeated_one_exception_bank_invariant_proved=False,general_higher_repair_or_positive_iid_epsilon_proved=False,
        smallest_globally_sufficient_change_proved=False,Gray_or_G17_refutation=False,
        global_reliability_established=False,seconds=time.monotonic()-started)
    (OUT/'SP31_one_exception_bank_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('same_actual_J225_first_boundary_one_exception_bank_proved',
        'first_boundary_zero_GF_Info_copies','next_physical_MF509_one_colonies',
        'global_reliability_established','seconds')}),flush=True)

if __name__=='__main__':main()
