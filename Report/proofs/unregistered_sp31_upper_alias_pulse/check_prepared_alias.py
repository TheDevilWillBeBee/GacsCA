#!/usr/bin/env python3
"""Freeze once; replay the prepared native trajectory without changing assets."""
from pathlib import Path
import argparse,hashlib,json,subprocess,sys,tempfile,time
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
OUT=ROOT/'figs/robustness/unregistered_sp31_upper_alias_pulse'
CERT=OUT/'prepared_alias_certificate.json';PROOF=HERE/'SP31_PREPARED_UPPER_ALIAS_OBSTRUCTION.md'
PARENT=ROOT/'figs/robustness/unregistered_sp31_right_halfline/halfline_renewal_certificate.json'
sys.path.insert(0,str(HERE));import probe_prepared_alias as probe
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def compare_core():
    old=(ROOT/'Report/proofs/sp31_native_events.c').read_text()
    new=(HERE/'sp31_prepared_upper_alias.c').read_text()
    initial=(HERE/'sp31_prepared_upper_alias_initial_source.c').read_text()
    # The report separator added one blank line, outside the function core.
    fragment=lambda x:x[x.index('typedef struct'):x.index('static void report')].rstrip()
    assert fragment(old)==fragment(new)==fragment(initial)
    assert initial[initial.index('int main'):] ==new[new.index('int main'):]
    return dict(native_Info_core_byte_identical_to_J225=True,initial_source_only_trace_instrumentation_differs=True,
                core_sha256=hashlib.sha256(fragment(new).encode()).hexdigest())
def replay_trace():
    with tempfile.TemporaryDirectory(prefix='sp31_prepared_alias_') as tmp:
        exe=Path(tmp)/'native';subprocess.run(['gcc','-std=c99','-O2','-Wall','-Wextra','-Werror',str(HERE/'sp31_prepared_upper_alias.c'),'-o',str(exe)],check=True)
        raw=subprocess.check_output([str(exe),'512'])
    assert raw==(OUT/'native_trace02.jsonl').read_bytes()
    rows=[json.loads(x) for x in raw.decode().splitlines()];end=rows.pop()
    old=[json.loads(x) for x in (OUT/'native_trace01.jsonl').read_text().splitlines()]
    assert len(rows)==513 and len(old)==514
    assert [{k:v for k,v in x.items() if k not in ('native_segments','voted_Info_ones')} for x in rows]+[end]==old
    assert [r['relative_row'] for r in rows]==list(range(513))
    assert all(r['upper_logical_Age']==278401+r['relative_row'] for r in rows)
    assert all(not r['wrongGF_right_sites'] for r in rows[:171])
    assert rows[171]['wrongGF_right_sites']==1 and probe.at(rows[171],2)&1
    assert all(not (probe.at(r,0)&1) for r in rows[:172]) and rows[172]['native0']==3
    assert rows[172]['wrongGF_right_sites']==rows[172]['wrongGF_right_exclusive']==4
    assert rows[-1]['events']==508646 and rows[-1]['wrongGF_right_sites']==1024
    assert end['endpoint_segments']==[[-17408,-16896,2],[-16896,-512,1],[-512,173,3],[173,512,1],[512,1024,3]]
    assert all(r['voted_Info_ones']==[1021] for r in rows[:-1]) and not rows[-1]['voted_Info_ones']
    assert end['prepared_native_trajectory_not_original_J225_history'] and not end['physical_lift_supplied_by_this_C']
    # Retained holder recurrence and every group's voted value, independently
    # of the C's Info tracker. All other groups stay0 by the written factor.
    votes=0
    for t,r in enumerate(rows):
        holders=[probe.info_holder(rows,t,1021-slot,slot) for slot in range(-2,3)]
        assert int(sum(holders)>=3)==int(1021 in r['voted_Info_ones'])
        votes+=1
    return dict(full_native_states=513,exact_constant_event_intervals=508646,
                actual_source_holder_vote_reconstructions=votes,first_right_wrong_GF_upper_step=171,
                first_cell0_wrong_GF_upper_step=172,first_source_vote_erasure_upper_step=512,
                physical_first_right_GF_bank_boundary=171*475136,physical_cell0_GF_bank_boundary=172*475136,
                final_right_wrong_GF_interval=[0,1024])
def assets():
    parent=json.loads(PARENT.read_text());pinned=dict(parent['assets_sha256'])
    for rel,h in pinned.items():assert sha(ROOT/rel)==h,rel
    pinned[str(PARENT.relative_to(ROOT))]=sha(PARENT)
    paths={*HERE.iterdir(),*OUT.iterdir(),ROOT/'Report/proofs/sp31_native_events.c',ROOT/'Report/proofs/SP31_FIRST_PULSE.md',ROOT/'Report/proofs/check_native_command1024_first_pulse.py'}
    for module in list(sys.modules.values()):
        f=getattr(module,'__file__',None)
        if f:
            p=Path(f).resolve()
            if p.suffix=='.py' and p.is_relative_to(ROOT):paths.add(p)
    for p in paths:
        if p.is_file() and p.name not in (CERT.name,'issue_run.log','readonly_run.log'):
            rel=str(p.relative_to(ROOT));h=sha(p);assert rel not in pinned or pinned[rel]==h,rel;pinned[rel]=h
    return dict(sorted(pinned.items()))
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--issue',action='store_true');args=ap.parse_args();start=time.monotonic()
    if args.issue:assert not CERT.exists(),'Immutable certificate exists; use read-only replay.'
    else:
        frozen=json.loads(CERT.read_text())
        for rel,h in frozen['assets_sha256'].items():assert sha(ROOT/rel)==h,rel
    core=compare_core();trajectory=replay_trace()
    old=json.loads((OUT/'prepared_alias_cofactors01.json').read_text());new=probe.compute()
    assert {k:v for k,v in old.items() if k!='seconds'}=={k:v for k,v in new.items() if k!='seconds'}
    assert len(old['selected_actual_native_and_Info_holder_cofactors'])==190
    assert not old['universal_infinite_line_prepared_or_physical_lift_supplied_by_this_probe']
    assert old['actual_Info_holder_erasures_reconstructed_from_old_vote_and_refined_self_keep']
    encoding=json.loads((ROOT/'figs/robustness/SP31_encoded_certificate.json').read_text())
    assert encoding['complete_start_noiseless_and_all_period_pure_E0_simulation_proved']
    cert=dict(passed=True,Q=1024,U=475136,TF=278401,radius=37,proof_sha256=sha(PROOF),checker_sha256=sha(__file__),
        candidate_sha256=old['candidate_sha256'],netlist_sha256=old['netlist_sha256'],algebra=core,trajectory=trajectory,
        prepared_complete_E_C_satisfies_A_TF_zero_edge_premises_proved=True,
        actual_noiseless_upper_Info_alias_projection_and_infinite_line512_step_history_proved=True,
        encoding_composition_represented_GF_bit9_changes_at171U_and172U_proved=True,
        raw_lower_GF_and_clock_remain_canonical_common_in_complete_encoding_execution=True,
        arbitrary_right_Info_all_time_canonical_represented_GF_bank_extension_disproved_for_prepared_family=True,
        prepared_host_not_identified_with_original_J225_fault_or_intact_hierarchy_noise=True,
        selected_full_R_native_Info_holder_cofactors=190,selected_cases_measured_supplements=True,
        actual_J225_after_TF_U_full_repair_general_higher_iid_minimum_proved=False,
        whole81million_tick_CA_experiment_or_original_class_claim=False,
        Gray_G17_or_Gacs_noise_reliability_refutation=False,rule_ROM_constants_or_G17_changed=False,
        global_reliability_established=False,assets_sha256=assets())
    if args.issue:CERT.write_text(json.dumps(cert,indent=2)+'\n')
    else:assert cert==frozen,'Read-only certificate differs.'
    print(json.dumps(dict(passed=True,readonly=not args.issue,assets_verified=len(cert['assets_sha256']),
        certificate_sha256=sha(CERT),upper_steps=512,event_intervals=508646,native_cofactors=190,
        first_right_wrong_upper_GF=171,first_edge_cell_wrong_upper_GF=172,
        prepared_host_only_not_J225_or_iid_counterexample=True,raw_lower_GF_clock_correct=True,
        all_time_repair_or_iid_or_minimum_proved=False,seconds=time.monotonic()-start)),flush=True)
if __name__=='__main__':main()
