#!/usr/bin/env python3
"""Universal local h1 flag fronts and original-E0 charge geometry.

The noisy whole-word GF/Age majority implication is a separate elementary
lemma in the written proof. These exact cofactors certify the resulting
native flag equations, with all replacement flag bits free.
"""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from gacsca import maintenance
from gacsca.netlist import Net,const_word
import gray_staged_rule as proposed


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p=proposed.parameters(); phases=sorted({0,p.Q}|set(range(1,6))|set(range(p.Q-5,p.Q)))[:-1]
    cases=[]
    for which,positions in (('f1',(0,-1,-2)),('f2',(0,1,2))):
        for delta in positions:
            for pair in (None,*range(-6,6)):
                fault=set() if pair is None else {pair,pair+1}
                # Charge strips are relative to the tested target.
                strip=(set(range(-delta,5-delta)) if which=='f1' else
                       set(range(-4-delta,1-delta)))
                if delta and fault&strip: continue
                for phase in phases:
                    n=Net(); clock=[n.input(('clock',b)) for b in range(p.m)]
                    cells={}
                    for x in range(-5,6):
                        if which=='f1':
                            bg=dict(f1=int(delta+x<0),f2=1,wf1=0,wf2=0)
                        else:
                            bg=dict(f1=0,f2=int(delta+x>0),wf1=0,wf2=0)
                        cells[x]=dict(addr=const_word((phase+x)%p.Q,p.k),age=clock,
                            **{f:n.input(('arbitrary_replacement',x,f)) if x in fault else value
                               for f,value in bg.items()})
                    actual=maintenance.build(n,cells,p.k,p.m)
                    assert actual[which]==0,(which,delta,pair,phase)
                    if which=='f2': assert actual['f1']==0
                    cases.append(dict(flag=which,relative_to_boundary=delta,
                                      pair_left_offset=pair,phase=phase))
    assert len(cases)==616
    # A guaranteed boundary moves at most2 sites per row. Charge points
    # differ by atmost2*dt+4 sites; dt<10 is therefore (24,24)-linked.
    exclusions=[dict(tick_gap=dt,maximum_spatial_gap=2*dt+4) for dt in range(1,10)]
    assert all(row['tick_gap']<24 and row['maximum_spatial_gap']<24 for row in exclusions)
    ticks=next(n for n in range(p.Q+1) if 2*(n-((n+9)//10))>=p.Q)
    assert ticks==4552
    quiet=98*p.Q+2*ticks
    assert quiet==811920<100*p.Q<112*p.Q
    result=dict(candidate='GR1',Q=p.Q,U=p.U,error_lambda=24,error_separation_c=104,
        healthy_flag2_repair_h=1,exact_native_front_cofactors=len(cases),records=cases,
        common_clock_bits_symbolic=p.m,arbitrary_error_fields=['f1','f2','wf1','wf2'],
        current_GF_Age_error_words_handled_by_separate_majority_lemma=True,
        no_invention_inside_zero_suffix_or_prefix_proved=True,
        two_site_uncharged_growth_proved=True,
        charged_growth_lower_bound=0,uncharged_growth_lower_bound=2,
        charge_tick_gap_lower_bound=10,charge_exclusions=exclusions,
        worst_case_rows_per_sweep=ticks,worst_case_total_rows=2*ticks,
        computed_native_flags_quiet_by_age=quiet,
        flags_quiet_before_final_interpreter=True,
        pure_E0_flag_recovery_proved=True,
        hypotheses=['all physical errors form isolated spatial adjacent-pair/singleton groups at one tick, with distinct groups(24,24)-separated',
            'canonical GF/common Age outside current error sites, so both directional5-word votes restore the correct geometry and inconsistency isfalse',
            'Workspace flags are0 outside current errors during the interval beginning at98Q'],
        proof_scope='A guaranteed Flag1 zero suffix or Flag2 zero prefix never retreats. Each row advances2 unless its respective five-site charge strip meets current E0. Guaranteed boundaries advance atmost2, so distinct charge events less than10ticks apart contradict original E0 isolation. Atmostceil(n/10) rows are charged;4552 rows coverQ. Flag2 starts after global computedFlag1 quieting. The quiet state is stable under subsequent E0.',
        checker_sha256=digest(__file__),proposal_sha256=digest(proposed.__file__),
        active_native_source_sha256=digest(maintenance.__file__),
        full_physical_E0_lift_proved=False,real1_recovery_proved=False,
        iid_reliability_proved=False,gray_verbatim_simulation=False,global_reliability_established=False,
        measured_only=False)
    (ROOT/'figs/gray_counterexamples/GR1_E0_flag_recovery_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ('exact_native_front_cofactors',
        'charge_tick_gap_lower_bound','worst_case_rows_per_sweep','computed_native_flags_quiet_by_age',
        'pure_E0_flag_recovery_proved','full_physical_E0_lift_proved')}))


if __name__=='__main__': main()
