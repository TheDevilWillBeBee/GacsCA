"""Two-record native/copy absorption and exact padding contract reuse.

Full arbitrary-word quantification is in the accompanying written proof.
The finite checks cover the residual flag and in-colony categories and
prove exact three-clean-word VMAJ cases with arbitrary bit cubes.
"""
from pathlib import Path
from itertools import combinations,product
import hashlib,json,sys,time
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw21'
sys.path.insert(0,str(S.parent/'unregistered_gaw20'))
sys.path.insert(0,str(S.parent/'unregistered_gaw19'))
import check_gaw20_padding_congruence02 as contract
import gaw19_symbolic_executor as cubes
k=contract.k;own=contract.own

def main():
    started=time.monotonic();checks=0;dig=hashlib.sha256()
    cuts=sorted({0,k.Q,*range(1,6),*range(k.Q-5,k.Q)})
    # Every flag mask supported on <=2 records. Numeric bad GF/Age words
    # are handled by the three-clean quorum theorem; this concrete pair
    # puts both bad words in the unequal category of every mismatch test.
    supports=[()] + [(j,) for j in range(-5,6)] + list(combinations(range(-5,6),2))
    for phase,end in zip(cuts,cuts[1:]):
        assert all(tuple(0<=phase+j<k.Q for j in range(-5,6))==
                   tuple(0<=a+j<k.Q for j in range(-5,6)) for a in (phase,end-1))
        for theta in (0,k.U-1):
            for support in supports:
                for flags in product(range(16),repeat=len(support)):
                    cells={j:k.Cell(addr=(phase+j)%k.Q,age=theta) for j in range(-8,9)}
                    for j,f in zip(support,flags):
                        cells[j]=k.Cell(addr=(phase+j+17)%k.Q,age=(theta+8191)%k.U,
                            f1=f&1,f2=(f>>1)&1,wf1=(f>>2)&1,wf2=(f>>3)&1)
                    got=k.native_at(cells)
                    assert got==dict(addr=phase,age=(theta+1)%k.U,f1=0,f2=0,wf1=0,wf2=0),(phase,theta,support,flags,got)
                    checks+=1
                    dig.update(str((phase,theta,support,flags)).encode())
    # The exact accepted 100-bit cube primitive, not a selected payload:
    # in each5-vector, two chunks have all20 bits unknown and three are
    # the same known word. Every fallback bit may also be unknown.
    quorum=adjusted=0
    for bad in combinations(range(5),2):
        for value in (0,1,k.Q-1,k.U-1):
            packed=cubes.C(0)
            for i in range(5):
                word=cubes.B(0,(1<<20)-1) if i in bad else cubes.C(value)
                packed=cubes.bor(packed,cubes.shift(word,20*i))
            assert cubes.alu(k.ALU['VMAJ'],packed,cubes.TOP,cubes.TOP)==cubes.C(value)
            assert cubes.alu(k.ALU['VEXISTS'],packed,cubes.TOP,cubes.TOP)==cubes.C(1)
            quorum+=2
        for centre in (0,1,2,k.Q-3,k.Q-2,k.Q-1):
            for side in (-1,1):
                packed=cubes.C(0)
                for i in range(5):
                    word=cubes.B(0,(1<<20)-1) if i in bad else cubes.C((centre+side*(i+1))%k.Q)
                    packed=cubes.bor(packed,cubes.shift(word,20*i))
                adjustedVector=cubes.alu(k.ALU['VADDINDEX'],packed,cubes.C(-side),cubes.C(13))
                assert cubes.alu(k.ALU['VMAJ'],adjustedVector,cubes.TOP,cubes.TOP)==cubes.C(centre)
                adjusted+=1
    # These code functions are conditional on native quorum and newF1zero.
    # Their old receipt's four-clean sufficient hypothesis is not asserted
    # here. The written two-record lemma proves the required primitive
    # conditions with only three clean votes, without editing old sources.
    macros,raw,native=contract.native_contracts();guards,prefix=contract.paired_prefix(macros)
    assert len(raw)==14 and len(guards)==8 and prefix['paired_prefix_states']==2139
    assert prefix['body_cut_states']==51
    for pc in contract.ROWS:contract.row(pc)
    r=dict(Q=k.Q,U=k.U,error_lambda=24,error_separation=104,
        prepared_upper_record_count_at_most=2,arbitrary_replacement_bits=2*496*100,
        native_phase_predicate_partition=cuts,actual_scalar_flag_support_checks=checks,
        scalar_flag_support_digest_sha256=dig.hexdigest(),
        universal_two_unknown_word_quorum_cube_checks=quorum,
        three_clean_adjusted_GF_cube_checks=adjusted,
        universal_numeric_word_argument_supplied_in_written_proof=True,
        computed_F1_F2zero_but_upper_final_Workspace_only_equal_to_clean_R=True,
        native_and_full_SF_votes_have_at_least3_correct_identical_members=True,
        arbitrary_native_padding_is_retained_in_actual_lower_Info_History_and_Mem=True,
        reused_generic_exact_native_and_paired_prefix_code_contract=native,
        paired_prefix=prefix,all3726_actual_instructions_checked=True,
        GAW20_receipt_four_clean_premise_not_silently_assumed=True,
        generic_malformed_projection_or_arbitrary_geometry_work_repair=False,
        all_phase_global_physical_period_and_all_n_intact_corollary_supplied_by_written_proof=True)
    p=D/'GAW21_two_raw_record_certificate.json'
    if '--issue' in sys.argv:assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n')
    else:assert r==json.loads(p.read_text())
    print(json.dumps(dict(passed=True,elapsed_seconds=time.monotonic()-started,**r)),flush=True);return r

if __name__=='__main__':main()
