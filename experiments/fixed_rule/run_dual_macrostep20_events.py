"""Attempt one complete clean U20 macrostep by checked physical events.

Gather and SEND flight and quiet flags use bounded skips. Every clock reset,
evaluator capture, and final Info commit is a complete native ring step; both
8Q circuits evolve continuously. Only a fifteen-cell upper neighborhood is
represented, so this is a local macrostep, not a closed upper ring.
"""
import argparse
from collections import defaultdict
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import resource
import time

import numpy as np

from gacsca.fixed_rule import spatial_epoch8 as spatial
from gacsca.fixed_rule import stream28_compact_layout as layout_module
from gacsca.fixed_rule import stream28_dual_flags_cpu20 as flags_cpu
from gacsca.fixed_rule import stream28_dual_flags_gpu20 as flags_gpu
from gacsca.fixed_rule import stream28_dual_core20 as core
from gacsca.fixed_rule import stream28_dual_holder_rom as rom
from gacsca.fixed_rule import stream28_dual_holder_rule20 as holder
from gacsca.fixed_rule import stream28_dual_native20 as native
from gacsca.fixed_rule import stream28_dual_dense_gpu20 as gpu_full
from gacsca.fixed_rule import stream28_dual_pass20 as physical
from gacsca.fixed_rule import stream28_dual_projected20 as projected
from experiments.fixed_rule.build_compact8_circuit import initial_cells
from experiments.fixed_rule.compact8_address_rom import project_all_dual_static
from experiments.fixed_rule.replay_compact8_numpy import replay
from experiments.fixed_rule.run_dual_capture20_events import check as early
from experiments.fixed_rule.audit_dual_spatial_gpu20 import verify as verify_gpu
from experiments.fixed_rule.run_dual_spatial_gpu20 import run as gpu_replay


def flag_arrays(world):
    if world.colonies!=1:raise ValueError('one lower colony required')
    packed=world.runs
    first=np.zeros(physical.Q,dtype=np.uint8)
    second=np.zeros(physical.Q,dtype=np.uint8)
    start=0
    for stop,one,two in packed:
        for index in range(start,int(stop)):
            base=index*64
            for bit in range(64):
                first[base+bit]=(int(one)>>bit)&1
                second[base+bit]=(int(two)>>bit)&1
        start=int(stop)
    assert start==physical.Q//64
    return first,second


def ring(data,spatial_rows,signal_words,world,head_site=None):
    age=world.info['age']
    first,second=flag_arrays(world)
    on=holder.WF_START<=age<holder.WF_END
    rows=[]
    for site in range(physical.Q):
        copies={f's{offset+2}_data':int(data[(site+offset)%physical.Q])
                for offset in holder.OFFSETS}
        if head_site is not None:
            for offset in holder.OFFSETS:
                if (site+offset)%physical.Q==head_site:
                    copies[f's{offset+2}_head']=1
                    copies[f's{offset+2}_pc']=rom.HALT_PC
        forcing={}
        for offset in holder.OFFSETS:
            source=(site+offset)%physical.Q
            forcing[f'w{offset+2}_wf1']=int(
                on and source>=physical.Q-5 and world.signals[0][0])
            forcing[f'w{offset+2}_wf2']=int(
                on and source<=4 and world.signals[1][0] and
                not first[source])
        raw=holder.Cell(**rom.holder_static_fields(site),
                        address=site,age=age,
                        f1=int(first[site]),f2=int(second[site]),
                        signal=int(signal_words[site]),
                        **copies,**forcing)
        rows.append(physical.Cell(raw,spatial_rows[site]))
    return tuple(rows)


def check_flags(rows,world,label):
    if not all(row.holder.age==world.info['age'] for row in rows):
        raise AssertionError((label,'Age diverged'))
    first,second=flag_arrays(world)
    for site,row in enumerate(rows):
        if (row.holder.f1,row.holder.f2)!=(first[site],second[site]):
            raise AssertionError((label,'physical Flag differs',site))


def check(*,upper_age=physical.U-1,seed=2026092928,
          quiet_geometry=False,flag_backend='cpu',gpu_spatial=False,
          full_rule_backend='cpu',evaluator_backend='cpu'):
    if flag_backend not in ('cpu','gpu'):
        raise ValueError('one fixed-rule flag backend required')
    if full_rule_backend not in ('cpu','gpu'):
        raise ValueError('one complete physical rule backend required')
    if evaluator_backend not in ('cpu','gpu'):
        raise ValueError('one fixed physical evaluator backend required')
    if gpu_spatial and evaluator_backend=='gpu':
        raise ValueError('CPU/GPU parity mode and GPU-primary mode are distinct')
    ring_step=(native.step_ring if full_rule_backend=='cpu' else
               gpu_full.step_ring)
    started=time.perf_counter()
    preceding,state=early(physical_period=True,return_state=True,
                          upper_age=upper_age,seed=seed,
                          quiet_geometry=quiet_geometry,
                          gpu_spatial=gpu_spatial,
                          full_rule_backend=full_rule_backend,
                          evaluator_backend=evaluator_backend)
    target_col=7
    q=physical.Q
    data=state['data'][target_col*q:(target_col+1)*q].copy()
    spatial_rows=state['spatial']
    signal_words=state['signals']
    signal_capture=state['signal_after']
    signal_right=(signal_words[q-3]>>2)&1
    signal_left=(signal_words[3]>>2)&1
    packed={site:row.holder.f1|(row.holder.f2<<1)
            for site,row in enumerate(signal_capture)
            if row.holder.f1 or row.holder.f2}
    full_steps=[]
    for site in range(rom.LAST_SITE):
        row=core.Cell(**dict(zip(core.STATIC,rom.record(site))),
                      address=site,age=holder.RESET_AGES[3]+site+1,
                      head=1,phase=core.FETCH,pc=rom.HALT_PC)
        updated=core.advance(row)
        if (updated!={name:getattr(row,name) for name in core.CONTROL[:-1]}
                or core.halted(row) or core.waiting(row)):
            raise AssertionError(('ordinary HALT head is not inert',site))
    flag_world=(flags_cpu.World if flag_backend=='cpu' else flags_gpu.World)
    with flag_world((signal_right,),(signal_left,),
                         age=holder.CAPTURE_AGE,
                         runs=flags_cpu.pack_sparse(packed)) as flags:
        check_flags(signal_capture,flags,'signal capture')
        next_ring=ring_step(signal_capture)
        flags.run(1,skip_fixed=False)
        check_flags(next_ring,flags,'Signal fixed-point step')
        if tuple(row.holder.signal for row in next_ring)!=signal_words:
            raise AssertionError('Signal not stable after capture')
        if any(row.holder.s2_data!=data[site]
               for site,row in enumerate(next_ring)):
            raise AssertionError('Data changed during quiet Signal step')
        spatial_rows=tuple(row.evaluator for row in next_ring)
        full_steps.append(holder.CAPTURE_AGE)

        flags.run(holder.RESET_AGES[3]-flags.info['age'])
        before=ring(data,spatial_rows,signal_words,flags)
        after=ring_step(before)
        flags.run(1,skip_fixed=False)
        check_flags(after,flags,'stage-three reset')
        if sum(row.holder.s2_head for row in after)!=1:
            raise AssertionError('stage-three HALT head not started once')
        full_steps.append(holder.RESET_AGES[3])
        data=np.array([row.holder.s2_data for row in after],dtype=np.uint64)
        spatial_rows=tuple(row.evaluator for row in after)
        halt_age=holder.RESET_AGES[3]+1+rom.LAST_SITE
        flags.run(halt_age-flags.info['age'])
        before=ring(data,spatial_rows,signal_words,flags,
                    head_site=rom.LAST_SITE)
        after=ring_step(before)
        flags.run(1,skip_fixed=False)
        check_flags(after,flags,'stage-three halt')
        if any(row.holder.s2_head for row in after):
            raise AssertionError('stage-three HALT head persisted')
        data=np.array([row.holder.s2_data for row in after],dtype=np.uint64)
        spatial_rows=tuple(row.evaluator for row in after)
        full_steps.append(halt_age)

        flags.run(holder.WF_END-flags.info['age'])
        before=ring(data,spatial_rows,signal_words,flags)
        after=ring_step(before)
        flags.run(1,skip_fixed=False)
        check_flags(after,flags,'Wf end')
        if (any(row.holder.s2_head for row in after) or
                any(row.holder.s2_data!=data[site]
                    for site,row in enumerate(after)) or
                tuple(row.holder.signal for row in after)!=signal_words):
            raise AssertionError('quiet Wf-end ring state changed unexpectedly')
        spatial_rows=tuple(row.evaluator for row in after)
        full_steps.append(holder.WF_END)

        flags.run(holder.RESET_AGES[4]-flags.info['age'])
        before=ring(data,spatial_rows,signal_words,flags)
        after=ring_step(before)
        flags.run(1,skip_fixed=False)
        check_flags(after,flags,'final reset')
        if any(row.holder.s2_head for row in after):
            raise AssertionError('final evaluator failed to suppress holder head')
        full_steps.append(holder.RESET_AGES[4])
        after=ring_step(after)
        flags.run(1,skip_fixed=False)
        check_flags(after,flags,'final capture')
        if any(row.holder.s2_head for row in after):
            raise AssertionError('final holder head persisted into evaluator')
        full_steps.append(holder.RESET_AGES[4]+1)
        data=np.array([row.holder.s2_data for row in after],dtype=np.uint64)
        captured=tuple(row.evaluator for row in after)
        upper_words=state['upper_words']
        addressed=project_all_dual_static(state['upper'][7].holder.address,
                                          upper_words,True)
        expected_entry=initial_cells(addressed,True,True)
        if captured!=expected_entry:
            site=next(i for i,(a,b) in enumerate(zip(captured,expected_entry))
                      if a!=b)
            raise AssertionError(('final physical capture mismatch',site,
                                  captured[site],expected_entry[site]))
        final,evolved,_=(gpu_replay(captured) if evaluator_backend=='gpu' else
                         replay(1,state['upper'][7].holder.address,True,True,
                                upper_words,u20=True,captured_rows=captured,
                                record_output_events=True,return_rows=True))
        final_gpu=(final if evaluator_backend=='gpu' else verify_gpu(
                   captured,evolved,final['physical_output_events'],
                   packets=final['packet_deliveries'][0],
                   gates=final['gate_completions'][0],
                   wrap_gates=final['next_period_initial_gate_completions'])
                   if gpu_spatial else None)
        events=final['physical_output_events']
        groups=defaultdict(list)
        for age,site,value in events:groups[age].append((site,value))
        commits=0
        for eval_age in sorted(groups):
            absolute=holder.RESET_AGES[4]+2+eval_age-1
            flags.run(absolute-flags.info['age'])
            pre_data=data.copy()
            first,second=flag_arrays(flags)
            for target,value in groups[eval_age]:
                for backup in holder.OFFSETS:
                    center_site=(target-backup)%q
                    neighbors=[]
                    for delta in physical.NEIGHBORHOOD:
                        site=(center_site+delta)%q
                        copies={f's{offset+2}_data':int(pre_data[
                            (site+offset)%q]) for offset in holder.OFFSETS}
                        raw=holder.Cell(**rom.holder_static_fields(site),
                            address=site,age=absolute,
                            f1=int(first[site]),f2=int(second[site]),
                            signal=int(signal_words[site]),**copies)
                        spatial_cell=replace(expected_entry[site],
                                             age=eval_age-1)
                        if site==(target+1)%q:
                            spatial_cell=replace(spatial_cell,
                                mail=spatial.Packet(1,target,0,3,value))
                        neighbors.append(physical.Cell(raw,spatial_cell))
                    out=physical.local_step(tuple(neighbors))
                    if getattr(out.holder,f's{backup+2}_data')!=value:
                        raise AssertionError(('final Hold copy',eval_age,
                                              target,backup))
                    commits+=1
            for target,value in groups[eval_age]:data[target]=value
            flags.run(1,skip_fixed=False)
        if commits!=595:raise AssertionError('incomplete final Hold commits')
        flags.run(physical.U-1-flags.info['age'])
        before=ring(data,evolved,signal_words,flags)
        after=ring_step(before)
        flags.run(1,skip_fixed=False)
        check_flags(after,flags,'final Info commit')
        full_steps.append(physical.U-1)
        layout=layout_module.build()
        decoded=tuple(after[site].holder.s2_data for site in layout.info)
        intended=projected.encode_cell(projected.project(
            physical.local_step(state['upper'])))
        if decoded!=intended:
            mismatches=[(i,a,b) for i,(a,b) in enumerate(zip(decoded,intended))
                        if a!=b]
            raise AssertionError(('decoded upper F differs',mismatches[:12],
                                  len(mismatches)))
        return dict(passed=True,Q=q,U=physical.U,
                    flag_backend=flag_backend,
                    gpu_spatial=gpu_spatial,
                    full_rule_backend=full_rule_backend,
                    evaluator_backend=evaluator_backend,
                    early_gpu_evaluator=preceding['gpu_evaluator_receipt'],
                    final_gpu_evaluator=final_gpu,
                    upper_center_address=state['upper'][7].holder.address,
                    upper_input_age=upper_age,fixture_seed=seed,
                    quiet_upper_geometry=quiet_geometry,
                    complete_gather_history_words=preceding['gathered_history_words'],
                    early_flag_holds=preceding['committed_flag_hold_values'],
                    early_signal_copy_checks=preceding['literal_signal_copy_checks'],
                    full_literal_ring_step_ages=full_steps,
                    final_evaluator_packets=final['packet_deliveries'][0],
                    final_evaluator_gate_completions=final['gate_completions'][0],
                    final_literal_holder_copy_steps=commits,
                    decoded_upper_words=len(decoded),
                    changed_upper_words=sum(a!=b for a,b in zip(
                        projected.encode_cell(projected.project(state['upper'][7])),
                        decoded)),
                    decoded_sha256=hashlib.sha256(np.array(decoded,dtype=np.uint64)
                                                  .tobytes()).hexdigest(),
                    flag_metrics=flags.info,
                    max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                    seconds=time.perf_counter()-started,
                    limitation='One local upper macrostep with checked clean-domain '
                               'event skips, not a continuous full lower-rule '
                               'U-period, a closed upper ring, a second macrostep, '
                               'or a repair/noise result.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--upper-age',type=int,default=physical.U-1)
    parser.add_argument('--seed',type=int,default=2026092928)
    parser.add_argument('--quiet-geometry',action='store_true')
    parser.add_argument('--flag-backend',choices=('cpu','gpu'),default='cpu')
    parser.add_argument('--gpu-spatial',action='store_true')
    parser.add_argument('--full-rule-backend',choices=('cpu','gpu'),default='cpu')
    parser.add_argument('--evaluator-backend',choices=('cpu','gpu'),default='cpu')
    args=parser.parse_args()
    result=check(upper_age=args.upper_age,seed=args.seed,
                 quiet_geometry=args.quiet_geometry,
                 flag_backend=args.flag_backend,
                 gpu_spatial=args.gpu_spatial,
                 full_rule_backend=args.full_rule_backend,
                 evaluator_backend=args.evaluator_backend)
    result['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    print(json.dumps(result,indent=2))
    if args.output:
        if args.output.exists():raise FileExistsError(args.output)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
