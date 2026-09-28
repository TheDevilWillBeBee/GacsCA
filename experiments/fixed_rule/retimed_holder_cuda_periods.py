"""Successive actual GPU periods from Info-only initial physical data.

Compare complete canonical physical boundary states with frozen CPU executions;
check actual gathered histories and Hold at internal phase boundaries. No host
upper step is allowed during physical GPU evolution.
"""
import argparse,hashlib,json,resource,time
from pathlib import Path
from unittest.mock import patch
import numpy as np
from gacsca.fixed_rule import retimed_holder_resident_gather as gpu
from gacsca.fixed_rule import retimed_holder_resident_mixed as mixed
from gacsca.fixed_rule import retimed_holder_resident_period as resident
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_core as c,retimed_holder_program as p
from gacsca.fixed_rule import retimed_holder_projected as r,retimed_holder_native as native
from gacsca.fixed_rule import retimed_holder_cpu_profile as cpu,retimed_holder_cpu_events as events
from gacsca.fixed_rule import retimed_holder_cuda_packets_bridge as bridge,retimed_holder_packed as packed,retimed_holder_quotient as q
from gacsca.fixed_rule.wordcode import Program


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--reference',required=True);parser.add_argument('--output',required=True);parser.add_argument('--periods',type=int,choices=(1,2),default=2);args=parser.parse_args()
 out=Path(args.output);artifact=out.with_suffix('.npz');reference=Path(args.reference)
 if out.exists() or artifact.exists():raise FileExistsError('preserve evidence')
 receipt=json.loads(reference.read_text());assert receipt['passed'] and receipt['periods']>=args.periods
 assert receipt['descriptor_sha256']==f.self_description().digest()
 assert receipt['rom_sha256']==hashlib.sha256(p.base_rom().tobytes()).hexdigest()
 assert sha(reference.with_suffix('.npz'))==receipt['snapshot_sha256']
 for name,digest in receipt['source_sha256'].items():assert sha(name)==digest,name
 started=time.perf_counter();g=p.layout();timing=g.timing_certificate()
 with np.load(reference.with_suffix('.npz'),allow_pickle=False) as saved:
  initial=saved['initial_upper'];parents=tuple(r.decode_cell(row) for row in initial);n=len(parents)
  assert n in (1,15)
  expected=[];upper=parents
  for epoch in range(args.periods):upper=r.step_ring(upper);expected.append(upper)
  results=[];totals={};banks=[];sparse=[];counts=[];rights=[];gpu_seconds=0.
  with gpu.World(parents,device_budget=32*1024**2) as world:
   assert world.time==world.age==0
   initialbank,_,_=world.snapshot();known=np.zeros_like(initialbank)
   for col,parent in enumerate(parents):known[col,list(g.info)]=f.encode_cell(r.lift(parent))
   np.testing.assert_array_equal(initialbank,known)
   def advance(to):
    nonlocal gpu_seconds
    ticks=to-world.age
    if not ticks:return
    assert ticks>0
    tick=time.perf_counter()
    with patch.object(Program,'evaluate',side_effect=AssertionError('host evaluator')),patch.object(f,'local_step',side_effect=AssertionError('host upper rule')),patch.object(r,'local_step',side_effect=AssertionError('host upper rule')),patch.object(native,'local_step',side_effect=AssertionError('host full rule')):
     row=world.advance(ticks,extra_device_budget=32*1024**2)
    gpu_seconds+=time.perf_counter()-tick
    for key,value in row.items():totals[key]=max(totals.get(key,0),value) if key=='extra_device_bytes' else totals.get(key,0)+value
   def quiet():
    bank,rows,count=world.snapshot()
    fields=[q.COL[name] for name in resident.ACTIVE if name!='signal']
    for col,num in enumerate(count):assert not np.any(packed.unpack(rows[col,:int(num)])[:,fields]),'unconsumed head or mail'
    return bank
   for epoch in range(args.periods):
    before=parents if epoch==0 else expected[epoch-1];raw=np.array([f.encode_cell(r.lift(cell)) for cell in before],dtype=np.uint64)
    phases=[];period_start=time.perf_counter()
    for stage in range(3):
     stop=c.RESET_AGES[stage]+max(timing['gathers'][stage]['head_stopped'],timing['gathers'][stage]['last_arrival'])
     advance(stop);bank=quiet()
     for prior in range(stage+1):
      for offset in range(-7,8):
       positions=[g.history(prior,offset,k) for k in range(f.FIELDS)]
       np.testing.assert_array_equal(bank[:,positions],raw[(np.arange(n)+offset)%n])
     phases.append(dict(phase='gather_'+str(stage),age=world.age,actual_history_words_checked=n*(stage+1)*15*f.FIELDS,bank_sha256=hashlib.sha256(bank.tobytes()).hexdigest()))
     print(json.dumps(dict(period=epoch+1,**phases[-1],seconds=time.perf_counter()-started)),flush=True)
    stop=c.VOTE_AGES[0]+max(timing['stage3_head_stopped'],timing['stage3_last_delivery'])
    advance(stop);bank=quiet();wanted=np.array([f.encode_cell(r.lift(cell)) for cell in expected[epoch]],dtype=np.uint64)
    np.testing.assert_array_equal(bank[:,list(g.hold)],wanted)
    np.testing.assert_array_equal(bank[:,g.memory_count:]&1,np.repeat(saved['boundary_right'][epoch][:,None],5,axis=1))
    assert not np.any(bank[:,1:6]&1),'unexpected left Signal capture input'
    phases.append(dict(phase='first_evaluation',age=world.age,complete_Hold_matches=True))
    print(json.dumps(dict(period=epoch+1,**phases[-1],seconds=time.perf_counter()-started)),flush=True)
    advance(c.RESET_AGES[3]+g.schedule(*g.stage_ranges[3])[0]);quiet()
    advance(c.RESET_AGES[4]+g.schedule(*g.stage_ranges[4])[0]);bank=quiet()
    np.testing.assert_array_equal(bank[:,list(g.hold)],wanted)
    advance(f.U)
    assert world.age==0 and world.time==(epoch+1)*f.U
    checkpoint=cpu.World(saved['boundary_data'][epoch],np.zeros((n,len(events.CONTROL)),dtype=np.uint64),np.zeros(n,dtype=np.uint64),age=0,right=saved['boundary_right'][epoch]);checkpoint.time=world.time
    bank,rows,count=bridge.compare(world,checkpoint)
    assert world.decode()==expected[epoch]
    right=np.array([cell.signal>>2 for cell in world.logical_cells(tuple(col*f.Q+f.Q-3 for col in range(n)))],dtype=np.uint64)
    assert world.device_bytes+totals['extra_device_bytes']<=64*1024**2
    banks.append(bank);sparse.append(rows);counts.append(count);rights.append(right)
    results.append(dict(period=epoch+1,passed=True,physical_time=world.time,phases=phases,complete_boundary_state_matches_CPU=True,complete_raw_decode_matches=True,bank_sha256=hashlib.sha256(bank.tobytes()).hexdigest(),seconds=time.perf_counter()-period_start,gpu_seconds_so_far=gpu_seconds))
    print(json.dumps(results[-1]),flush=True)
   np.savez_compressed(artifact,initial_upper=initial,initial_bank=initialbank,boundary_banks=np.stack(banks),boundary_sparse=np.stack(sparse),boundary_counts=np.stack(counts),boundary_right=np.stack(rights))
   paths=[Path(__file__),Path(bridge.__file__),Path(gpu.__file__),Path(gpu.__file__).with_suffix('.cu'),Path(mixed.__file__),Path(resident.__file__),Path(resident.__file__).with_suffix('.cu')]
   result=dict(passed=True,colonies=n,periods=args.periods,physical_ticks=world.time,period_results=results,metrics=totals,gpu_evolution_seconds=gpu_seconds,base_device_bytes=world.device_bytes,peak_explicit_device_bytes=world.device_bytes+totals['extra_device_bytes'],host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,seconds=time.perf_counter()-started,initial_histories_zero=True,one_retained_physical_state=True,descriptor_sha256=f.self_description().digest(),rom_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),reference=str(reference),reference_sha256=sha(reference),reference_artifact_sha256=sha(reference.with_suffix('.npz')),artifact_sha256=sha(artifact),source_sha256={str(path):sha(path) for path in paths},binaries={str(module.library()._name):sha(module.library()._name) for module in (gpu,mixed,resident)},limitation='One-link complete periods on canonical coherent mixed-right/left-zero trajectories only; no complete depth-two work period or general noise robustness.')
 assert totals['physical_ticks']==args.periods*f.U
 assert totals['physical_ticks']==totals['independent_ticks']+totals['synchronous_literal_ticks']+totals['synchronous_transport_or_quiet_ticks']
 out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
