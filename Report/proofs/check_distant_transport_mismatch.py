#!/usr/bin/env python3
"""Exact transport-coordinate refutation for retained SP24--SP26.

These proposals capture to distance37 but inherited a distance12 fast
mail window. The native and conditional abstract ROM proofs survive;
the claimed physical encoding lift is withdrawn. No trajectory sampled.
"""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import proposed_sparse_distant_power1024 as sp24
import proposed_sparse_distant_faster1024 as sp25
import proposed_sparse_distant_short1024 as sp26

def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def check_module(module):
    p=module.parameters();source=module.generated_source(p)
    # Pin the actual speed switch and mailbox update, not the verifier's
    # idealized speed-eight coordinate assumption.
    for text in (
        'p.age_code(g * Q + 12 * (Q // 8) + 1)',
        "n.MUX(fast_mail, lv(x - 8, 'mr'), lv(x - 1, 'mr'))",
        "n.MUX(fast_mail, lv(x + 8, 'ml'), lv(x + 1, 'ml'))"):
        assert source.count(text)==1,text
    table=module.dependency_table(p);offsets=sorted(set().union(*(set(r['offsets']) for r in table)))
    assert max(map(abs,offsets))==37 and p.Q==1024
    rows=[]
    for gather in p.gathers_q:
        for off in offsets:
            ticks=abs(off)*(p.Q//8)
            fast=min(ticks,12*(p.Q//8));slow=ticks-fast
            distance=8*fast+slow
            expected=abs(off)*p.Q
            rows.append(dict(gather_input_age=gather*p.Q,offset=off,
                capture_input_age=gather*p.Q+ticks+1,fast_shifts=fast,slow_shifts=slow,
                actual_distance=distance,required_distance=expected,
                correct_coordinate=distance==expected))
    bad=[r for r in rows if not r['correct_coordinate']]
    assert bad and all(abs(r['offset'])>12 for r in bad)
    witness=next(r for r in rows if r['offset']==37 and r['gather_input_age']==0)
    assert (witness['capture_input_age'],witness['fast_shifts'],witness['slow_shifts'],
            witness['actual_distance'],witness['required_distance'])==(4737,1536,3200,15488,37888)
    # In a quiet encoded start, Info is constant during all gathers and
    # all flag1 values are0. Load at gQ creates M at state gQ+1. Each
    # next shift follows the literal speed switch above. Five identical
    # copies preserve this exact reference under majority voting.
    # Thus the wrong primary at p+15488 is actually sampled, rather
    # than p+37888. For p=59 these are phase187/colony15 versus
    # phase59/colony37. Distinct upper state bits can independently
    # assign0/1 to those Info primaries in a complete encoding.
    assert divmod(59+15488,p.Q)==(15,187)
    assert divmod(59+37888,p.Q)==(37,59)
    assert 59 in module.layout(p) and 187 in module.layout(p)
    return dict(proposal_source_sha256=digest(Path(module.__file__)),
        generated_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        Q=p.Q,U=p.U,width=module.width(p),native_radius=37,
        actual_fast_maximum_offset=12,requested_maximum_offset=37,
        checked_coordinates=len(rows),failed_coordinates=len(bad),witness=witness,
        all_coordinates=rows,physical_gather_premise_refuted=True,
        conditional_abstract_ROM_proof_with_correct_gathers_invalidated=False,
        native_E0_plus_real1_proof_invalidated=False,
        complete_encoded_physical_simulation_proved=False,
        full_output_commutation_counterexample_established=False,
        epsilon_or_global_reliability_established=False)

def check_corrected_module(module):
    p=module.parameters();source=module.generated_source(p)
    assert source.count('p.age_code(g * Q + 37 * (Q // 8) + 1)')==1
    assert 'p.age_code(g * Q + 12 * (Q // 8) + 1)' not in source
    for text in ("n.MUX(fast_mail, lv(x - 8, 'mr'), lv(x - 1, 'mr'))",
                 "n.MUX(fast_mail, lv(x + 8, 'ml'), lv(x + 1, 'ml'))"):
        assert source.count(text)==1
    offsets=sorted(set().union(*(set(r['offsets']) for r in module.dependency_table(p))))
    assert len(offsets)==64 and max(map(abs,offsets))==37
    checked=0
    for i,gather in enumerate(p.gathers_q):
        for off in offsets:
            shifts=abs(off)*(p.Q//8)
            assert shifts<=37*(p.Q//8)
            assert 8*shifts==abs(off)*p.Q
            capture=gather*p.Q+shifts+1
            assert capture<(p.gathers_q[i+1]*p.Q if i<2 else p.E0)
            assert capture<min(p.courier_ticks()[1:])
            checked+=1
    return dict(source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        actual_fast_maximum_offset=37,requested_maximum_offset=37,
        checked_coordinates=checked,failed_coordinates=0,
        all_requested_gather_coordinates_proved=True,
        correct_native_controls_quiet_Flag1_and_consistent_copies_required=True,
        full_physical_noisy_induction_provided_by='ROBUSTNESS J135',
        iid_or_higher_error_theorem_proved=False)

def main():
    out=ROOT/'figs/robustness'
    result=dict(checker_sha256=digest(Path(__file__)),
        proposals={label:check_module(module) for label,module in
                   (('SP24',sp24),('SP25',sp25),('SP26',sp26))},
        exact_arithmetic_and_literal_source_proof=True,numerical_trajectory_used=False,
        withdrawn_claims=['ROBUSTNESS J130 physical lift','J131 physical lift','J132 physical lift'],
        historical_encoding_receipts={label:digest(out/(label+'_encoded_certificate.json'))
                                     for label in ('SP24','SP25','SP26')},
        withdrawn_original_encoding_receipts={label:dict(
            file=label+'_withdrawn_encoded_certificate.json',
            sha256=digest(out/(label+'_withdrawn_encoded_certificate.json')),
            checker_file=label+'_withdrawn_encoded_checker.py',
            checker_sha256=digest(out/(label+'_withdrawn_encoded_checker.py')))
            for label in ('SP24','SP25','SP26')},
        scope='wrong physical gather coordinates; native and conditional abstract programmes retained; final-map theorem unproved')
    (out/'distant_transport_mismatch_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({label:{k:v[k] for k in ('checked_coordinates','failed_coordinates','physical_gather_premise_refuted')}
                      for label,v in result['proposals'].items()}))

if __name__=='__main__':main()
