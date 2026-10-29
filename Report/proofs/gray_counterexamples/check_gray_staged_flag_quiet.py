#!/usr/bin/env python3
"""Healthy-geometry, noiseless h1 Flag clearing; not real1 recovery."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT)); sys.path.insert(0,str(ROOT/'Report/proofs'))
from gacsca import maintenance
from gacsca.netlist import Net,const_word,Compiled
from check_g17_schedule import Terms
import gray_staged_rule as proposed


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p=proposed.parameters(); boundaries=sorted({0,p.Q}|set(range(1,6))|set(range(p.Q-5,p.Q)))
    checked=[]
    for phase in boundaries[:-1]:
        for which in ('f1','f2'):
            n=Net(); clock=[n.input(('clock',b)) for b in range(p.m)]
            cells={x:dict(addr=const_word((phase+x)%p.Q,p.k),age=clock,
                f1=(n.input(('flag1',x)) if which=='f1' and x<=1 else 0),
                f2=(0 if which=='f2' and x<=-2 else n.input(('flag2',x))),
                wf1=0,wf2=(n.input(('workspace2',x)) if which=='f1' else 0))
                for x in range(-5,6)}
            result=maintenance.build(n,cells,p.k,p.m)
            # f1 may have one arbitrary flagged positive neighbour; every
            # other positive neighbour is zero. f2 is similarly allowed one
            # arbitrary flagged negative neighbour once f1 is identically0.
            assert result[which]==0,(phase,which)
            checked.append(dict(phase=phase,flag=which,symbolic_clock_bits=p.m))
    assert len(checked)==22
    result=dict(candidate='GR1',Q=p.Q,U=p.U,
        error_lambda=24,error_separation_c=104,healthy_flag2_repair_h=1,
        exact_native_boundary_cofactors=len(checked),address_partition_boundaries=boundaries,
        records=checked,
        workspace_pulse_end_age=98*p.Q,
        Flag1_clear_clean_ticks=(p.Q+1)//2,
        subsequent_Flag2_clear_clean_ticks=(p.Q+1)//2,
        all_flags_quiet_by_age=99*p.Q,
        Flag1_suffix_proof='With canonical GF/common Age and Workspace.Flag1=0, inconsistency is false. A cell with at most one possibly flagged positive in-colony neighbour computes Flag1=0. Starting at the right colony boundary, a zero suffix therefore grows by at least two cells per tick, regardless of the remaining input Flag1/Flag2 and Workspace.Flag2 values. Every colony clears within ceil(Q/2) clean ticks.',
        Flag2_prefix_proof='Once input Flag1=0 everywhere and both Workspace flags are0, computed Flag1=0. A cell with at most one possibly flagged negative in-colony neighbour computes Flag2=0 under the explicit h1 repair, regardless of its own Flag2 or flags outside the colony. Starting at the left boundary, a zero prefix grows by at least two cells per tick. Every colony clears within a further ceil(Q/2) clean ticks.',
        all_colony_flags_noiseless_clearing_proved=True,
        hypotheses=['canonical GF/common Age throughout, so the canonical native-geometry invariant applies',
            'Workspace.Flag1=Workspace.Flag2=0 on every site for the complete Q-tick clearing interval',
            'no errors during that interval'],
        not_proved=['clearing with E0 errors continuing','geometry recovery from real1 corruption','literal printed Flag2 clause clearing','iid reliability'],
        checker_sha256=digest(__file__),native_source_sha256=digest(maintenance.__file__),
        proposal_sha256=digest(proposed.__file__),
        native_geometry_receipt_sha256=digest(ROOT/'figs/gray_counterexamples/native_geometry_invariant_certificate.json'),
        measured_only=False,full_physical_E0_lift_proved=False,global_reliability_established=False)
    (ROOT/'figs/gray_counterexamples/GR1_flag_quiet_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(exact_native_boundary_cofactors=len(checked),
        all_flags_quiet_by_age=result['all_flags_quiet_by_age'],
        all_colony_flags_noiseless_clearing_proved=True)))


if __name__=='__main__': main()
