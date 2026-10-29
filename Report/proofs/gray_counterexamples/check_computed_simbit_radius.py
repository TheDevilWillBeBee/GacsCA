#!/usr/bin/env python3
"""Exact conditional radius obstruction in Gray's computed-SimBit clause.

The published native equations, p33 mandatory simulation wipe and p41
computed-SimBit read are checked on two raw configurations differing only
in Address(8). The unstated full interpreter is not supplied: the premise
that SimBit otherwise stutters at the fourth-stage start is explicit.
No noisy-hierarchy or iid-memory counterexample is asserted.
"""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from gacsca import maintenance,gray_errors
from gacsca.netlist import Net,const_word
import literal_maintenance

Q=8192; U=128*Q; TIME=3*U//4


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def configuration(changed):
    cells={x:dict(addr=x%Q,age=TIME,f1=0,f2=0,wf1=0,wf2=0)
           for x in range(-5,9)}
    for x in (-2,-1,0):
        cells[x]['addr']=(x+1)%Q
    for x in (4,5):
        cells[x]['addr']=(x+2)%Q
    cells[8]['addr']=10 if changed else 8
    return cells


def exact_native(cells,x,builder):
    n=Net()
    neighbourhood={j:dict(addr=const_word(cells[x+j]['addr'],13),
        age=const_word(cells[x+j]['age'],20),
        **{f:cells[x+j][f] for f in ('f1','f2','wf1','wf2')}) for j in range(-5,6)}
    outputs=builder(n,neighbourhood,13,20)
    result={}
    for field,value in outputs.items():
        if isinstance(value,list):
            assert set(value)<=set((0,1)),(field,value)
            result[field]=sum(bit<<i for i,bit in enumerate(value))
        else:
            assert value in (0,1),(field,value)
            result[field]=value
    scalar=maintenance.maintenance_scalar({j:cells[x+j] for j in range(-5,6)},Q,U)
    assert scalar==result
    return result


def main():
    out=ROOT/'figs/gray_counterexamples'; rows=[]
    good,bad=configuration(False),configuration(True)
    assert all(good[x]==bad[x] for x in range(-5,6))
    assert [x for x in good if good[x]!=bad[x]]==[8]
    for changed,cells in ((False,good),(True,bad)):
        native={x:exact_native(cells,x,maintenance.build) for x in (0,3)}
        # This witness does not depend on the disputed erasure predicate:
        # every raw Flag2 is0, so literal and h1 equations coincide here.
        literal={x:exact_native(cells,x,literal_maintenance.build) for x in (0,3)}
        assert literal==native
        assert native[0]==dict(addr=0,age_now=TIME,age=TIME+1,f1=0,f2=0)
        expected_y=dict(addr=4 if changed else 3,age_now=TIME,age=TIME+1,
                        f1=int(changed),f2=0)
        assert native[3]==expected_y
        wipe=bool(native[3]['f1'] and native[3]['addr']!=cells[3]['addr'])
        assert wipe==changed
        # Exact stated refinement premise: all five copies of logical SimBit3
        # are1, and there is no other SimBit write on this fourth-stage tick.
        # ComputedAge=96Q+1 avoids a simultaneous stage-start reset at96Q.
        unwiped_simbit=1
        computed_simbit=0 if wipe else unwiped_simbit
        wf2=int(0<=native[0]['addr']<=4 and
            3*U//4<=native[0]['age']<3*U//4+2*Q and
            computed_simbit and not native[0]['f1'])
        rows.append(dict(changed_address8=changed,raw_neighbourhood=cells,
                         computed_native=native,simbit3_wiped=wipe,
                         computed_simbit3=computed_simbit,computed_workspace_flag2_at0=wf2))
    assert [r['computed_workspace_flag2_at0'] for r in rows]==[1,0]
    points=[(x,TIME) for x in range(-5,9)]
    classification=gray_errors.classify(points,Q=Q,U=U,sep=104)
    assert classification['level1'] and classification['level0']==0
    text=ROOT/'papers_txt/gray_readers_guide.txt'
    # Newline numbering matches nl -ba; control characters in extracted text
    # must not be treated as extra line breaks.
    lines=text.read_text().split('\n')
    references={}
    for title,needle in (
        ('declared_range5','N=[&5, &4, &3, &2, &1, 0, 1, 2, 3, 4, 5]'),
        ('mandatory_simulation_wipe','value of Address at x differs from the current value of Address at x.'),
        ('rest_and_five_stages','In the absence of noise, no'),
        ('computed_SimBit_WorkspaceFlag2','computed value of SimBit at the site x&A(x)+3 is 1,')):
        hits=[i+1 for i,line in enumerate(lines) if needle in line]
        assert len(hits)==1,(title,hits)
        references[title]=hits[0]
    result=dict(Q=Q,U=U,error_lambda=24,error_separation_c=104,
        raw_state_time=TIME,computed_age=TIME+1,comparison_site=0,referenced_simbit_site=3,
        sole_different_input_site=8,radius5_input_neighbourhood_equal=True,
        witness=rows,exact_native_cofactors=8,conditional_radius_lower_bound=8,
        proof_premise='At computedAge3U/4+1 the primary SimBit3 is its coherent fivefold majority unless the p33 mandatory native wipe applies; no other SimBit write occurs.',
        conditional_literal_composition_obstruction_proved=True,
        unconditional_gray_completion_nonexistence_proved=False,
        full_physical_programme_verified=False,encoded_history_reachability_proved=False,
        legal_real1_location_set_for_conditional_one_tick_lift=points,
        real1_classification=classification,independent_of_healthy_flag2_repair=True,
        iid_unreliability_proved=False,gacs_2001_refuted=False,global_reliability_established=False,
        checker_sha256=digest(__file__),active_maintenance_sha256=digest(ROOT/'gacsca/maintenance.py'),
        literal_module_sha256=digest(literal_maintenance.__file__),
        generated_literal_maintenance_sha256=literal_maintenance.source_sha256(),
        classifier_sha256=digest(ROOT/'gacsca/gray_errors.py'),
        gray_text_sha256=digest(text),primary_newline_references=references,
        gray_pdf_sha256=digest(next((ROOT/'papers').glob('A Reader*'))),
        inspected_page_images_sha256={f'Gray_page{p}.png':digest(out/f'Gray_page{p}.png') for p in (14,33,34,41)})
    (out/'computed_simbit_radius_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('exact_native_cofactors','conditional_radius_lower_bound',
        'conditional_literal_composition_obstruction_proved','unconditional_gray_completion_nonexistence_proved',
        'primary_newline_references')}))


if __name__=='__main__':
    main()
