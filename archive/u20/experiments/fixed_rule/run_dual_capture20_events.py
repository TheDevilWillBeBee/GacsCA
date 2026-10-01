"""Feed a literal full-rule evaluator capture from three executed gathers.

The fifteen upper cells form one coherent local neighborhood, not a complete
upper colony. Gather events retain lower Data, and one full 8192-cell native
transition captures that Data into the encoded 8Q evaluator. An optional
physical evaluator period then starts from the literal capture result.
"""
import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import resource
import time

from gacsca.fixed_rule import spatial_epoch8 as spatial
from gacsca.fixed_rule import stream28_compact_layout as layout_module
from gacsca.fixed_rule import stream28_dual_holder_rom as holder_rom
from gacsca.fixed_rule import stream28_dual_holder_rule20 as holder
from gacsca.fixed_rule import stream28_dual_native20 as native
from gacsca.fixed_rule import stream28_dual_dense_gpu20 as gpu_full
from gacsca.fixed_rule import stream28_dual_pass20 as physical
from gacsca.fixed_rule import stream28_dual_projected20 as projected
from experiments.fixed_rule.build_compact8_circuit import static_plan
from experiments.fixed_rule.certify_dual_projection20 import neighborhood
from experiments.fixed_rule.compact8_address_rom import (
    project_all_dual_static,template)
from experiments.fixed_rule.replay_compact8_numpy import replay
from experiments.fixed_rule.run_dual_gather20_events import check as gather
from experiments.fixed_rule.audit_dual_holder_send20 import check as send
from experiments.fixed_rule.audit_dual_spatial_gpu20 import verify as verify_gpu
from experiments.fixed_rule.run_dual_spatial_gpu20 import run as gpu_replay


def check(*,physical_period=False,return_state=False,
          upper_age=physical.U-1,seed=2026092928,
          quiet_geometry=False,gpu_spatial=False,
          full_rule_backend='cpu',evaluator_backend='cpu'):
    if full_rule_backend not in ('cpu','gpu'):
        raise ValueError('one complete physical rule backend required')
    ring_step=(native.step_ring if full_rule_backend=='cpu' else
               gpu_full.step_ring)
    if gpu_spatial and not physical_period:
        raise ValueError('GPU parity requires a complete physical evaluator period')
    if evaluator_backend not in ('cpu','gpu'):
        raise ValueError('one fixed physical evaluator backend required')
    if gpu_spatial and evaluator_backend=='gpu':
        raise ValueError('use CPU replay with GPU parity, or GPU as primary')
    started=time.perf_counter()
    center=3218
    target_col=7
    if not 0<=upper_age<physical.U:
        raise ValueError('upper Age outside fixed alphabet')
    upper=neighborhood(center,upper_age,seed)
    if quiet_geometry:
        quiet={name:0 for name,_ in holder.SCHEMA
               if name.startswith('w')}
        upper=tuple(physical.Cell(replace(row.holder,signal=0,**quiet),
                                  row.evaluator) for row in upper)
    upper_words=tuple(word for row in upper
                      for word in physical.encode_cell(row))
    addressed=project_all_dual_static(center,upper_words,True)
    if addressed!=upper_words:
        raise AssertionError('coherent upper static ROM does not project')
    parents=tuple(projected.encode_cell(projected.project(row))
                  for row in upper)
    plan=static_plan(True,True)
    static=set(layout_module.build().static_inputs)
    static_preload={target_col*physical.Q+site:addressed[wire]
                    for site,wire in plan['raw_sources'].items()
                    if wire in static}
    receipt,data,_=gather(colonies=15,parents=parents,
                          initial_data=static_preload,return_data=True)
    raw_source_matches=0
    for site,wire in plan['raw_sources'].items():
        actual=int(data[target_col*physical.Q+site])
        if actual!=addressed[wire]:
            raise AssertionError(('gather/static SOURCE differs',site,wire,
                                  actual,addressed[wire]))
        raw_source_matches+=1
    spatial_rom=template(True,True)
    rows=[]
    for site in range(physical.Q):
        copies={f's{offset+2}_data':int(data[target_col*physical.Q+
                                              ((site+offset)%physical.Q)])
                for offset in holder.OFFSETS}
        h=holder.Cell(**holder_rom.holder_static_fields(site),
                      address=site,age=physical.EARLY_CAPTURE_AGE,
                      **copies)
        rows.append(physical.Cell(h,spatial_rom[site]))
    after=ring_step(tuple(rows))
    captured=tuple(row.evaluator for row in after)
    from experiments.fixed_rule.build_compact8_circuit import initial_cells
    expected=initial_cells(addressed,True,True)
    if captured!=expected:
        site=next(i for i,(a,b) in enumerate(zip(captured,expected)) if a!=b)
        raise AssertionError(('full-rule evaluator capture mismatch',site,
                              captured[site],expected[site]))
    source_matches=sum(captured[site].source_value==addressed[wire]
                       for site,wire in plan['raw_sources'].items())
    if source_matches!=raw_source_matches:
        raise AssertionError('captured SOURCE Data mismatch')
    run,evolved,_=((gpu_replay(captured) if evaluator_backend=='gpu' else
                    replay(1,center,True,True,upper_words,u20=True,
                           captured_rows=captured,
                           record_output_events=True,return_rows=True))
                   if physical_period else (None,None,None))
    gpu_evaluator=(run if evaluator_backend=='gpu' and physical_period else
                   verify_gpu(
                   captured,evolved,run['physical_output_events'],
                   packets=run['packet_deliveries'][0],
                   gates=run['gate_completions'][0],
                   wrap_gates=run['next_period_initial_gate_completions'])
                   if gpu_spatial else None)
    committed=0
    flags={}
    sent=None
    signal_copy_checks=0
    if run is not None:
        events=run['physical_output_events']
        if len(events)!=119 or len({site for _,site,_ in events})!=119:
            raise AssertionError('incomplete physical output event trace')
        for evaluator_age,target,value in events:
            old_data=int(data[target_col*physical.Q+target])
            flag=target in physical.EARLY_FLAG_HOLD_ADDRESSES
            expected=value if flag else old_data
            for backup in holder.OFFSETS:
                center_site=(target-backup)%physical.Q
                neighbors=[]
                for delta in physical.NEIGHBORHOOD:
                    site=(center_site+delta)%physical.Q
                    copies={f's{offset+2}_data':int(data[
                        target_col*physical.Q+((site+offset)%physical.Q)])
                        for offset in holder.OFFSETS}
                    raw=holder.Cell(**holder_rom.holder_static_fields(site),
                        address=site,
                        age=physical.EARLY_RUN_START+evaluator_age-1,
                        **copies)
                    spatial_cell=replace(spatial_rom[site],age=evaluator_age-1)
                    if site==(target+1)%physical.Q:
                        spatial_cell=replace(spatial_cell,
                            mail=spatial.Packet(1,target,0,3,value))
                    neighbors.append(physical.Cell(raw,spatial_cell))
                after=physical.local_step(tuple(neighbors))
                if getattr(after.holder,f's{backup+2}_data')!=expected:
                    raise AssertionError(('literal fivefold Hold commit',
                                          evaluator_age,target,backup))
                committed+=1
            if flag:
                data[target_col*physical.Q+target]=value
                flags[target]=value
        if set(flags)!=set(physical.EARLY_FLAG_HOLD_ADDRESSES):
            raise AssertionError('both early flags must be physically committed')
        sent=send(flag1_value=flags[holder_rom.FLAG1_HOLD],
                  flag2_value=flags[holder_rom.FLAG2_HOLD])
        if not sent['passed'] or sent['packet_phase_intervals_checked']!=10:
            raise AssertionError('actual Flag SEND path failed')
        for pc in range(10):
            target=pc+1 if pc<5 else physical.Q-5+pc-5
            data[target_col*physical.Q+target]=(flags[holder_rom.FLAG2_HOLD]
                                                if pc<5 else
                                                flags[holder_rom.FLAG1_HOLD])
        signal_before=[]
        for site in range(physical.Q):
            copies={f's{offset+2}_data':int(data[target_col*physical.Q+
                                                  ((site+offset)%physical.Q)])
                    for offset in holder.OFFSETS}
            raw=holder.Cell(**holder_rom.holder_static_fields(site),
                        address=site,age=holder.CAPTURE_AGE-1,**copies)
            signal_before.append(physical.Cell(raw,evolved[site]))
        signal_after=ring_step(tuple(signal_before))
        for target,value in ((3,flags[holder_rom.FLAG2_HOLD]),
                             (physical.Q-3,flags[holder_rom.FLAG1_HOLD])):
            for backup in holder.OFFSETS:
                site=(target-backup)%physical.Q
                bit=(signal_after[site].holder.signal>>(backup+2))&1
                if bit!=(value&1):
                    raise AssertionError(('literal physical Signal capture',
                                          target,backup,bit,value))
                signal_copy_checks+=1
    result=dict(passed=True,colonies=15,upper_center_address=center,
                full_rule_backend=full_rule_backend,
                evaluator_backend=evaluator_backend,
                upper_age=upper_age,
                quiet_upper_geometry=quiet_geometry,
                gathered_history_words=receipt['complete_history_words_checked'],
                retained_source_words_checked=raw_source_matches,
                literal_full_ring_capture_sites=physical.Q,
                captured_source_words_checked=source_matches,
                encoded_evaluator_entry_equal=True,
                physical_evaluator_period_checked=physical_period,
                literal_early_holder_copy_steps=committed,
                committed_flag_hold_values=flags,
                actual_flag_send_receipt=sent,
                literal_signal_copy_checks=signal_copy_checks,
                physical_evaluator_receipt=run,
                gpu_evaluator_receipt=gpu_evaluator,
                input_sha256=hashlib.sha256(b''.join(
                    int(word).to_bytes(8,'little') for word in upper_words)).hexdigest(),
                max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                seconds=time.perf_counter()-started,
                limitation='Gather flight is analytically skipped with literal '
                           'endpoints; capture is one literal full-rule ring '
                           'step, not a complete U-period or decoded upper '
                           'macrostep.')
    if return_state:
        if not physical_period:
            raise ValueError('retained state requires a physical evaluator period')
        return result,dict(data=data,upper_words=upper_words,
                           upper=upper,spatial=evolved,
                           signals=tuple(row.holder.signal for row in signal_after),
                           flag_hold=flags,signal_after=signal_after)
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--physical-period',action='store_true')
    parser.add_argument('--upper-age',type=int,default=physical.U-1)
    parser.add_argument('--seed',type=int,default=2026092928)
    parser.add_argument('--quiet-geometry',action='store_true')
    parser.add_argument('--gpu-spatial',action='store_true')
    parser.add_argument('--full-rule-backend',choices=('cpu','gpu'),default='cpu')
    parser.add_argument('--evaluator-backend',choices=('cpu','gpu'),default='cpu')
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=check(physical_period=args.physical_period,
                 upper_age=args.upper_age,seed=args.seed,
                 quiet_geometry=args.quiet_geometry,
                 gpu_spatial=args.gpu_spatial,
                 full_rule_backend=args.full_rule_backend,
                 evaluator_backend=args.evaluator_backend)
    result['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    print(json.dumps(result,indent=2))
    if args.output:
        if args.output.exists():raise FileExistsError(args.output)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
