#!/usr/bin/env python3
"""GI0 quantified stipulated-interface and confined-evaluator obstruction."""
from pathlib import Path
from itertools import product
import hashlib,json,random,sys,time
SOURCE=Path(__file__).resolve().parent
sys.path.insert(0,str(SOURCE))
import gray_final_source_gi0 as interface
ROOT=interface.ROOT;REGISTERED=interface.REGISTERED
from gacsca.netlist import Compiled
import gray_early_native_flags as early
import gray_raw_gather as gather
import gray_moving_word_kernel as head

Q=8192;U=1048576;TIME=96*Q
DIRECTORY=ROOT/'figs/gray_counterexamples/unregistered_gi0'


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def state(shift=0):
    return {x:dict(addr=(x+shift)%Q,age=TIME,f1=0,f2=0,wf1=0,wf2=0,
        simbit=(1,)*5,nextbit=(0,)*5,courierL=(0,)*5,courierR=(0,)*5)
        for x in interface.INTERVAL}


def witnesses():
    positive=[];negative=[]
    for changed in (False,True):
        cells=state()
        for x in (6,7):cells[x]['age']=U-1
        if changed:cells[8]['age']=U-1
        for x in range(-2,3):cells[x]['f2']=1
        positive.append(cells)
        cells=state(Q-1)
        for x in (-6,-5):cells[x]['age']=U-1
        if changed:cells[-7]['age']=U-1
        for x in (-4,-3,-2):cells[x]['wf1']=1
        negative.append(cells)
    result=[]
    for name,inputs,site,field,target in (
        ('positive8_no_wipe_Age_wrap',positive,8,'wf2',3),
        ('negative7_no_wipe_Age_wrap',negative,-7,'wf1',-2)):
        assert [x for x in interface.INTERVAL if inputs[0][x]!=inputs[1][x]]==[site]
        assert all(inputs[0][x]==inputs[1][x] for x in range(-5,6))
        rows=[]
        for cells in inputs:
            printed=interface.project(cells)
            corrected=interface.project(cells,h1=True)
            assert printed==corrected
            reader=interface.native_at(cells,0);source=interface.native_at(cells,target)
            assert reader['age']==TIME+1
            assert reader['addr']==cells[0]['addr']
            assert source['addr']==cells[target]['addr']
            assert reader['f1']==(1 if field=='wf1' else 0)
            assert not (source['f1'] and source['addr']!=cells[target]['addr'])
            rows.append(dict(raw_projection=cells,computed_reader_native=reader,
                computed_source_native=source,computed_final_primary_SimBit=
                    interface.computed_simbit_copy(cells,target,0),computed_projection=printed))
        assert [row['computed_projection'][field] for row in rows]==[1,0]
        assert [row['computed_source_native']['age'] for row in rows]==[TIME+1,0]
        result.append(dict(name=name,sole_changed_old_site=site,source_displacement=target,
            changed_output_field=field,reader_native_equal=rows[0]['computed_reader_native']==rows[1]['computed_reader_native'],
            no_source_or_reader_wipe=True,rows=rows))
    return result


def raw_cell(cells,source,x,seed):
    """Full finite GE0 cell with the projected bits and arbitrary hidden fields."""
    rng=random.Random(seed+19*x);projection=cells[source+x]
    data=[]
    for field,width in gather.FIELDS:
        bits=projection[field] if field in interface.DATA else tuple(rng.randrange(2) for _ in range(5*width))
        data.append(tuple(bits))
    return early.Cell(**{field:projection[field] for field,width in interface.NATIVE},
        data=tuple(data),heads=tuple(rng.getrandbits(early.HEAD_BITS) for _ in range(5)),
        early_out=tuple(rng.randrange(2) for _ in range(5)),
        courierL=projection['courierL'],courierR=projection['courierR'])


def hidden_field_and_port_independence(beta,inputs):
    checks=0;sig=hashlib.sha256()
    for witness in inputs:
        target=witness['source_displacement']
        for row in witness['rows']:
            cells={int(x):v for x,v in row['raw_projection'].items()}
            for pattern in product((0,1),repeat=7):
                seed=sum(bit<<i for i,bit in enumerate(pattern))
                native_cells={j:raw_cell(cells,target,j,seed) for j in range(-5,6)}
                ports={s:(1,pattern[i+2]) for i,s in enumerate(gather.SLOTS)}
                out=early.local_transition(native_cells,beta,pattern[:2],ports)
                expected=interface.computed_simbit_copy(cells,target,0)
                assert out.data[0][0]==expected
                sig.update(json.dumps([witness['name'],seed,expected]).encode());checks+=1
    return dict(actual_GE0_full_hidden_fields_and_all128_Workspace_fifth_port_patterns=checks,
        trace_sha256=sig.hexdigest(),universal_port_independence_argument='GT0 SimBit reads OLD fields and no write_port branch')


def sample_states():
    rng=random.Random(0x474930)
    rows=[]
    for clock in (0,1,TIME-1,TIME,98*Q-1,98*Q,U-1):
        for address in (0,3,4,5,Q-5,Q-3,Q-1):
            cells=state(address)
            for x in interface.INTERVAL:
                cells[x]['age']=clock
                for field in ('f1','f2','wf1','wf2'):cells[x][field]=rng.randrange(2)
                for field in interface.DATA:cells[x][field]=tuple(rng.randrange(2) for _ in range(5))
            rows.append(cells)
    for _ in range(79):
        cells=state()
        for x in interface.INTERVAL:
            cells[x]['addr']=rng.randrange(Q);cells[x]['age']=rng.randrange(U)
            for field in ('f1','f2','wf1','wf2'):cells[x][field]=rng.randrange(2)
            for field in interface.DATA:cells[x][field]=tuple(rng.randrange(2) for _ in range(5))
        rows.append(cells)
    return rows


def symbolic_projection(inputs):
    result=[];samples=sample_states()
    for h1 in (False,True):
        net=interface.netlist(h1);compiled=Compiled(net)
        assert len(net.input_names)==16*57 and len(net.outputs)==42
        assert {name[1] for name in net.input_names}==set(range(-7,9))
        live=set(net.live_nodes())
        used=sorted({name[1] for name,node in net.input_node.items() if node in live})
        assert min(used)==-7 and max(used)==8
        signature=hashlib.sha256();count=0
        rows=samples+[row['raw_projection'] for item in inputs for row in item['rows']]
        for raw in rows:
            cells={int(x):v for x,v in raw.items()}
            actual=interface.decoded(compiled.evaluate_scalar(interface.values(cells)))
            expected=interface.project(cells,h1)
            assert actual==expected
            signature.update(json.dumps(expected,sort_keys=True).encode());count+=1
        result.append(dict(h1_explicit_correction=h1,net_sha256=net.digest(),
            raw_input_bits=len(net.input_names),live_gates=net.gate_count(),output_bits=len(net.outputs),
            syntactically_used_old_site_range=[min(used),max(used)],scalar_graph_replays=count,
            scalar_graph_trace_sha256=signature.hexdigest()))
    return result


def lane_and_deadline_audit():
    # Exact projection of a 17-record tape to native11, not a new interpreter.
    centre=8;checks=0
    for mem17 in range(1<<17):
        mem11=(mem17>>3)&2047
        assert ((mem17>>centre)&1)==((mem11>>5)&1)
        for side in (0,1):
            for i in range(5):
                oldlane=5+(i+1)*(1 if side else -1)
                newlane=centre+(i+1)*(1 if side else -1)
                assert ((mem11>>oldlane)&1)==((mem17>>newlane)&1)
        checks+=1
    assert len(head.OP_NAMES)==28 and max(head.OP.values())==27
    assert 5*4*6==120 and early.FRAME_BITS+120==2582
    assert early.FRAME_BITS+100==2562
    native_ready=64*Q+2+5*Q;whole_ready=64*Q+2+8*Q
    assert (native_ready,whole_ready)==(565250,589826)
    assert whole_ready-early.RESET==24575
    # If a pass requires all17 later records at birth, the existing reset
    # cannot justify that prepared execution. This does not forbid the
    # native11 early pass, which does not use the additional six records.
    earliest_new_reset=whole_ready+1;earliest_new_birth=whole_ready+2
    ticks_before75Q=early.SEED-earliest_new_birth-1
    assert ticks_before75Q==24571 and 34396>ticks_before75Q
    return dict(symmetric_lane_offsets=[-8,8],asymmetric_lane_offsets=[-7,8],
        symmetric_history_and_voted_extra_raw_bits=120,asymmetric_extra_raw_bits=100,
        symmetric_declared_frame_bits_without_new_evaluator_fields=2582,
        asymmetric_declared_frame_bits_without_new_evaluator_fields=2562,
        centred_symmetric_frame_interval=[2805,5387],centred_asymmetric_frame_interval=[2815,5377],
        latest_native11_third_capture=native_ready,latest_whole17_third_capture=whole_ready,
        existing_early_reset=early.RESET,existing_early_birth=early.BIRTH,
        full17_ready_after_existing_reset_ticks=whole_ready-early.RESET,
        earliest_ready_then_reset_birth=[earliest_new_reset,earliest_new_birth],
        actual_native_code_ticks=34396,available_ticks_before_existing75Q_seed=ticks_before75Q,
        native_code_would_miss75Q_seed_after_waiting_for_all17=True,
        native11_early_pass_still_uses_only_inner11_and_is_not_refuted=True,
        native11_lane_projection_identities=checks,
        unused_five_bit_opcode_values=[28,29,30,31],
        proposed_FULLCOL_opcode_and_side_bit_not_implemented=True,
        largest_gather_capture_fits16Q_active_interval=8*Q+2<16*Q,
        whole_fifth_eval_beta_layout_runtime_and_shorter_U_proved=False)


def blindness(inputs):
    positive=next(row for row in inputs if row['sole_changed_old_site']==8)
    a,b=(row['raw_projection'] for row in positive['rows'])
    # These are upper raw states: every simulated raw bit in inner eleven
    # records agrees, not just the reader's native word.
    assert all(a[x]==b[x] for x in range(-5,6))
    assert interface.project(a)['wf2']!=interface.project(b)['wf2']
    return dict(equal_inner11_upper_raw_records=True,
        distinct_required_upper_Workspace2_outputs=[1,0],
        confined_HEAD_correct_control_same_beta_LOAD11_complete_input_blindness_obstruction=True,
        quantifies_all_beta_lengths_and_execution_times_under_stated_read_interface=True,
        unrestricted_head_travel_auxiliary_external_inputs_or_other_Gray_evaluators_refuted=False,
        full_own_beta_for_this_stipulated_radius8_rule_with_unchanged_LOAD11_possible=False)


def calculate():
    inputs=witnesses();beta,_,_=early.native_programme()
    return dict(exact_opposite_endpoint_witnesses=inputs,
        full_hidden_fields_and_future_port_checks=hidden_field_and_port_independence(beta,inputs),
        total_all_raw_interface_nets=symbolic_projection(inputs),
        current_confined_evaluator_obstruction=blindness(inputs),
        actual_lane_and_deadline_audit=lane_and_deadline_audit(),
        fifth_programme_or_auxiliary_choices_cannot_remove_this_stipulated_radius5_obstruction=True,
        smallest_symmetric_radius_for_this_projection=8,
        smallest_contiguous_interval_hull_for_this_projection=[-7,8],
        all_Gray_completions_or_Gacs_nonexistence_proved=False,
        whole_self_rule_own_beta_iid_or_shorter_U_proved=False)


def receipt():
    sources=('literal_maintenance.py','gray_raw_gather.py','gray_early_native_flags.py',
        'gray_moving_word_kernel.py','GRAY_COMPUTED_SIMBIT_ORDER.md','GT0_RADIUS_INTEGRATION.md')
    manifest=DIRECTORY/'GI0_initial_boolean_identity_failure_manifest.json'
    retained=json.loads(manifest.read_text())
    for name,sha in retained['assets_sha256'].items():assert digest(DIRECTORY/name)==sha
    return dict(name='GI0 quantified stipulated whole-interface obstruction',Q=Q,U=U,
        lambda_original=24,c_original=104,checker_sha256=digest(__file__),
        emitted_interface_source_sha256=digest(SOURCE/'gray_final_source_gi0.py'),
        proof_sha256=digest(SOURCE/'GI0_TOTAL_SOURCE_INTERFACE.md'),
        source_dependencies_sha256={name:digest(REGISTERED/name) for name in sources},
        repository_netlist_source_sha256=digest(ROOT/'gacsca/netlist.py'),
        repository_corrected_native_source_sha256=digest(ROOT/'gacsca/maintenance.py'),
        primary_Gray_text_sha256=digest(ROOT/'papers_txt/gray_readers_guide.txt'),
        frozen_order_receipt_sha256=digest(ROOT/'figs/gray_counterexamples/Gray_computed_simbit_order_certificate.json'),
        retained_initial_boolean_identity_failure_manifest_sha256=digest(manifest),
        retained_initial_boolean_identity_failure_assets_sha256=retained['assets_sha256'],
        remaining_whole_rule_fields_are_not_emitted_and_remain_unproved=True,
        no_intact_history_error_counterexample_or_iid_inference=True,
        registered_main_or_old_artifacts_changed=False,results=calculate())


if __name__=='__main__':
    started=time.monotonic();r=receipt();r['elapsed_seconds']=time.monotonic()-started
    path=DIRECTORY/'GI0_total_source_interface_certificate.json'
    path.write_text(json.dumps(r,sort_keys=True,indent=2)+'\n')
    print(json.dumps(dict(receipt=str(path),receipt_sha256=digest(path),
        minimal_projection_interval=[-7,8],stipulated_radius5_completion_impossible=True,
        whole_Gray_or_iid_refutation=False,elapsed_seconds=r['elapsed_seconds'])))
