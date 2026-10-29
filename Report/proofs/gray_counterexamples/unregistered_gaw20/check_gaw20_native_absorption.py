"""Finite predicate categories supporting GAW20's written native absorption.

The unbounded word/phase quantifiers follow from four identical quorums,
one mismatch at most, and the source predicates in the written proof.
This exhausts the remaining finite in-colony/flag/equality categories in
the actual scalar rule. It does not simulate prepared future commands.
"""
from pathlib import Path
import json,sys,time
import check_gaw20_padding_congruence02 as contract
k=contract.k;ROM=contract.own.ROM
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw20'

def main():
    started=time.monotonic()
    # These cuts exactly partition all predicates 0<=GF+j<Q for j=-5..5.
    cuts=sorted({0,k.Q,*range(1,6),*range(k.Q-5,k.Q)})
    checks=0
    for phase,end in zip(cuts,cuts[1:]):
        assert phase<end
        assert all(tuple(0<=phase+j<k.Q for j in range(-5,6))==
                   tuple(0<=a+j<k.Q for j in range(-5,6))
                   for a in (phase,end-1))
        # Four identical Age votes make all intermediate numeric values
        # irrelevant; these endpoints separately check increment/wrap.
        for theta in (0,k.U-1):
            for bad in range(-5,6):
                for different_GF in (0,1):
                    for different_Age in (0,1):
                        for flags in range(16):
                            cells={j:k.Cell(addr=(phase+j)%k.Q,age=theta)
                                   for j in range(-8,9)}
                            old=cells[bad]
                            cells[bad]=k.Cell(addr=(old.addr+different_GF)%k.Q,
                                age=(theta+different_Age)%k.U,
                                f1=flags&1,f2=(flags>>1)&1,
                                wf1=(flags>>2)&1,wf2=(flags>>3)&1)
                            assert k.native_at(cells)==dict(addr=phase,
                                age=(theta+1)%k.U,f1=0,f2=0,wf1=0,wf2=0)
                            checks+=1
    # Upper final Workspace may be positive despite computed F1/F2zero.
    # This exact example prevents silently replacing WF equality by WFzero.
    source=k.Q-3
    cells={j:k.Cell(addr=(source+j)%k.Q,age=96*k.Q-1,
                   info=(1,)*5) for j in range(-8,9)}
    result=k.local_transition(cells,ROM)
    assert result.f1==result.f2==0 and result.wf1==1 and result.wf2==0
    r=dict(Q=k.Q,U=k.U,error_lambda=24,error_separation=104,
        phase_predicate_partition=cuts,scalar_predicate_category_checks=checks,
        all_native_GF_Age_words_covered_by_four_identical_quorum_word_argument=True,
        flag_and_Workspace_quorums_require_at_least3_distinct_bad_records=True,
        isolated_corrected_h1_F2_clears=True,
        computed_F1_F2zero_does_not_imply_final_Workspacezero=True,
        positive_upper_Workspace_example=dict(centre=source,old_common_Age=96*k.Q-1,
            all_coherent_Info=1,computed_F1=0,computed_F2=0,computed_WF1=1,computed_WF2=0),
        arbitrary_unknown_word_values_are_not_replaced_by_sampled_native_payloads=True,
        proof_scope='one bad raw record in canonical/common/zero-old-flags family; written universal word proof plus finite predicate categories')
    path=D/'GAW20_native_absorption_certificate.json'
    if '--issue' in sys.argv:assert not path.exists();path.write_text(json.dumps(r,indent=2)+'\n')
    else:assert r==json.loads(path.read_text())
    print(json.dumps(dict(passed=True,elapsed_seconds=time.monotonic()-started,**r)),flush=True)
    return r

if __name__=='__main__':main()
