#!/usr/bin/env python3
"""Universal GT0 route/rest/storage certificate and emitted transitions.

The native/control and future programme interfaces are explicit. This is
not an own-programme fit certificate or a full self-simulating CA. The
emitted C's compiler comparison is separately labeled measured evidence.
"""
from pathlib import Path
from itertools import combinations,product
from functools import lru_cache
import ctypes,hashlib,json,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'Report/proofs'))
import numpy as np
from gacsca.netlist import Net,const_word,at_least
from gacsca import gray_errors
from check_g17_schedule import Terms
import gray_raw_gather as implementation


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def emit(comp,directory):
    rows=list(comp.outputs.items())
    description=dict(name='GT0 raw gather/storage transducer, not a complete CA',
        Q=implementation.Q,U=implementation.U,data_bits=implementation.DATA_BITS,
        native_and_programme_integration_ports_unimplemented=True,
        inputs=comp.inputs,gates=comp.gates,outputs=rows,netlist_sha256=comp.digest)
    graph=directory/'GT0_transitions.json'
    graph.write_text(json.dumps(description,separators=(',',':'))+'\n')
    code=['#include <stdint.h>',f'void gt0_transition(const uint8_t *input, uint8_t *output) {{',
          f'  uint8_t v[{comp.n_nodes}];','  v[0]=0; v[1]=1;']
    code += [f'  v[{2+i}] = input[{i}] & 1;' for i in range(len(comp.inputs))]
    symbols=('&','|','^')
    for i,(op,a,b) in enumerate(comp.gates,2+len(comp.inputs)):
        assert 0<=a<i and 0<=b<i and op in (0,1,2)
        code.append(f'  v[{i}] = v[{a}] {symbols[op]} v[{b}];')
    for i,(name,node) in enumerate(rows):
        assert 0<=node<comp.n_nodes
        code.append(f'  output[{i}] = v[{node}]; /* {name} */')
    code.append('}')
    c_source=directory/'GT0_transitions.c';c_source.write_text('\n'.join(code)+'\n')
    return graph,c_source


def initial_frame():
    p=implementation; layout=p.preliminary_layout()
    tags=list(layout); reverse={a:tag for tag,a in layout.items()}
    assert len(tags)==p.FRAME_BITS==277
    assert not set(reverse)&{0,3,p.Q-3}
    assert all(4<=layout['simbit',b]<=p.Q-4 for b in range(5))
    @lru_cache(maxsize=None)
    def D(x):
        i,a=divmod(int(x),p.Q)
        if a==0:return ('arbitrary_correct_programme_beta',i%p.Q)
        tag=reverse.get(a)
        if tag is None:return 0
        f,b=tag
        if f=='addr':return ((i%p.Q)>>b)&1
        if f=='simbit':
            nxt=i+p.SLOTS[b]
            assert abs(nxt)<abs(x)
            return D(nxt)
        return 0
    def raw(x,f,b):
        if f=='addr':return ((x%p.Q)>>b)&1
        if f=='simbit':return D(x+p.SLOTS[b])
        return 0
    examples=sorted(set(range(-8,9))|{s*(p.Q**e+d) for s in (-1,1)
        for e in (1,2,8,32) for d in (0,1,p.Q-1)})
    for x in examples:
        assert D(x*p.Q)==('arbitrary_correct_programme_beta',x%p.Q)
        for f,b in tags:assert D(x*p.Q+layout[f,b])==raw(x,f,b)
    y=layout['history1',0]
    assert y==4010 and D(y)==0
    assert all(D(x)==0 for x in range(y-14,y+15))
    assert D(0)!=0  # No zero-programme/all-zero-colony premise.
    return layout,y,len(examples)*len(tags)


def main():
    started=time.monotonic(); directory=ROOT/'figs/gray_counterexamples';p=implementation
    clocks=p.clock_boundaries(); phases=p.address_boundaries()
    equations=rest_equations=0
    for age in clocks[:-1]:
        for phase in phases[:-1]:
            n=Net(); variables={(f,x,b):n.input(('logical',f,x,b)) for f,w in p.FIELDS
                for x in range(-7,8) for b in range(w)}
            cells={j:{f:[variables[f,j+s,b] for s in p.SLOTS for b in range(w)]
                for f,w in p.FIELDS} for j in range(-5,6)}
            f1=n.input(('free_native_flag1',));wipe=n.input(('free_native_wipe',))
            flag1=n.input(('early_flag1_port',));flag2=n.input(('early_flag2_port',))
            writes={s:(n.input(('write_enable',s)),n.input(('write_value',s))) for s in p.SLOTS}
            actual=p.build(n,cells,const_word(phase,p.K),const_word(age,p.M),f1,wipe,flag1,flag2,writes)
            def expression(command):
                if command[0]=='zero':return 0
                if command[0]=='flag1_port':return flag1
                if command[0]=='flag2_port':return flag2
                if command[0]=='write_port':
                    _,slot,current=command
                    return n.MUX(*writes[slot],expression(current))
                if command[0]=='majority3':
                    a,b,c=[expression(q) for q in command[1:]]
                    return n.OR(n.AND(a,b),n.AND(c,n.OR(a,b)))
                return variables[command]
            rest=any(active_end<=age<end for _,active_end,end in p.STAGES)
            for f,w in p.FIELDS:
                for slot in p.SLOTS:
                    for b in range(w):
                        command=p.scalar_plan(age,phase,slot,f,b)
                        expected=expression(command)
                        if f in ('mailR','mailL'):expected=n.AND(expected,n.NOT(f1))
                        expected=n.AND(expected,n.NOT(wipe))
                        assert actual[f,slot,b]==expected,(age,phase,f,slot,b,command)
                        equations+=1
                        if rest:
                            assert command==(f,slot,b),(age,phase,f,slot,b,command)
                            rest_equations+=1
    majority_cases=0
    for i,j in combinations(range(5),2):
        for correct,a,b in product((0,1),repeat=3):
            values=[correct]*5;values[i]=a;values[j]=b
            assert at_least(Net(),values,3)==correct;majority_cases+=1
    assert at_least(Net(),[0,1,1,1,0],3)==1
    coordinates=[]
    for stage in range(3):
        for lane,off in enumerate(p.LANES):
            age=p.capture_age(stage,lane);S,active_end,_=p.STAGES[stage]
            assert S<age<active_end
            if off==0:assert age==S+1
            else:assert age-(S+1)-1==abs(off)*p.Q
            coordinates.append(dict(stage=stage+1,offset=off,load_age=S+1,
                capture_age=age,source_displacement=off*p.Q,same_within_colony_address=True))
    assert max(p.capture_age(1,l) for l in range(11))<48*p.Q
    assert max(p.capture_age(2,l) for l in range(11))<80*p.Q-1
    comp=p.compiled();graph,c_source=emit(comp,directory)
    assert max(abs(name[1]) for name in comp.inputs if name[0]=='x')==5
    # Actual emitted source/compiler comparison on all control partitions,
    # with arbitrary damaged data/ports, is measured separately from proof.
    library=directory/'GT0_transitions.so'
    subprocess.run(['gcc','-std=c11','-O2','-fPIC','-shared',str(c_source),'-o',str(library)],check=True)
    lib=ctypes.CDLL(str(library));fun=lib.gt0_transition
    ptr=ctypes.POINTER(ctypes.c_uint8);fun.argtypes=[ptr,ptr];fun.restype=None
    count=(len(clocks)-1)*(len(phases)-1)
    rng=np.random.default_rng(0x47415448)
    inputs=rng.integers(0,2,size=(count,len(comp.inputs)),dtype=np.uint8)
    for row,(age,phase) in enumerate(product(clocks[:-1],phases[:-1])):
        for name,value,width in (('computed_age',age,p.M),('computed_address',phase,p.K)):
            for bit in range(width):inputs[row,comp.inputs.index((name,bit))]=(value>>bit)&1
    reference=comp.evaluate({name:inputs[:,i].astype(bool) for i,name in enumerate(comp.inputs)},bool)
    outputs=np.empty((count,len(comp.outputs)),dtype=np.uint8)
    for i in range(count):fun(inputs[i].ctypes.data_as(ptr),outputs[i].ctypes.data_as(ptr))
    expected=np.column_stack([reference[name] for name in comp.outputs]).astype(np.uint8)
    assert np.array_equal(outputs,expected)
    vectors=directory/'GT0_C_comparison_inputs_outputs.npz'
    np.savez_compressed(vectors,inputs=inputs,outputs=outputs)
    layout,y,initial_checks=initial_frame()
    layout_path=directory/'GT0_preliminary_frame_layout.json'
    layout_path.write_text(json.dumps(dict(frame_schema=p.FRAME_SCHEMA,frame_bits=p.FRAME_BITS,
        preliminary_only=True,adding_interpreter_changes_frame_and_layout=True,
        rows=[[f,b,a] for (f,b),a in layout.items()]),indent=2)+'\n')
    points=[(y+d,1) for d in (-1,0,1)]
    classification=gray_errors.classify(points,Q=p.Q,U=p.U,sep=104)
    assert classification['level1'] and classification['level0']==0
    # Full emitted-net first clean update in the actual recursive frame's
    # local cone. At time1 all live local data inputs here are0: SimBit
    # primaries are within y±14, first-stage mail/own-history snapshot these
    # zeros, and every other record/private field is still initially0.
    # The error changes just the designated three stored SimBit copies.
    terms=Terms();injection_assertions=0
    for site in range(y-7,y+8):
        for noisy in (False,True):
            nodes=[0,1]
            for name in comp.inputs:
                if name[0]=='x':
                    _,off,field,bit=name;w=dict(p.FIELDS)[field]
                    copy,lane=divmod(bit,w);holder=site+off
                    logical=holder+p.SLOTS[copy]
                    assert y-14<=logical<=y+14
                    value=int(noisy and field=='simbit' and logical==y and holder in (y-1,y,y+1))
                elif name[0]=='computed_address':value=((site%p.Q)>>name[1])&1
                elif name[0]=='computed_age':value=(2>>name[1])&1
                elif name[0] in ('computed_flag1','native_wipe'):value=0
                else:value=terms.var(('future_port',)+name)
                nodes.append(value)
            for op,a,b in comp.gates:nodes.append(terms.op(op,nodes[a],nodes[b]))
            for name,node in comp.outputs.items():
                _,field,slot,bit=name
                expected=int(noisy and field=='simbit' and site+slot==y)
                assert nodes[node]==expected,(site,noisy,name)
                injection_assertions+=1
    assert injection_assertions==7200
    T=56*p.Q
    witnesses=[dict(site=y-p.Q,colony=-1,field='history2',lane=6,source=y),
               dict(site=y,colony=0,field='simbit',source=y),
               dict(site=y+p.Q,colony=1,field='history2',lane=4,source=y)]
    for item in (witnesses[0],witnesses[2]):
        off=p.LANES[item['lane']]
        assert item['site']+off*p.Q==y
        assert p.capture_age(1,item['lane'])<48*p.Q<T<64*p.Q
    dependencies=('Gray_literal_stage_envelope_certificate.json',)
    result=dict(name='GT0 concrete raw-gather/storage component',Q=p.Q,U=p.U,
        error_lambda=24,error_separation_c=104,input_radius=5,
        data_fields=p.FIELDS,data_bits_per_holder=p.DATA_BITS,preliminary_frame_bits=p.FRAME_BITS,
        primitive_sha256=digest(p.__file__),checker_sha256=digest(__file__),netlist_sha256=comp.digest,
        netlist_library_sha256=digest(ROOT/'gacsca/netlist.py'),
        written_proof_sha256=digest(Path(__file__).with_name('GT0_RAW_GATHER.md')),
        emitted_transition_graph_sha256=digest(graph),emitted_C_source_sha256=digest(c_source),
        emitted_C_library_sha256=digest(library),C_comparison_asset_sha256=digest(vectors),
        preliminary_layout_sha256=digest(layout_path),
        classifier_sha256=digest(gray_errors.__file__),
        term_library_sha256=digest(ROOT/'Report/proofs/check_g17_schedule.py'),
        gray_text_sha256=digest(ROOT/'papers_txt/gray_readers_guide.txt'),
        receipt_dependencies_sha256={name:digest(directory/name) for name in dependencies},
        clock_partition_boundaries=clocks,address_partition_boundaries=phases,
        symbolic_logical_bits_per_class=15*sum(w for _,w in p.FIELDS),
        exact_route_equalities=equations,exact_rest_equalities=rest_equations,
        exact_two_fault_majority_cofactors=majority_cases,gather_coordinates=coordinates,
        all_clock_address_route_equations_proved=True,
        raw_full_state_gather_G_proved_for_component_conditionally=True,
        local_receiver_record_storage_and_older_history_independence_proved=True,
        record_retention_R_proved_for_component_conditionally=True,
        all_data_fields_coherent_rest_stuttering_proved_conditionally=True,
        final_programme_ports_unused_before112Q_proved=True,
        flag_result_ports_unused_before80Q_minus1_proved=True,
        preliminary_all_level_recursive_data_initialization_proved=True,
        symbolic_arbitrary_ProgramBits_allowed=True,initial_sample_encoding_equalities=initial_checks,
        actual_self_programme_beta_compiled=False,
        exact_three_copy_physical_error_set=points,error_classification=classification,
        exact_first_clean_update_compiled_net_cofactors=30,
        exact_first_clean_update_output_assertions=injection_assertions,
        all_future_programme_ports_symbolic_in_injection_cofactors=True,
        only_SimBit_copies_overwritten=True,
        conditional_three_colony_early_prefix_witness=witnesses,conditional_witness_time=T,
        native_controls_need_matching_literal_rule_and_pulse_zero_before96Q=True,
        GT0_closed_first56Q_prefix_composition_proved_under_that_native_condition=True,
        C_source_gate_mapping_structurally_verified=True,
        C_compiler_output_comparison_cases=count,C_compiler_output_comparison_measured_only=True,
        universal_binary_backend_equivalence_proved=False,
        no_GR1_rule_ROM_front_or_transport_dependency=True,
        chosen_same_address_gather_layout_and_clock_schedule_explicit=True,
        actual_Gray_full_rule_G_R_refinement_proved=False,
        integrated_interpreter_ProgramBit_or_computed_SimBit_rule_proved=False,
        full_noiseless_or_noisy_period_composition_proved=False,
        faster_work_period_variant_used=False,full_faithful_Gray_counterexample_proved=False,
        decoded_memory_or_iid_failure_proved=False,global_reliability_established=False,
        active_rule_modified=False,mathematical_route_proof_measured_only=False,
        elapsed_seconds=time.monotonic()-started)
    (directory/'GT0_raw_gather_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('data_bits_per_holder','preliminary_frame_bits',
        'exact_route_equalities','exact_rest_equalities','C_compiler_output_comparison_cases',
        'raw_full_state_gather_G_proved_for_component_conditionally',
        'actual_Gray_full_rule_G_R_refinement_proved','elapsed_seconds')}))


if __name__=='__main__':main()
