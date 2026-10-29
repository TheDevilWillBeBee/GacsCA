#!/usr/bin/env python3
"""Exact finite native prefixes; stop rather than choose ambiguous GF."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import hashlib,json,subprocess,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import proposed_sparse_distant_epoch1024 as baseline
import proposed_sparse_short_epoch_duration as family


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    started=time.monotonic();out=ROOT/'figs/robustness';p=baseline.parameters();N=256*p.Q
    source=Path(__file__).with_name('native_address_short_epoch_enclosure.c')
    executable=Path('/tmp/SP28_short_epoch_enclosure_certificate')
    subprocess.run(['cc','-O3','-std=c11','-Wall','-Wextra','-Werror',str(source),'-o',str(executable)],check=True)
    def run(duration):
        proc=subprocess.run([str(executable),str(duration),'-1'],capture_output=True,text=True)
        log=out/f'SP28_short_epoch_{duration}_enclosure_certificate_run.jsonl';log.write_text(proc.stdout)
        rows=[json.loads(line) for line in proc.stdout.splitlines()]
        expected=(2064,124365) if duration==p.Q else (2368,123453)
        assert proc.returncode==6 and not proc.stderr,(duration,proc.returncode,proc.stderr)
        assert (rows[-1]['ambiguous_offset'],rows[-1]['site'])==expected
        assert rows[-1]['bounds']==[1,1,0,1]
        return duration,log,rows
    with ThreadPoolExecutor(max_workers=2) as pool:runs=list(pool.map(run,(p.Q,2*p.Q)))
    frames={};compared=0
    with np.load(out/'SP28_short_epoch_initial_enclosure_traces.npz') as old:
        for duration,log,rows in runs:
            for row in rows:
                stage='ambiguous' if 'ambiguous_offset' in row else row['stage']
                offset=row.get('ambiguous_offset',row.get('offset'))
                raw=Path(f'/tmp/SP28_short_epoch_enclosure_{duration}_mode-1_{stage}_{offset}.bin').read_bytes()
                assert len(raw)==12*N
                key=f'{duration}_{stage}_{offset}'
                planes=np.frombuffer(raw[:10*N],np.uint8).reshape(10,N).copy()
                code=np.frombuffer(raw[10*N:],np.uint16).copy()
                assert np.array_equal(planes,old[key+'_planes'])
                assert np.array_equal(code,old[key+'_code'])
                compared+=len(raw)
                frames[key+'_planes']=planes;frames[key+'_code']=code
    asset=out/'SP28_short_epoch_enclosure_certificate_states.npz';np.savez_compressed(asset,**frames)
    corners=json.loads((out/'SP28_short_epoch_local_corner_certificate.json').read_text())
    assert [r['outputs']['addr'] for r in corners['corner_rows']]==[461,973,573,61]
    legal=np.arange(p.U,dtype=np.int64);codes=np.array([p.age_code(int(t)) for t in legal])
    exact_clock_cases=0
    for duration in (p.Q,2*p.Q):
        assert np.array_equal((p.age_code(p.T_wf)<=codes)&(codes<p.age_code(p.T_wf+duration)),
            (p.T_wf<=legal)&(legal<p.T_wf+duration))
        exact_clock_cases+=len(legal)
    assert np.array_equal((p.age_code(p.T_wf)<=codes)&(codes<p.age_code(p.T_wf+1792)+1),
        (p.T_wf<=legal)&(legal<=p.T_wf+1792))
    assert np.array_equal((p.age_code(p.T_wf)<=codes)&(codes<p.age_code(p.T_wf+2*p.Q-1)+1),
        (p.T_wf<=legal)&(legal<p.T_wf+2*p.Q))
    exact_clock_cases+=2*len(legal)
    with np.load(out/'SP28_short_epoch_extreme_WF1_traces.npz') as extreme:
        controlled=[]
        for duration in (p.Q,2*p.Q):
            for mode,translation in ((0,-6*p.Q),(1,-8*p.Q)):
                initial=extreme[f'{duration}_mode{mode}_initial_0_planes']
                final=extreme[f'{duration}_mode{mode}_final_6144_planes']
                assert np.array_equal(final,np.roll(initial,translation,axis=1))
                assert not np.any(extreme[f'{duration}_mode{mode}_final_6144_code'])
                controlled.append(dict(duration=duration,WF1_mode=mode,translation=translation,
                    measured_only=True,full_private_intact_reachability_proved=False))
    dependencies=('SP28_short_epoch_local_corner_certificate.json','SP28_full_clock_island_certificate.json',
        'SP28_full_Address_island_certificate.json','SP28_auxiliary_lifetime_certificate.json',
        'SP28_short_epoch_initial_inline_cofactor_parse_failure.json')
    result=dict(name='Short-duration SP28 native prefixes and exact enclosure gap',
        Q=p.Q,U=p.U,T_wf=p.T_wf,durations=[p.Q,2*p.Q],radius=37,
        prefix_offsets=[2064,2368],terminal_sites=[124365,123453],
        native_GF_prefix_translation_per_row=-3,
        actual_native_header_one_step_projection_proved=True,
        arbitrary_private_signal_native_enclosure_proved=True,
        exhaustive_periodic_prefix_rows=[2065,2369],periodic_array_cells=N,
        GF_sharp_interval_asserted_on_every_prefix_row=True,
        arbitrary_private_native_prefix_on_infinite_line_proved=True,
        discrepancy_influence_margin=48*p.Q,
        terminal_allowed_raw_corners_distinct_full_native_outputs_proved=True,
        exact_full_native_free_private_terminal_cofactors=4,
        terminal_native_GF_outputs=[461,973,573,61],
        terminal_corner_dynamic_reachability_proved=False,
        common_clock_comparator_legal_cases=exact_clock_cases,
        retained_snapshot_bytes_compared_with_prior_exploration=compared,
        conditional_Info_509_1021_zero_implies_WF1_zero_during_pulse_proved=True,
        Info509_layout_field='h2',Info509_layout_bit=77,
        controlled_WF1_outcomes_measured_only=controlled,
        changed_duration_own_programmes_or_self_simulation_proved=False,
        short_duration_all_period_orbit_or_finite_eroder_proved=False,
        iid_failure_proved=False,global_reliability_established=False,
        proposed_rule_changes_explicit=True,active_G17_modified=False,original_SP28_modified=False,
        written_proof_sha256=digest(Path(__file__).with_name('SP28_SHORT_EPOCH_ENCLOSURE_GAP.md')),
        checker_sha256=digest(__file__),C_source_sha256=digest(source),C_executable_sha256=digest(executable),
        family_source_sha256=digest(family.__file__),baseline_source_sha256=digest(baseline.__file__),
        epoch_helper_source_sha256=digest(ROOT/'Report/proofs/proposed_sparse_epoch_duration_family.py'),
        source_generated_transition_sha256=hashlib.sha256(baseline.generated_source(p).encode()).hexdigest(),
        receipt_dependencies_sha256={name:digest(out/name) for name in dependencies},
        prior_trace_asset_sha256=digest(out/'SP28_short_epoch_initial_enclosure_traces.npz'),
        extreme_WF1_asset_sha256=digest(out/'SP28_short_epoch_extreme_WF1_traces.npz'),
        extreme_WF1_projection_source_sha256=digest(Path(__file__).with_name('native_address_short_epoch_bounds.c')),
        extreme_WF1_receipts_sha256={f'SP28_short_epoch_{d}_mode{mode}_exploratory.json':
            digest(out/f'SP28_short_epoch_{d}_mode{mode}_exploratory.json')
            for d in (p.Q,2*p.Q) for mode in (0,1)},
        certificate_state_asset_sha256=digest(asset),
        certificate_run_logs_sha256={log.name:digest(log) for d,log,rows in runs},
        seconds=time.monotonic()-started,
        scope='Finite arbitrary-private native prefix plus exact terminal enclosure ambiguity; no post-stop trajectory/higher/iid theorem')
    (out/'SP28_short_epoch_enclosure_gap_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('prefix_offsets','actual_native_header_one_step_projection_proved',
        'arbitrary_private_native_prefix_on_infinite_line_proved','global_reliability_established','seconds')}),flush=True)


if __name__=='__main__':main()
