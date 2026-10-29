#!/usr/bin/env python3
"""Discovery of J261's longer actual native/alias projection, not full SF.

Writes a separate analysis C and full trace once. The frozen J259 core
is unchanged; only this specified initial stripe and reporting differ.
The all-row physical/reset lift requires a companion written proof.
"""
from pathlib import Path
import hashlib,json,subprocess,tempfile,time
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
OUT=ROOT/'figs/robustness/unregistered_sp31_phaseTF_continuation'
OLD=ROOT/'Report/proofs/unregistered_sp31_upper_alias_pulse/sp31_prepared_upper_alias.c'
NEW=HERE/'sp31_actual_phaseTF_continuation.c'
TRACE=OUT/'native_trace01.jsonl';RECEIPT=OUT/'native_continuation_probe01.json'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def make_source():
    s=OLD.read_text();changes={
        '512;if(ticks<1||ticks>1024)':'6144;if(ticks<1||ticks>6144)',
        'append(&a,-17*Q,-16*Q-512,2);':'append(&a,-15*Q,-14*Q-512,2);',
        'append(&a,-16*Q-512,-512,1);':'append(&a,-14*Q-512,-512,1);',
        'prepared_native_trajectory_not_original_J225_history':'J261_actual_native_projection_input_requires_written_factor',
        'physical_lift_supplied_by_this_C':'whole_SF_or_reset_lift_supplied_by_this_C'}
    for old,new in changes.items():assert s.count(old)==1,old;s=s.replace(old,new)
    fragment=lambda x:x[x.index('typedef struct'):x.index('static void report')].rstrip()
    assert fragment(s)==fragment(OLD.read_text())
    return s
def compute():
    start=time.monotonic();source=make_source()
    assert NEW.read_text()==source
    with tempfile.TemporaryDirectory(prefix='sp31_phaseTF_cont_') as td:
        exe=Path(td)/'native'
        subprocess.run(['gcc','-std=c99','-O2','-Wall','-Wextra','-Werror',str(NEW),'-o',str(exe)],check=True)
        raw=subprocess.check_output([str(exe),'6144'])
    lines=[json.loads(s) for s in raw.decode().splitlines()];end=lines.pop()
    assert len(lines)==6145 and [r['relative_row'] for r in lines]==list(range(6145))
    assert all(r['upper_logical_Age']==278401+r['relative_row'] for r in lines)
    assert all(not r['wrongGF_right_sites'] for r in lines[:171])
    assert lines[171]['wrongGF_right_sites']==1 and lines[172]['native0']==3
    first_empty=next(r['relative_row'] for r in lines if not r['voted_Info_ones'])
    fixed=next(t for t in range(len(lines)) if all(r['native_segments']==lines[t]['native_segments'] and r['voted_Info_ones']==lines[t]['voted_Info_ones'] for r in lines[t:]))
    result=dict(passed=True,Q=1024,U=475136,TF=278401,steps=6144,full_projected_states=len(lines),
        final_native_segments=end['endpoint_segments'],final_voted_alias_ones=end['endpoint_Info'],
        first_source_vote_erasure=first_empty,first_final_native_projection_row=fixed,
        exact_constant_event_intervals=lines[-1]['events'],maximum_native_segments=max(r['segments'] for r in lines),
        old_frozen_C_sha256=sha(OLD),new_analysis_C_sha256=sha(NEW),probe_sha256=sha(__file__),
        native_alias_function_core_byte_identical_to_J259=True,initial_geometry_exactly_J261=True,
        final_source_raw_fiveholders_or_allrow_quiet_tail_or_reset_lift_proved_by_this_probe=False,
        arbitrary_original_real2_higher_error_or_iid_proved=False,
        rule_ROM_constants_or_G17_changed=False,global_reliability_established=False,
        trace_sha256=hashlib.sha256(raw).hexdigest(),seconds=time.monotonic()-start)
    return raw,result
def main():
    OUT.mkdir(parents=True,exist_ok=True)
    assert not NEW.exists() and not TRACE.exists() and not RECEIPT.exists()
    NEW.write_text(make_source());raw,result=compute();TRACE.write_bytes(raw)
    RECEIPT.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
if __name__=='__main__':main()
