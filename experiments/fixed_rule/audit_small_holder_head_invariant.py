"""Independent complete scalar/native checks of head routing at clock boundaries."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import resource
import time

from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c
from gacsca.fixed_rule import small_holder_program as p, small_holder_projected as r, small_holder_native as native
from experiments.fixed_rule import certify_small_holder_head_invariant as proof
from experiments.fixed_rule.audit_small_holder_clock_mail_factorization import ages,assignment
from experiments.fixed_rule.audit_small_holder_position_events import evaluate,sha


def destination(age,old):
    """Relative destination for an isolated old head, before clock reboot."""
    if not old['head']:return None
    if not any(lo<=age<hi for lo,hi in zip(c.RESET_AGES,c.ACTIVE_ENDS)):return 0
    matched=old['phase']==c.FETCH and old['pc']==old['index']
    if old['direction']==c.RIGHT and matched:
        if old['kind']==c.HALT:return None
        if old['kind']==c.IF_THIRD and not c.RESET_AGES[2]<=age<c.ACTIVE_ENDS[2]:return None
        if old['kind']==c.WAIT and old['rd']>0:return 0
    if old['direction']==c.LEFT:return 0 if old['first'] else -1
    return 0 if old['last'] else 1


def run_case(terms,raw,phase,age,address,rng,index,override=None):
    rows={pos:tuple(raw(pos+j) for j in f.NEIGHBORHOOD) for pos in range(-4,5)}
    assignments=assignment(terms,phase,age,address,'raw',rng)
    for node in terms.nodes:
        if node[0]!='variable' or not node[1].startswith('meta_'):continue
        _,site,name=node[1].split('_',2);site=int(site)
        assignments[node[1]]=r.record((address+site)%f.Q)[name]
        if site==0 and override and name in override:assignments[node[1]]=override[name]
    record=r.record(address);record.update(override or {})
    if phase is not None:
        assignments.update(old_direction=index%2,old_pc=record['index'],old_rd=(index%7)+1)
    values=evaluate(terms,assignments)
    old=dict(record,head=int(phase is not None),phase=phase,pc=assignments.get('old_pc',0),
             direction=assignments.get('old_direction',0),rd=assignments.get('old_rd',0))
    to=destination(age,old);boot=age in (*c.RESET_AGES,c.VOTE_AGES[0])
    actual={};controller_words=0;digest=hashlib.sha256()
    for holder,neighborhood in rows.items():
        cells=tuple(f.decode_cell(tuple(values[x] for x in row)) for row in neighborhood)
        result=f.local_step(cells);assert result==native.local_step(cells),(phase,age,address,holder,'native')
        assert (result.address,result.age)==((address+holder)%f.Q,(age+1)%f.U)
        actual[holder]=result
        for delta in f.OFFSETS:
            site=holder+delta;at=(address+site)%f.Q
            wanted=int(at==0) if boot else int(to is not None and site==to)
            assert getattr(result,f's{delta+2}_head')==wanted,(phase,age,address,holder,delta,'head')
            if not wanted:
                for name in c.CONTROL:
                    assert getattr(result,f's{delta+2}_{name}')==0,(phase,age,address,holder,delta,name)
                    controller_words+=1
        digest.update(json.dumps(f.encode_cell(result),separators=(',',':')).encode())
    groups=0
    for primary in range(-2,3):
        for name in ('data','head',*c.CONTROL,'wf1','wf2'):
            prefix='w' if name in ('wf1','wf2') else 's'
            copies=[getattr(actual[primary+e],f'{prefix}{2-e}_{name}') for e in f.OFFSETS]
            assert len(set(copies))==1,(phase,age,address,primary,name,'coherence');groups+=1
    if phase is not None and not override and not boot and to is not None:
        assert 0<=address+to<len(p.base_rom()),('core escape',age,address,to)
    return dict(complete_outputs=len(actual),inactive_controller_words=controller_words,
                coherent_groups=groups,output_sha256=digest.hexdigest())


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--certificate',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();cert=json.loads(Path(args.certificate).read_text())
    assert cert['passed'] and not cert['pilot'] and cert['descriptor_sha256']==f.self_description().digest()
    for path,wanted in cert['source_sha256'].items():assert sha(path)==wanted,path
    assert len(cert['cases'])==9 and {row['phase'] for row in cert['cases']}=={None,*range(8)}
    assert cert['geometry']==proof.geometry()
    g=p.layout();halt=g.memory_count+next(i for i,op in enumerate(g.instructions) if op.kind==c.HALT)
    third=g.memory_count+next(i for i,op in enumerate(g.instructions) if op.kind==c.IF_THIRD)
    addresses=(0,1,len(p.base_rom())-2,len(p.base_rom())-1,halt,third)
    rng=random.Random(2026092610);rows=[]
    for phase in (None,*range(8)):
        t,raw,_=proof.raw_mail.prepare(phase)
        for index,age in enumerate(ages()):
            address=addresses[index%len(addresses)]
            if phase is None and index%3==0:address=f.Q-1
            rows.append(run_case(t,raw,phase,age,address,rng,index))
        # Ensure both directions at each actual endpoint/opcode around active/rest/reboot.
        for address in addresses:
            for age in (1,c.VOTE_AGES[0]+1,c.RESET_AGES[4]+1,c.ACTIVE_ENDS[0],0):
                for direction in (0,1):rows.append(run_case(t,raw,phase,age,address,rng,direction))
    # WAIT is absent from this ROM but present in the fixed transition alphabet.
    # Local arbitrary-static proof must cover it, including a coincident endpoint.
    t,raw,_=proof.raw_mail.prepare(c.FETCH)
    for first,last in ((0,0),(1,0),(0,1),(1,1)):
        for direction in (0,1):
            rows.append(run_case(t,raw,c.FETCH,1,100,rng,direction,dict(kind=c.WAIT,first=first,last=last)))
    result=dict(passed=True,cases=len(rows),complete_scalar_native_outputs=sum(row['complete_outputs'] for row in rows),
                inactive_controller_words_checked=sum(row['inactive_controller_words'] for row in rows),
                coherent_five_copy_groups_checked=sum(row['coherent_groups'] for row in rows),
                output_sha256=hashlib.sha256(json.dumps(rows,sort_keys=True).encode()).hexdigest(),
                sampled_clock_ages=ages(),actual_ROM_head_addresses=addresses,arbitrary_WAIT_metadata_cases=8,
                certificate_sha256=sha(args.certificate),source_sha256={str(path):sha(path) for path in (Path(__file__),Path(proof.__file__),Path('experiments/fixed_rule/audit_small_holder_clock_mail_factorization.py'))},
                seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                limitation='Finite complete-output scalar/native audit with actual-ROM metadata and arbitrary raw flags/mail. No whole-work-period, Data/Signal schedule or nested/noise correctness claim.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
