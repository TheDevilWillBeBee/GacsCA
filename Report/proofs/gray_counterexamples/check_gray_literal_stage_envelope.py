#!/usr/bin/env python3
"""Constituents of the conditional literal-stage/Proposition4 contradiction.

This is not a compiled Gray rule or a physical counterexample run. G/R
are explicit unverified refinement assumptions in the written theorem.
No GR1 own programme, rule, transport or experimental receipt is used.
"""
from pathlib import Path
from functools import lru_cache
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from gacsca import maintenance,gray_errors
from gacsca.netlist import Net,const_word,w_add_const,at_least
import literal_maintenance as literal


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def symbolic_initialization_example(Q):
    """Illustrative encoding frame, not Gray's actual fields or layout.

    beta/gamma values are arbitrary symbolic atoms, not an all-zero
    programme. The universal case split is proved in the document; the
    finite example only pins the executable interpretation of those cases.
    """
    schema=(('addr',13),('age',20),('flag',2),('simbit',5),('work',8),('mail',4))
    tags=[(f,b) for f,w in schema for b in range(w)]
    first=4096-tags.index(('work',2))
    layout={tag:first+row for row,tag in enumerate(tags)}
    reverse={a:tag for tag,a in layout.items()}
    slots=(0,-2,-1,1,2)
    assert all(4<=layout['simbit',b]<=Q-4 for b in range(5))
    assert not set(reverse)&{0,3,Q-3}
    beta=lambda i:('arbitrary_correct_programme_bit',i%Q)
    gamma=lambda a:('arbitrary_unused_marker_bit',a)
    @lru_cache(maxsize=None)
    def D(x):
        i,a=divmod(x,Q)
        if a==0:return beta(i)  # p31–32 lifted ProgramBit auxiliary.
        if a in (3,Q-3):return 0
        tag=reverse.get(a)
        if tag is None:return gamma(a)
        f,b=tag
        if f=='addr':return ((i%Q)>>b)&1
        if f=='simbit':
            nxt=i+slots[b]
            assert abs(nxt)<abs(x)
            return D(nxt)
        return 0
    def raw(x,f,b):
        if f=='addr':return ((x%Q)>>b)&1
        if f=='simbit':return D(x+slots[b])
        return 0
    examples=sorted(set(range(-8,9))|{s*(Q**e+d) for s in (-1,1)
        for e in (1,2,8,32) for d in (0,1,Q-1)})
    checks=0
    for i in examples:
        assert D(i*Q)==beta(i)
        for f,b in tags:
            assert D(i*Q+layout[f,b])==raw(i,f,b)
            checks+=1
    y=layout['work',2]
    assert y==4096 and D(y)==0
    assert D(0)==beta(0) and D(0)!=0
    assert D(3)==D(Q-3)==0
    return dict(kind='Illustrative52-bit symbolic encoding frame only, not Gray actual field sizes/layout, a CA or a compiled programme.',
        schema=schema,represented_primary_example=y,
        arbitrary_correct_ProgramBits_symbolic=True,unused_marker_bits_symbolic=True,
        upper_cell0_not_all_zero=True,lifted_ProgramBit_auxiliary_consistent=True,
        represented_Workspace_example_zero_independently_of_programme=True,
        examples=examples,finite_encoding_equalities=checks,
        finite_examples_not_basis_of_universal_initialization_proof=True)


def main():
    started=time.monotonic(); Q,U=literal.Q,literal.U
    directory=ROOT/'figs/gray_counterexamples'
    # Compile the exact literal generator once; scanning native phases does
    # not repeatedly import, inspect or mutate the active source.
    namespace=dict(maintenance.__dict__)
    exec(compile(literal.generated_source(),'<literal Gray native equations>','exec'),namespace)
    build=namespace['build']
    for phase in range(Q):
        n=Net(); age=[n.input(('free_common_clock',b)) for b in range(literal.M)]
        cells={j:dict(addr=const_word((phase+j)%Q,literal.K),age=age,
                     f1=0,f2=0,wf1=0,wf2=0) for j in range(-5,6)}
        out=build(n,cells,literal.K,literal.M)
        assert out['addr']==const_word(phase,literal.K)
        assert out['age_now']==age and out['age']==w_add_const(n,age,1)
        assert out['f1']==out['f2']==0
    # Primary and four secondary holder copies of this one logical bit.
    # Group-value assertions are actual Boolean majority computations.
    clean=[0]*5; corrupted=[0,1,1,1,0]
    n=Net(); first=at_least(n,corrupted,3)
    assert first==1 and at_least(n,[first]*5,3)==1
    assert at_least(n,clean,3)==0
    y=4096; points=[(y+d,1) for d in (-1,0,1)]
    classification=gray_errors.classify(points,Q=Q,U=U,sep=104)
    assert classification['level0']==0 and classification['level1']
    assert tuple(classification['extent'])==(3,1)
    assert not gray_errors.level0_points(points)
    # Stage arithmetic and spatial interval obstruction only. No asserted
    # raw mail route, loop controller, time-U physical run or ROM.
    second_start=U//4; second_active_end=second_start+U//8
    third_start=U//2; T=(second_active_end+third_start)//2
    assert (second_start,second_active_end,third_start,T)==(32*Q,48*Q,64*Q,56*Q)
    assert second_active_end<T<third_start<3*U//4
    intervals=[]
    for j in range(-4,4):
        covered={c for c in (-1,0,1) if j<=c<j+2}
        assert len(covered)<3
        assert not {-1,1}<=covered
        intervals.append(dict(j=j,covered_colonies=sorted(covered)))
    illustrative=symbolic_initialization_example(Q)
    pdf=next((ROOT/'papers').glob('A Reader*'))
    result=dict(Q=Q,U=U,error_lambda=24,error_separation_c=104,
        checker_sha256=digest(__file__),
        written_proof_sha256=digest(Path(__file__).with_name('GRAY_LITERAL_STAGE_ENVELOPE.md')),
        literal_module_sha256=digest(literal.__file__),
        generated_literal_maintenance_sha256=literal.source_sha256(),
        active_maintenance_sha256=digest(maintenance.__file__),
        netlist_library_sha256=digest(ROOT/'gacsca/netlist.py'),
        classifier_sha256=digest(gray_errors.__file__),
        gray_text_sha256=digest(ROOT/'papers_txt/gray_readers_guide.txt'),gray_pdf_sha256=digest(pdf),
        original_page_images_sha256={f'Gray_page{p}.png':digest(directory/f'Gray_page{p}.png')
            for p in (14,31,32,33,34,35,36,41)},
        exact_literal_native_phase_cofactors=Q,symbolic_common_clock_bits=literal.M,
        printed_Flag2_clause_preserved=True,corrected_Flag2_rule_used=False,
        canonical_geometry_and_zero_flags_before_pulse_proved_conditionally=True,
        native_premise='Correct native input fields, all Workspace flags0. Published computed-clock pulse forbids Workspace flags before96Q; error overwrites only three SimBit copies.',
        error_points=points,error_classification=classification,
        modified_raw_bits='Only each of the three holders\u2019 copy of logical primary y. All other raw bits unchanged.',
        Age_GF_or_Workspace_overwrite_used=False,spurious_Age0_Hold_commit_used=False,
        three_copy_majority_one_and_persistence_proved_under_S=True,
        arbitrary_programme_recursive_initialization_data_compatibility_proved=True,
        initialization_illustrative_frame=illustrative,
        actual_Gray_programme_and_final_layout_verified=False,
        actual_Q8192_programme_size_and_last_stage_runtime_verified=False,
        second_stage_start=second_start,second_active_end=second_active_end,
        third_stage_start=third_start,conditional_observation_time=T,
        conditional_difference_colonies=[-1,0,1],fixed_spatial_interval_checks=intervals,
        simultaneous_Mailbox_streams_required=False,
        full_raw_state_gather_G_and_record_retention_R_are_assumed=True,
        G_R_verified_against_Gray_transition_function=False,
        direct_raw_Mailbox_payload_witness_verified=False,
        conditional_pointwise_Proposition4_stage_axiom_incompatibility_proved=True,
        result_scope='If I,N,S,G,R hold, a legal three-copy real1 error forces Workspace/SimBit disagreements in three colonies during stage2 rest, incompatible with literal Proposition4. G/R and actual programme/layout realization remain unverified.',
        no_GR1_rule_ROM_or_transport_dependency=True,
        faithful_Gray_full_rule_counterexample_proved=False,
        corrected_Gray_decoded_boundary_counterexample_proved=False,
        iid_unreliability_proved=False,gacs_2001_refuted=False,
        global_reliability_established=False,active_rule_modified=False,measured_only=False,
        elapsed_seconds=time.monotonic()-started)
    (directory/'Gray_literal_stage_envelope_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('exact_literal_native_phase_cofactors',
        'error_classification','conditional_observation_time',
        'conditional_pointwise_Proposition4_stage_axiom_incompatibility_proved',
        'faithful_Gray_full_rule_counterexample_proved','elapsed_seconds')}))


if __name__=='__main__':main()
