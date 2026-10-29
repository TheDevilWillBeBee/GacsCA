#!/usr/bin/env python3
"""Replay the prepared SP31 finite native pulse, not a damaged history.

The written factor/event proof supplies correspondence and compression.
This validates its specific6144-step exact finite execution and keeps
experimental transcription checks separate from actual-input premises.
"""
from pathlib import Path
import hashlib,json,subprocess,tempfile,time
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'figs/robustness';SOURCE=Path(__file__).with_name('sp31_native_events.c')


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def main():
    start=time.monotonic()
    interface=json.loads((OUT/'SP31_interface_certificate.json').read_text())
    assert interface['C_source_sha256']==sha(SOURCE)
    assert interface['unrestricted_native_GF_Age_F1_F2_private_header_instruction_independence']
    assert interface['selected_actual_full_net_factor_transcription_cases']==2048
    trace=OUT/'SP31_native_events_trace.jsonl'
    with tempfile.TemporaryDirectory(prefix='sp31_prepared_pulse_') as td:
        binary=Path(td)/'pulse'
        built=subprocess.run(['cc','-O3','-std=c11','-Wall','-Wextra','-Werror',str(SOURCE),'-o',str(binary)],
            check=True,capture_output=True,text=True)
        assert not built.stdout and not built.stderr
        compile_sha=sha(binary)
        replay=Path(td)/'trace.jsonl'
        with replay.open('wb') as stream:
            run=subprocess.run([str(binary),'6144'],stdout=stream,stderr=subprocess.PIPE,check=True)
        assert not run.stderr
        assert replay.read_bytes()==trace.read_bytes(),'prepared trajectory changed'
    records=[json.loads(line) for line in trace.read_text().splitlines()]
    rows,endpoint=records[:-1],records[-1]
    assert len(rows)==6145 and [r['row'] for r in rows]==list(range(6145))
    assert rows[0]['GF_sites']==15872 and rows[-1]['GF_sites']==11776
    assert rows[-1]['GF_holes']==0 and rows[-1]['Flag1_sites']==1024 and rows[-1]['WF1_sites']==0
    assert rows[-1]['GF_left']==135*1024-512 and rows[-1]['GF_right_exclusive']==146*1024
    assert endpoint['endpoint_segments']==[[134*1024,135*1024-512,2],
        [135*1024-512,146*1024-512,1],[146*1024-512,146*1024,3]]
    assert endpoint['endpoint_Info']==[127997,129021,130045,138749,139773,140797,
        141821,142845,143869,144893,145917]
    assert endpoint['exact_event_execution_complete'] and not endpoint['physical_input_premises_supplied_by_this_C']
    assert rows[-1]['events']==9894718
    # Intermediate holes are allowed. The theorem claims the endpoint
    # template and its width, not a solid wrong-GF interval on every row.
    hole_rows=sum(r['GF_holes']>0 for r in rows)
    max_holes=max(r['GF_holes'] for r in rows)
    assert all(a['events']<b['events'] for a,b in zip(rows,rows[1:]))
    assert all(a['Info_ones']>=b['Info_ones'] for a,b in zip(rows,rows[1:]))
    assert min(r['Info_ones'] for r in rows)==11
    max_segments=max(r['segments'] for r in rows)
    # For this run, no empty-state lookup is reached; every old native
    # state has wrong GF and Info is nonempty. Bound all cut writes before
    # C's final capacity check using the radius37 support induction.
    assert all(r['GF_sites']>0 and r['segments']>0 for r in rows)
    span=(145*1024+1022)-(124*1024+1021)+2*37*6144
    max_cuts=2+150*max_segments+34*(span//1024+8)
    assert max_segments<20000 and max_cuts<20000*180
    deps=('SP31_program_build.json','SP31_symbolic_schedule.json','SP31_interface_certificate.json',
        'SP31_encoded_certificate.json')
    kept=('SP31_native_events_trace.jsonl','SP31_native_events_compile.log','SP31_native_events_stderr.log',
        'SP31_native_events_initial_source.c.txt','SP31_native_events_initial_compile_failure.txt',
        'SP31_prepared_pulse_initial_checker.py.txt','SP31_prepared_pulse_initial_failure.log')
    result=dict(proposal='SP31',explicit_new_rule=True,active_G17_or_SP30_modified=False,
        checker_sha256=sha(__file__),proof_sha256=sha(Path(__file__).with_name('SP31_OWN_RULE.md')),
        C_source_sha256=sha(SOURCE),rebuilt_C_binary_sha256=compile_sha,
        candidate_sha256=interface['candidate_sha256'],netlist_sha256=interface['netlist_sha256'],
        receipt_dependencies_sha256={name:sha(OUT/name) for name in deps},
        retained_assets_sha256={name:sha(OUT/name) for name in kept},
        Q=1024,U=475136,T_wf=278401,updates=6144,trace_rows=6145,
        prepared_initial_template=[128,143],prepared_endpoint_template=[135,146],
        initial_wrong_GF_sites=15872,endpoint_wrong_GF_sites=11776,shrink_sites=4096,
        left_edge_translation=7168,right_edge_translation=3072,
        exact_event_intervals=9894718,maximum_constant_segments=max_segments,
        intermediate_GF_hole_rows=hole_rows,maximum_intermediate_GF_holes=max_holes,
        initial_false_all_rows_solid_GF_assertion_rejected_and_retained=True,
        checked_cut_capacity_upper_bound=max_cuts,retained_Info_one_primaries=11,
        exact_infinite_line_event_replay_and_capacity_for_this_run=True,
        factor_and_event_equation_proof_required=True,
        common_legal_clock_two_GF_phases_and_no_errors_or_Info_writes_required=True,
        native_Flag2_Workspace2_and_voted_Info3_515_zero_required=True,
        selected_full_net_transcription_cases_measured_only=2048,
        actual_intact_start_fault_commands_or_repeated_pulse_regeneration_proved=False,
        arbitrary_damaged_native_input_or_general_eroder_proved=False,
        iid_or_Gray_G17_refutation_or_minimum_sufficient_change_proved=False,
        global_reliability_established=False,elapsed_seconds=time.monotonic()-start)
    (OUT/'SP31_prepared_pulse_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ('updates','shrink_sites','exact_event_intervals',
        'maximum_constant_segments','actual_intact_start_fault_commands_or_repeated_pulse_regeneration_proved',
        'global_reliability_established','elapsed_seconds')}),flush=True)


if __name__=='__main__':main()
