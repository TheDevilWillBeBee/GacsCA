#!/usr/bin/env python3
"""Read-only reproduction/provenance check for the isolated GH0/GH1 milestone.

No programme existence, full Gray refinement or iid conclusion follows
from this component checkpoint. This validator never regenerates accepted
older artifacts or changes the active rule.
"""
from pathlib import Path
import ctypes,hashlib,json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
import gray_layout_hardwirer as gh
import gray_hardwired_gather as gather
import check_gray_layout_hardwirer as check


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def expected_C(comp,name):
    """Independent structural reproduction of the emitted source mapping."""
    lines=['#include <stdint.h>',f'void {name.lower()}_transition(const uint8_t *input,uint8_t *output) {{',
        f' uint8_t v[{comp.n_nodes}];',' v[0]=0; v[1]=1;']
    lines += [f' v[{2+i}]=input[{i}]&1;' for i in range(len(comp.inputs))]
    for i,(op,a,b) in enumerate(comp.gates,2+len(comp.inputs)):
        assert op in (0,1,2) and 0<=a<i and 0<=b<i
        lines.append(f' v[{i}]=v[{a}] '+('&','|','^')[op]+f' v[{b}];')
    for i,(tag,node) in enumerate(comp.outputs.items()):
        assert 0<=node<comp.n_nodes
        lines.append(f' output[{i}]=v[{node}]; /* {tag} */')
    lines+=['}',f'void {name.lower()}_projected(const uint8_t *raw,const uint16_t *gf,const uint8_t *beta,uint8_t *output) {{',
        f' uint8_t input[{len(comp.inputs)}];',f' for(unsigned i=0;i<{len(comp.inputs)};i++)input[i]=raw[i]&1;']
    bindings=[]
    for i,tag in enumerate(comp.inputs):
        if tag[0]=='x' and tag[2]=='programme':
            holder=tag[1];slot=gh.SLOTS[tag[3]]
            assert -5<=holder<=5 and -2<=slot<=2
            lines.append(f' input[{i}]=beta[((gf[{holder+5}]&8191)+({slot+gh.Q}))&8191]&1;')
            bindings.append(dict(input_index=i,actual_relative_holder=holder,copy_slot=slot))
    lines+=[f' {name.lower()}_transition(input,output);','}']
    return '\n'.join(lines)+'\n',bindings


def validate(directory=None):
    directory=directory or ROOT/'figs/gray_counterexamples';source=Path(__file__).parent
    row=json.loads((directory/'GH0_hardwirer_gather_certificate.json').read_text())
    for key,path in (
        ('kernel_sha256',gh.__file__),('gather_sha256',gather.__file__),
        ('checker_sha256',check.__file__),('proof_sha256',source/'GH0_HARDWIRER_GATHER.md'),
        ('base_GT0_sha256',check.gt.__file__),('native_h1_GMW2_sha256',check.native_h1.__file__),
        ('paper_text_sha256',ROOT/'papers_txt/gray_readers_guide.txt'),
        ('paper_pdf_sha256',next((ROOT/'papers').glob('A Reader*'))),
        ('classifier_sha256',ROOT/'gacsca/gray_errors.py'),
        ('netlist_library_sha256',ROOT/'gacsca/netlist.py'),
        ('term_library_sha256',ROOT/'Report/proofs/check_g17_schedule.py'),
        ('literal_native_sha256',check.native_h1.old.literal_maintenance.__file__),
        ('physical_trace_sha256',directory/'GH0_physical_courier_traces.npz'),
        ('raw_holder_witness_sha256',directory/'GH0_raw_holder_programme_witness.json'),
        ('raw_holder_witness_beta_sha256',directory/'GH0_raw_holder_witness_beta.bin')):
        assert row[key]==digest(path),(key,path)
    assert row['generated_literal_native_sha256']==check.native_h1.old.literal_maintenance.source_sha256()
    for name,value in row['receipt_dependencies_sha256'].items():assert value==digest(directory/name)
    failure=json.loads((directory/'GH0_initial_validator_serialization_failure.json').read_text())
    assert failure['retained_validator_sha256']==digest(directory/failure['retained_validator'])
    assert not failure['classifier_results_or_component_equations_differ']
    assert not failure['Gray_or_iid_failure_proved']
    assert (row['Q'],row['U'],row['lambda_original'],row['c_original'])==(8192,1048576,24,104)
    assert (row['courier_head_bits'],row['preliminary_projected_frame_bits'])==(18,367)
    for key in ('arbitrary_correct_beta_at_most_Q_is_premise','beta_used_for_checks_is_random_data_not_a_certified_own_programme',
        'no_64K_instruction_ROM_or_whole_rule_apply','projected_programme_source_uses_actual_raw_holder_GF',
        'native_h1_is_explicit_correction','only_Gather1_load_capture_schedule_changed',
        'recursive_initialization_for367_bit_prefix_frame_proved',
        'GH1_conditional_first56Q_native_hardwirer_gather_retention_composition_proved'):
        assert row[key]
    for key in ('final_complete_frame_certified','actual_own_beta_exists_proved','stage_endpoints_or_U_changed',
        'original_GT0_sources_or_receipts_modified','actual_complete_Gray_rule_or_Proposition4_counterexample_proved',
        'universal_programme_fit_update_runtime_or_full_period_proved','iid_failure_or_positive_noise_rate_proved',
        'active_rule_modified','global_reliability_established'):
        assert not row[key]
    assert row['bitwise_arbitrary_replacement_cofactors']==check.capacity()==102
    assert row['all_raw_GH1_data_route_and_rest_partition_certificate']==check.gather_routes()
    counts=[]
    for name,module in (('GH0',gh),('GH1',gather)):
        comp=module.compiled();emission=row['raw_holder_bindings'][name]
        graphfile=directory/(name+'_transitions.json');cfile=directory/(name+'_transitions.c')
        assert emission['netlist_sha256']==comp.digest
        assert (emission['inputs'],emission['outputs'],emission['gates'])==(len(comp.inputs),len(comp.outputs),len(comp.gates))
        assert emission['graph_sha256']==digest(graphfile) and emission['source_sha256']==digest(cfile)
        graph=json.loads(graphfile.read_text())
        assert graph['inputs']==json.loads(json.dumps(comp.inputs))
        assert graph['gates']==json.loads(json.dumps(comp.gates))
        assert graph['outputs']==json.loads(json.dumps(list(comp.outputs.items())))
        expected,bindings=expected_C(comp,name)
        assert cfile.read_text()==expected and bindings==emission['actual_programme_holder_bindings']
        assert max(abs(tag[1]) for tag in comp.inputs if tag[0]=='x')==5
        backend=row['backend_checks_measured_only'][name]
        assert backend['measured_only'] and backend['cases']==192
        assert backend['asset_sha256']==digest(directory/backend['asset'])
        assert backend['compiled_library_sha256']==digest(directory/(name+'_transitions.so'))
        with np.load(directory/backend['asset']) as a:
            raw=a['raw'];gf=a['gf'];beta=a['beta'];retained=a['net'];cvalues=a['compiled']
        assert raw.shape==(192,len(comp.inputs)) and gf.shape==(192,11)
        values=check.projected_inputs(comp,raw,gf,beta)
        result=comp.evaluate({tag:values[:,i].astype(bool) for i,tag in enumerate(comp.inputs)},bool)
        actual=np.column_stack([result[tag] for tag in comp.outputs]).astype(np.uint8)
        assert np.array_equal(actual,retained) and np.array_equal(cvalues,retained)
        ptr=ctypes.POINTER(ctypes.c_uint8);gptr=ctypes.POINTER(ctypes.c_uint16)
        function=getattr(ctypes.CDLL(str(directory/(name+'_transitions.so'))),name.lower()+'_projected')
        function.argtypes=[ptr,gptr,ptr,ptr];out=np.empty(len(comp.outputs),np.uint8)
        for i in range(192):
            assert check.scalar_output(comp,name,raw[i],gf[i],beta)==retained[i].tolist()
            function(raw[i].ctypes.data_as(ptr),gf[i].ctypes.data_as(gptr),beta.ctypes.data_as(ptr),out.ctypes.data_as(ptr))
            assert np.array_equal(out,retained[i])
        counts.append((name,len(comp.inputs),len(comp.gates),len(comp.outputs)))
    assert row['actual_first_clean_GH1_update_cofactors']==30
    assert row['actual_first_clean_GH1_output_assertions']==check.real1_first_update(gather.compiled())==9900
    with np.load(directory/'GH0_physical_courier_traces.npz') as a:
        beta=a['beta'].tolist();retained0=a['address0'];retained8191=a['address8191']
    count=0
    for address,retained in ((0,retained0),(8191,retained8191)):
        reproduced,cases=check.physical_run(address,beta)
        assert np.array_equal(retained,reproduced)
        assert retained.tolist()==[list(v) for v in gh.logical_run(address,beta)]
        count+=cases
    assert row['physical_all_five_holder_checks']==count==121730
    assert row['native_h1_complete_cell_finite_checks']==check.native_and_whole_cell_E0(beta)==10050
    layout,D,examples=check.initialization(beta)
    assert (len(layout),min(layout.values()),max(layout.values()),examples)==(367,3958,4324,15047)
    witness=json.loads((directory/'GH0_raw_holder_programme_witness.json').read_text())
    chosen=np.unpackbits(np.fromfile(directory/'GH0_raw_holder_witness_beta.bin',np.uint8),bitorder='little').tolist()
    expected=check.raw_holder_witness(beta)
    assert chosen==expected.pop('beta').tolist()
    assert witness==dict(expected,beta_asset='GH0_raw_holder_witness_beta.bin',
        beta_sha256=digest(directory/'GH0_raw_holder_witness_beta.bin'))
    assert witness['classification']['level0']==1 and witness['actual_E0_support']==[[0,3983]]
    assert [v['value'] for v in witness['physical_programme_accesses']]==[0,1,1,1,1]
    assert row['worst_courier_completion_age']==max(gh.completion_age(a) for a in range(gh.Q))==20366
    assert row['Gather1_load']==gather.GATHER_LOAD[0]==20367
    assert row['furthest_Gather1_capture']==max(gather.capture_age(0,b) for b in range(11))==61328<16*gh.Q
    assert len(row['gathering_coordinates'])==33
    for item in row['gathering_coordinates']:
        g=item['stage']-1;off=item['offset'];capture=gather.capture_age(g,check.gt.LANES.index(off))
        assert (item['load'],item['capture'],item['source_displacement'])==(gather.GATHER_LOAD[g],capture,off*gh.Q)
        assert capture==item['load']+(1+abs(off)*gh.Q if off else 0)
    classification=check.gray_errors.classify([(4009,1),(4010,1),(4011,1)],Q=gh.Q,U=gh.U,sep=104)
    assert json.loads(json.dumps(classification))==row['original_real1_classification'] and classification['level1']
    assert row['three_colony_witness_time']==56*gh.Q and row['three_colony_witness_sites']==[-4182,4010,12202]
    assert check.gt.LANES[6]==1 and check.gt.LANES[4]==-1
    assert -4182+gh.Q==12202-gh.Q==4010
    assert gather.capture_age(1,6)==gather.capture_age(1,4)==270338<48*gh.Q<56*gh.Q<64*gh.Q
    return dict(component_transition_dimensions=counts,physical_checks=count,whole_cell_finite_checks=10050,
        exact_GH1_routes=184320,exact_GH1_rest_routes=17280,
        all_status_limits_explicit=True,full_Gray_or_iid_theorem_proved=False,
        receipt_sha256=digest(directory/'GH0_hardwirer_gather_certificate.json'))


if __name__=='__main__':
    started=time.monotonic();result=validate();result['elapsed_seconds']=time.monotonic()-started
    print(json.dumps(result))
