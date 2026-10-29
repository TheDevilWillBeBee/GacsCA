#!/usr/bin/env python3
"""All-row certificate/lift interfaces for SP29's first supplied pulse."""
from pathlib import Path
import hashlib,json,subprocess,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'figs/robustness'


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    started=time.monotonic();prior=ROOT/'Report/proofs/certify_info_native_shrinking_pulse.c'
    source=prior.read_text()
    replacements={
        'lo=initial_lo-margin,hi=initial_b+margin':'lo=124*Q-margin,hi=147*Q+margin',
        'ones509==8 && ones1021==0':'ones509==8 && ones1021==3',
        'duration=atoi(argv[1]);info_mode=2;':'duration=atoi(argv[1]);info_mode=3;',
        'if(duration!=Q && duration!=2*Q)return 2;':'if(duration!=2*Q)return 2;',
        '/tmp/SP28_info_shrinking_pulse_%d_final.bin':'/tmp/SP29_first_signal_pulse_%d_final.bin',
        '    certify_row(0);':'    const int extra[6]={124,125,126,144,145,146};\n    for(int j=0;j<6;j++)info[extra[j]*Q+1021]=1;\n    certify_row(0);'}
    for old,new in replacements.items():
        assert source.count(old)==1,old
        source=source.replace(old,new)
    generated=OUT/'SP29_first_pulse_generated.c';generated.write_text(source)
    executable=Path('/tmp/SP29_first_signal_pulse_certificate')
    subprocess.run(['cc','-O3','-std=c11','-Wall','-Wextra','-Werror','-I',str(ROOT/'Report/proofs'),
                    str(generated),'-o',str(executable)],check=True)
    log=OUT/'SP29_first_pulse_certificate.jsonl'
    with log.open('w') as stream:
        proc=subprocess.run([str(executable),'2048'],stdout=stream,stderr=subprocess.PIPE,text=True)
    assert proc.returncode==0,(proc.returncode,proc.stderr)
    assert not proc.stderr
    rows=[json.loads(line) for line in log.read_text().splitlines()];summary=rows.pop();N=262144
    assert summary['certificate_complete'] and summary['rows_checked']==len(rows)==6145
    assert [r['row'] for r in rows]==list(range(6145))
    assert summary['GF_support_sites_checked']==6145*N
    assert summary['background_site_equalities']==sum(N-r['background_hi']+r['background_lo'] for r in rows)
    for r in rows:
        assert r['background_lo']==124*1024-8*(r['row']+1)-37
        assert r['background_hi']==147*1024+8*(r['row']+1)+37
    for old,new in zip(rows,rows[1:]):
        assert new['left']>=old['left']-3 and new['right_exclusive']<=old['right_exclusive']+3
        assert 0<=new['Info509_ones']<=old['Info509_ones']
        assert 0<=new['Info1021_ones']<=old['Info1021_ones']
    raw=Path('/tmp/SP29_first_signal_pulse_2048_final.bin').read_bytes();assert len(raw)==11*N
    native=np.frombuffer(raw,dtype=np.uint8,count=8*N).reshape(8,N).copy()
    code=np.frombuffer(raw,dtype=np.uint16,count=N,offset=8*N).copy()
    info=np.frombuffer(raw,dtype=np.uint8,count=N,offset=10*N).copy()
    with np.load(OUT/'SP28_info_shrinking_pulse_final_states.npz') as old:
        assert np.array_equal(native,old['duration2048_planes'])
        assert np.array_equal(code,old['duration2048_code'])
        expected=old['duration2048_info'].copy()
        for j in (144,145,146):expected[j*1024+1021]=1
        assert np.array_equal(info,expected)
    with np.load(OUT/'SP29_prepared_history_signal_states.npz') as experiment:
        assert np.array_equal(native,experiment['final_native'])
        assert np.array_equal(code,experiment['final_code'])
        assert np.array_equal(info,experiment['final_Info'])
    asset=OUT/'SP29_first_pulse_final_states.npz';np.savez_compressed(asset,native=native,code=code,Info=info)
    first=json.loads((OUT/'SP29_first_signal_certificate.json').read_text())
    assert first['exact_first_signal_physical_history_proved']
    assert first['first_true_MF1021_one_colonies']==[124,125,126,144,145,146]
    dependencies=('SP29_first_signal_certificate.json','SP28_info_native_factor_certificate.json',
        'SP28_info_native_factor_cofactor_certificate.json','SP28_info_native_shrinking_pulse_certificate.json',
        'SP29_interface_identity.json','SP29_program_build.json','SP29_prepared_history_signal_pulse.json')
    result=dict(proposal='SP29',scope='J167 first supplied6144-update native/Info pulse on Z after the specified clock0 native error and complete underlying encoding; no later-period/general/iid theorem',
        proposed_rule_change=False,additional_rule_change=False,active_G17_modified=False,SP28_modified=False,
        checker_sha256=digest(__file__),inherited_C_wrapper_sha256=digest(prior),
        generated_C_wrapper_sha256=digest(generated),included_transition_source_sha256=digest(ROOT/'Report/proofs/native_address_info_factor.c'),
        C_executable_sha256=digest(executable),written_proof_sha256=digest(ROOT/'Report/proofs/SP29_FIRST_SIGNAL.md'),
        all_row_log_sha256=digest(log),final_state_asset_sha256=digest(asset),
        Q=1024,U=475136,T_wf=278401,force_duration=2048,pulse_updates=6144,periodic_array_cells=N,
        initial_native_GF_interval=[130560,147456],initial_projected_background_defect_interval=[126976,150528],
        background_margin_formula='8*(r+1)+37',final_protected_interval=[77779,199725],
        final_native_GF_interval=[124416,139264],initial_width=16896,final_width=14848,width_decrease=2048,
        final_MF509_one_count=8,final_MF1021_one_colonies=[144,145,146],
        final_summary=rows[-1],exhaustive_checks=summary,
        intermediate_noninterval_rows=sum(r['holes_in_support_hull']>0 for r in rows),
        maximum_holes_in_support_hull=max(r['holes_in_support_hull'] for r in rows),
        all_rows_exact_integer_recurrence_checked=True,every_row_background_equality_checked=True,
        outward_GF_support_growth_at_most3_checked=True,infinite_line_lift_proved=True,
        actual_first_period_supplied_signal_pulse_proved=True,
        final_native_and_code_equal_J165_D2Q=True,Info_differs_only_in_three_stated_true_primaries=True,
        all_initial_upper_Info_payloads_allowed=True,no_subsequent_errors_required=True,
        complete_all_field_data_restoration_proved=False,later_signal_replenishment_proved=False,
        general_width_phase_eroder_or_higher_map_or_iid_rate_established=False,global_reliability_established=False,
        receipt_dependencies_sha256={name:digest(OUT/name) for name in dependencies},seconds=time.monotonic()-started)
    (OUT/'SP29_first_pulse_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('exhaustive_checks','final_native_GF_interval','width_decrease','seconds','global_reliability_established')}),flush=True)


if __name__=='__main__':main()
