#!/usr/bin/env python3
"""All-row finite certificate for a conditional shrinking pulse, not reliability."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import json
import subprocess
import sys
import time

import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    started=time.monotonic();out=ROOT/'figs/robustness'
    source=Path(__file__).with_name('certify_info_native_shrinking_pulse.c')
    executable=Path('/tmp/SP28_info_shrinking_pulse_certificate')
    subprocess.run(['cc','-O3','-std=c11','-Wall','-Wextra','-Werror',str(source),'-o',str(executable)],check=True)
    N=262144;Q=1024;frames={}

    def run(duration):
        log=out/f'SP28_info_shrinking_pulse_{duration}_certificate.jsonl'
        print(json.dumps(dict(phase='start',duration=duration)),flush=True)
        with log.open('w') as stream:
            proc=subprocess.run([str(executable),str(duration)],stdout=stream,stderr=subprocess.PIPE,text=True)
        assert proc.returncode==0,(duration,proc.returncode,proc.stderr)
        assert not proc.stderr
        rows=[json.loads(line) for line in log.read_text().splitlines()]
        summary=rows.pop()
        assert summary['certificate_complete'] and summary['rows_checked']==len(rows)==6145
        assert [r['row'] for r in rows]==list(range(6145))
        assert summary['GF_support_sites_checked']==6145*N
        assert summary['background_site_equalities']==sum(N-r['background_hi']+r['background_lo'] for r in rows)
        assert min(r['wrong_Addresses'] for r in rows)>=65
        assert all(r['Info1021_ones']==0 for r in rows)
        assert all(0<=b['Info509_ones']<=a['Info509_ones'] for a,b in zip(rows,rows[1:]))
        assert (rows[-1]['left'],rows[-1]['right_exclusive'],rows[-1]['wrong_Addresses'])==(124416,139264,14848)
        raw=Path(f'/tmp/SP28_info_shrinking_pulse_{duration}_final.bin').read_bytes()
        assert len(raw)==11*N
        planes=np.frombuffer(raw[:8*N],np.uint8).reshape(8,N).copy()
        code=np.frombuffer(raw[8*N:10*N],np.uint16).copy()
        info=np.frombuffer(raw[10*N:],np.uint8).copy()
        with np.load(out/'SP28_info_factor_states.npz') as prior:
            key=f'SP28_info_factor_{duration}_mode2_final_6144'
            for suffix,value in (('_planes',planes),('_code',code),('_info',info)):
                assert np.array_equal(value,prior[key+suffix])
        print(json.dumps(dict(phase='complete',duration=duration,summary=summary)),flush=True)
        return duration,log,rows,summary,planes,code,info

    with ThreadPoolExecutor(max_workers=2) as pool:
        runs=list(pool.map(run,(Q,2*Q)))
    summaries=[]
    for duration,log,rows,summary,planes,code,info in runs:
        for suffix,value in (('planes',planes),('code',code),('info',info)):
            frames[f'duration{duration}_{suffix}']=value
        summaries.append(dict(duration=duration,final=rows[-1],exhaustive_checks=summary,
                              intermediate_noninterval_rows=sum(r['holes_in_support_hull']>0 for r in rows),
                              maximum_holes_in_support_hull=max(r['holes_in_support_hull'] for r in rows),
                              log_sha256=digest(log)))
    asset=out/'SP28_info_shrinking_pulse_final_states.npz'
    np.savez_compressed(asset,**frames)
    dependencies=('SP28_info_native_factor_certificate.json','SP28_info_native_factor_cofactor_certificate.json')
    result=dict(
        scope='All-row finite certificate for two prepared actual-Info/native shrinking pulses; proof and lift separately scoped',
        Q=Q,U=475136,T_wf=278401,durations=[Q,2*Q],pulse_updates=6144,
        periodic_array_cells=N,initial_GF_interval=[130560,147456],
        initial_Flag1_intervals=[[130048,130560],[146944,147456]],
        initial_Info509_majority_one_only_inside_GF_interval=True,
        initial_Info1021_majority_zero=True,
        cases=summaries,all_rows_exact_integer_recurrence_checked=True,
        every_row_GF_hull_outward_growth_at_most3_checked=True,
        intermediate_GF_is_one_interval_claimed=False,
        every_row_background_equalities_checked=True,
        background_margin_formula='8*(r+1)+37',
        final_native_template_left_displacement=-6144,
        final_native_template_right_displacement=-8192,
        final_width_decrease=2048,
        initial_native_GF_width=16896,final_native_GF_width=14848,
        arbitrary_other_private_and_instruction_inputs_allowed_by_J164_factor=True,
        exact_infinite_line_lift_proof_supplied_separately=True,
        universal_other_width_or_phase_eroder_proved=False,
        intact_history_supplies_or_replenishes_initial_Info_pattern_proved=False,
        matching_changed_duration_own_programmes_proved=False,
        all_period_recovery_or_iid_threshold_proved=False,
        no_additional_rule_change=True,active_G17_modified=False,original_SP28_modified=False,
        global_reliability_established=False,
        checker_sha256=digest(__file__),C_wrapper_sha256=digest(source),
        included_transition_source_sha256=digest(source.with_name('native_address_info_factor.c')),
        C_executable_sha256=digest(executable),
        written_proof_sha256=digest(source.with_name('SP28_INFO_NATIVE_SHRINKING_PULSE.md')),
        final_state_asset_sha256=digest(asset),
        prior_state_asset_sha256=digest(out/'SP28_info_factor_states.npz'),
        retained_initial_sharp_failure_sha256=digest(out/'SP28_info_shrinking_initial_sharp_failure.json'),
        receipt_dependencies_sha256={name:digest(out/name) for name in dependencies},
        wall_seconds=time.monotonic()-started)
    (out/'SP28_info_native_shrinking_pulse_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(phase='certificate_written',wall_seconds=result['wall_seconds'],
                          global_reliability_established=False)),flush=True)


if __name__=='__main__':
    main()
