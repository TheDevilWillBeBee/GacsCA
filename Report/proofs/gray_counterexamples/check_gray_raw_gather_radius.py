#!/usr/bin/env python3
"""Exact radius obstruction for GT0 plus literal native/p41 components.

All-raw local transition scope only. No intact-history reachability or
unconditional Gray nonexistence is asserted. Future ports remain free.
"""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,const_word
from gacsca import maintenance
import literal_maintenance
import gray_raw_gather as component
import check_computed_simbit_radius as original


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    directory=ROOT/'figs/gray_counterexamples';p=component
    good,bad=original.configuration(False),original.configuration(True)
    assert [x for x in good if good[x]!=bad[x]]==[8]
    assert all(good[x]==bad[x] for x in range(-5,8))
    rows=[];native_cofactors=0
    for changed,cells in ((False,good),(True,bad)):
        native={x:original.exact_native(cells,x,literal_maintenance.build) for x in (0,3)}
        corrected={x:original.exact_native(cells,x,maintenance.build) for x in (0,3)}
        native_cofactors+=4
        assert native==corrected
        assert native[0]==dict(addr=0,age_now=original.TIME,age=original.TIME+1,f1=0,f2=0)
        assert native[3]==dict(addr=4 if changed else 3,age_now=original.TIME,
                              age=original.TIME+1,f1=int(changed),f2=0)
        n=Net()
        # Every SimBit copy is1; all other tracked data bits are0. This
        # coherent data extension is identical in the two raw states.
        data={j:{f:[int(f=='simbit')]*(5*w) for f,w in p.FIELDS}
              for j in range(-5,6)}
        writes={s:(n.input(('arbitrary_write_enable',s)),
                   n.input(('arbitrary_write_value',s))) for s in p.SLOTS}
        flag1=n.input(('arbitrary_early_flag1',));flag2=n.input(('arbitrary_early_flag2',))
        at3=native[3]
        wipe=int(at3['f1'] and at3['addr']!=cells[3]['addr'])
        result=p.build(n,data,const_word(at3['addr'],p.K),const_word(at3['age'],p.M),
                       at3['f1'],wipe,flag1,flag2,writes)
        simbit3=result['simbit',0,0]
        assert simbit3==int(not changed),(changed,simbit3)
        at0=native[0]
        native_wipe0=int(at0['f1'] and at0['addr']!=cells[0]['addr'])
        assert native_wipe0==0
        p41_gate=int(0<=at0['addr']<=4 and 96*p.Q<=at0['age']<98*p.Q and not at0['f1'])
        workspace_flag2=n.AND(p41_gate,simbit3)
        workspace_flag2=n.AND(workspace_flag2,n.NOT(native_wipe0))
        assert workspace_flag2==int(not changed)
        rows.append(dict(changed_address8=changed,raw_native_neighbourhood=cells,
                         computed_native=native,computed_primary_SimBit3=simbit3,
                         future_ports_symbolic=12,native_wipe3=wipe,
                         computed_Workspace_Flag2_at0=workspace_flag2))
    proof=Path(__file__).with_name('GT0_RADIUS_INTEGRATION.md')
    result=dict(name='GT0/literal-native/p41 all-raw locality obstruction',
        Q=p.Q,U=p.U,error_lambda=24,error_separation_c=104,raw_state_time=original.TIME,
        computed_age=original.TIME+1,sole_different_raw_site=8,
        radius7_neighbourhoods_identical=True,workspace_flag2_outputs=[1,0],
        exact_native_cofactors=native_cofactors,exact_GT0_primary_output_cofactors=2,
        all_future_programme_ports_symbolic=True,
        GT0_no_other_SimBit_write_premise_discharged=True,
        literal_component_set_required_radius_lower_bound=8,
        literal_radius5_completion_of_this_component_set_impossible=True,
        any_Gray_completion_nonexistence_proved=False,
        actual_self_programme_or_layout_refinement_proved=False,
        encoded_hierarchy_reachability_proved=False,decoded_memory_or_iid_failure_proved=False,
        independent_of_h1_Flag2_correction=True,global_reliability_established=False,
        active_rule_modified=False,measured_only=False,witness=rows,
        checker_sha256=digest(__file__),written_proof_sha256=digest(proof),
        GT0_primitive_sha256=digest(component.__file__),GT0_netlist_sha256=p.compiled().digest,
        earlier_conditional_checker_sha256=digest(original.__file__),
        literal_module_sha256=digest(literal_maintenance.__file__),
        generated_literal_maintenance_sha256=literal_maintenance.source_sha256(),
        active_maintenance_sha256=digest(ROOT/'gacsca/maintenance.py'),
        netlist_library_sha256=digest(ROOT/'gacsca/netlist.py'),
        gray_text_sha256=digest(ROOT/'papers_txt/gray_readers_guide.txt'),
        gray_pdf_sha256=digest(next((ROOT/'papers').glob('A Reader*'))),
        receipt_dependencies_sha256={name:digest(directory/name) for name in
          ('GT0_raw_gather_certificate.json','computed_simbit_radius_certificate.json')})
    (directory/'GT0_radius_integration_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('exact_native_cofactors',
        'exact_GT0_primary_output_cofactors','GT0_no_other_SimBit_write_premise_discharged',
        'literal_component_set_required_radius_lower_bound','any_Gray_completion_nonexistence_proved')}))


if __name__=='__main__':main()
