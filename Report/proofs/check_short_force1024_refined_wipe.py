#!/usr/bin/env python3
"""Refute the old wipe factor; certify its corrected three pulse histories.

This changes a proof model, not any cellular-automaton rule or programme.
Frozen earlier sources and receipts are retained for provenance.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca.netlist import Compiled
from check_g17_schedule import Terms
import proposed_sparse_short_force1024 as proposed

OUT = ROOT / 'figs/robustness'


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def counterexample(p):
    net, source = proposed.full_net(p)
    comp = Compiled(net)
    generated = proposed.generated_source(p)
    assert 'native_refined = distant_refinement(' in generated
    assert "cell = {j: dict(value, **native_refined[j])" in generated
    assert "wipe = n.AND(f1_new, n.NOT(w_eq(n, addr_now, c['addr'])))" in generated
    cases = []
    for x in range(507, 512):
        terms = Terms()
        nodes = [0, 1]
        for name in comp.inputs:
            if name[0] != 'x':
                value = terms.var(name)
            else:
                _, off, field, bit = name
                y = x + off
                values = dict(addr=(y + 512 * int(y in (508, 509, 510))) % p.Q,
                    age=p.age_code(p.T_wf), f1=1, f2=0, wf1=0, wf2=0,
                    packet_valid=0, packet_tag=0, packet_count=0,
                    service_valid=0, service_position=0, service_count=0,
                    backward_pressure=0)
                if field == 'info':
                    value = int(y + bit - 2 == 509)
                elif field in values:
                    value = (values[field] >> bit) & 1
                else:
                    value = terms.var(name)
            nodes.append(value)
        for op, a, b in comp.gates:
            nodes.append(terms.op(op, nodes[a], nodes[b]))
        checked = 0
        for name, node in comp.outputs.items():
            if len(name) != 3 or name[0] != 'y':
                continue
            _, field, bit = name
            if field == 'addr':
                expected = (x >> bit) & 1
            elif field == 'f1':
                expected = 1
            elif field == 'info' and x + bit - 2 == 509:
                expected = 1
            else:
                continue
            assert nodes[node] == expected, (x, name, nodes[node], expected)
            checked += 1
        assert checked == p.k + 2
        cases.append(dict(reader=x, new_GF=x, new_Flag1=1,
            tracked_Info_copy_output=1, constant_output_equalities=checked,
            other_private_and_instruction_inputs_free=True))
    actual = int(sum(c['tracked_Info_copy_output'] for c in cases) >= 3)
    old = int(sum(x not in (508, 509, 510) for x in range(507, 512)) >= 3)
    assert (actual, old) == (1, 0)
    return dict(clock=p.T_wf, raw_GF_shifted_sites=[508,509,510],
        raw_Flag1_everywhere=1, tracked_Info_primary=509,
        actual_new_Info_majority=actual, old_factor_new_Info_majority=old,
        full_net_constant_cofactors=cases, proposed_netlist_sha256=comp.digest,
        full_generated_source_sha256=hashlib.sha256(generated.encode()).hexdigest(),
        native_maintenance_source_sha256=hashlib.sha256(source.encode()).hexdigest())


def generate_sources():
    original = ROOT / 'Report/proofs/native_address_info_factor.c'
    text = original.read_text()
    old = 'keeps+=!(next[F1][x] && next[LABEL][x]!=state[LABEL][x]);'
    new = '''int corrected_keep=!(next[F1][x] && next[LABEL][x]!=refined[x]);
            int old_keep=!(next[F1][x] && next[LABEL][x]!=state[LABEL][x]);
            keeps+=corrected_keep;oldkeeps+=old_keep;
            if(info[y] && corrected_keep!=old_keep)refined_wipe_copy_mask_disagreements++;'''
    assert text.count(old) == 1
    text = text.replace(old, new)
    text = text.replace('int keeps=0;', 'int keeps=0,oldkeeps=0;')
    old = 'newinfo[y]=info[y] && keeps>=3;'
    assert text.count(old) == 1
    text = text.replace(old, '''newinfo[y]=info[y] && keeps>=3;
        if(info[y] && (oldkeeps>=3)!=(keeps>=3))refined_wipe_active_majority_disagreements++;''')
    text = text.replace('static int duration,info_mode;', '''static int duration,info_mode;
static uint64_t refined_wipe_copy_mask_disagreements,refined_wipe_active_majority_disagreements;''')
    factor = OUT / 'SP29_refined_wipe_factor_generated.c'
    factor.write_text(text)
    wrapper_original = ROOT / 'Report/proofs/certify_info_native_shrinking_pulse.c'
    text = wrapper_original.read_text()
    changes = {
        '#include "native_address_info_factor.c"': '#include "SP29_refined_wipe_factor_generated.c"',
        'static int previous_a,previous_b;': 'static int previous_a,previous_b,with_extras;',
        'lo=initial_lo-margin,hi=initial_b+margin': 'lo=124*Q-margin,hi=147*Q+margin',
        'ones509==8 && ones1021==0': 'ones509==8 && ones1021==3*with_extras',
        'if(argc!=2)return 2;': 'if(argc!=3)return 2;',
        'duration=atoi(argv[1]);info_mode=2;': 'duration=atoi(argv[1]);with_extras=atoi(argv[2]);info_mode=2+with_extras;',
        'if(duration!=Q && duration!=2*Q)return 2;':
            'if((duration!=Q && duration!=2*Q) || with_extras<0 || with_extras>1 || (with_extras && duration!=2*Q))return 2;',
        '    certify_row(0);': '''    if(with_extras){const int extra[6]={124,125,126,144,145,146};
        for(int j=0;j<6;j++)info[extra[j]*Q+1021]=1;}
    certify_row(0);''',
        '"/tmp/SP28_info_shrinking_pulse_%d_final.bin",duration':
            '"/tmp/SP29_refined_wipe_%d_mode%d_final.bin",duration,with_extras',
        '"\\\"background_site_equalities\\\":%llu,\\\"GF_support_sites_checked\\\":%llu}\\n",':
            '"\\\"background_site_equalities\\\":%llu,\\\"GF_support_sites_checked\\\":%llu,"\n'
            '           "\\\"refined_wipe_copy_mask_disagreements\\\":%llu,\\\"refined_wipe_active_majority_disagreements\\\":%llu}\\n",',
        '(unsigned long long)tested_GF_support_sites);':
            '(unsigned long long)tested_GF_support_sites,\n'
            '           (unsigned long long)refined_wipe_copy_mask_disagreements,\n'
            '           (unsigned long long)refined_wipe_active_majority_disagreements);'
    }
    for old, new in changes.items():
        assert text.count(old) == 1, old
        text = text.replace(old, new)
    wrapper = OUT / 'SP29_refined_wipe_pulse_generated.c'
    wrapper.write_text(text)
    return original, factor, wrapper_original, wrapper


def main():
    start = time.monotonic()
    p = proposed.parameters()
    witness = counterexample(p)
    print(json.dumps(dict(phase='old_general_factor_refuted', witness=witness)), flush=True)
    original, factor, wrapper_original, wrapper = generate_sources()
    executable = Path('/tmp/SP29_refined_wipe_pulse_certificate')
    subprocess.run(['cc','-O3','-std=c11','-Wall','-Wextra','-Werror',
                    str(wrapper),'-o',str(executable)], check=True)
    N = 262144

    def run(case):
        duration, extras = case
        print(json.dumps(dict(phase='pulse_start',duration=duration,extras=extras)), flush=True)
        log = OUT / f'SP29_refined_wipe_{duration}_mode{extras}.jsonl'
        with log.open('w') as stream:
            proc = subprocess.run([str(executable),str(duration),str(extras)],
                                  stdout=stream,stderr=subprocess.PIPE,text=True)
        assert proc.returncode == 0 and not proc.stderr, (case, proc.returncode, proc.stderr)
        rows = [json.loads(line) for line in log.read_text().splitlines()]
        summary = rows.pop()
        assert summary['certificate_complete'] and summary['rows_checked'] == len(rows) == 6145
        assert [row['row'] for row in rows] == list(range(6145))
        assert summary['GF_support_sites_checked'] == 6145*N
        assert summary['background_site_equalities'] == sum(N-r['background_hi']+r['background_lo'] for r in rows)
        assert summary['refined_wipe_active_majority_disagreements'] == 0, summary
        for r in rows:
            assert r['background_lo'] == 124*p.Q - 8*(r['row']+1)-37
            assert r['background_hi'] == 147*p.Q + 8*(r['row']+1)+37
        prior_name = 'SP29_first_pulse_certificate.jsonl' if extras else f'SP28_info_shrinking_pulse_{duration}_certificate.jsonl'
        prior_rows = [json.loads(line) for line in (OUT/prior_name).read_text().splitlines()][:-1]
        assert len(prior_rows) == len(rows)
        for new, old in zip(rows, prior_rows):
            for key in old:
                if key not in ('background_lo','background_hi'):
                    assert new[key] == old[key], (case, new['row'], key, new[key], old[key])
        raw = Path(f'/tmp/SP29_refined_wipe_{duration}_mode{extras}_final.bin').read_bytes()
        assert len(raw) == 11*N
        native = np.frombuffer(raw,dtype=np.uint8,count=8*N).reshape(8,N).copy()
        code = np.frombuffer(raw,dtype=np.uint16,count=N,offset=8*N).copy()
        info = np.frombuffer(raw,dtype=np.uint8,count=N,offset=10*N).copy()
        prior_asset = OUT / ('SP29_first_pulse_final_states.npz' if extras else 'SP28_info_shrinking_pulse_final_states.npz')
        with np.load(prior_asset) as old:
            names = ('native','code','Info') if extras else tuple(f'duration{duration}_{k}' for k in ('planes','code','info'))
            for name, value in zip(names,(native,code,info)):
                assert np.array_equal(value,old[name]), (case,name)
        print(json.dumps(dict(phase='pulse_complete',duration=duration,extras=extras,summary=summary)), flush=True)
        return case,rows,summary,log,(native,code,info),prior_name,prior_asset

    with ThreadPoolExecutor(max_workers=3) as pool:
        runs = list(pool.map(run, ((1024,0),(2048,0),(2048,1))))
    frames = {}
    cases = []
    historical_assets = {}
    for (duration,extras),rows,summary,log,arrays,prior_name,prior_asset in runs:
        for suffix,value in zip(('native','code','Info'),arrays):
            frames[f'duration{duration}_mode{extras}_{suffix}'] = value
        historical_assets[prior_name] = digest(OUT/prior_name)
        historical_assets[prior_asset.name] = digest(prior_asset)
        cases.append(dict(duration=duration,initial_true_phase_extras=bool(extras),
            final=rows[-1],exhaustive_checks=summary,
            intermediate_noninterval_rows=sum(r['holes_in_support_hull']>0 for r in rows),
            maximum_holes_in_support_hull=max(r['holes_in_support_hull'] for r in rows),
            corrected_full_history_equals_old_projected_history_by_induction=True,
            all_row_summaries_equal_historical_receipt=True,final_arrays_equal_historical_asset=True,
            log_name=log.name,log_sha256=digest(log)))
    asset = OUT / 'SP29_refined_wipe_final_states.npz'
    np.savez_compressed(asset,**frames)
    dependencies = ('SP28_info_native_factor_certificate.json','SP28_info_native_factor_cofactor_certificate.json',
        'SP28_info_native_shrinking_pulse_certificate.json','SP29_first_signal_certificate.json',
        'SP29_first_pulse_certificate.json','SP29_next_ghost_signal_certificate.json','SP29_interface_identity.json')
    result = dict(scope='J170 analysis-model correction and exact three prepared pulse bridges; no new reliability theorem',
        Q=p.Q,U=p.U,T_wf=p.T_wf,radius=37,
        old_unrefined_GF_general_factor_refuted=True,counterexample=witness,
        corrected_refined_old_GF_factor_proved=True,
        corrected_keep_formula='NOT(F1_new AND (L_new != joint_refined_old_L))',
        carry_wipe_majority_identity_assignments=1024,
        native_header_and_WF1_old_majority_source_equations_unchanged=True,
        cases=cases,all_three_corrected_pulse_histories_certified=True,
        all_three_active_Info_majority_disagreement_counts_zero=True,
        historical_J165_and_J167_particular_pulse_conclusions_restored=True,
        historical_J169_first_endpoint_premise_restored=True,
        historical_general_factor_claim_reinstated=False,
        historical_uniform_track_trajectories_revalidated=False,
        first_signal_source_theorem_and_next_signal_timing_proof_unchanged=True,
        infinite_line_pulse_lifts_proved_with_corrected_factor=True,
        full_other_private_simulation_confinement_proved=False,
        general_eroder_higher_error_map_or_positive_iid_noise_rate_proved=False,
        global_reliability_established=False,analysis_model_change=True,
        rule_programme_or_constant_change=False,active_G17_modified=False,
        proposed_candidate_sha256=proposed.load_artifact().digest(),
        checker_sha256=digest(__file__),written_proof_sha256=digest(Path(__file__).with_name('SP29_REFINED_WIPE_FACTOR.md')),
        frozen_old_C_factor_sha256=digest(original),generated_corrected_C_factor_sha256=digest(factor),
        frozen_old_C_wrapper_sha256=digest(wrapper_original),generated_C_wrapper_sha256=digest(wrapper),
        C_executable_sha256=digest(executable),final_state_asset_sha256=digest(asset),
        source_helpers_sha256={str(path.relative_to(ROOT)):digest(path) for path in
            (Path(proposed.__file__),ROOT/'gacsca/rule_g.py',ROOT/'gacsca/netlist.py',ROOT/'Report/proofs/check_g17_schedule.py')},
        receipt_dependencies_sha256={name:digest(OUT/name) for name in dependencies},
        historical_assets_sha256=historical_assets,seconds=time.monotonic()-start)
    receipt = OUT / 'SP29_refined_wipe_certificate.json'
    receipt.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(phase='certificate_written',cases=cases,seconds=result['seconds'],
                         global_reliability_established=False)),flush=True)


if __name__ == '__main__':
    main()
