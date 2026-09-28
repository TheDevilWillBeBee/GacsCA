"""Scalar/native audit of all-clock factorization with arbitrary raw mail."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import resource
import time

import numpy as np
from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c, small_holder_native as native
from experiments.fixed_rule import certify_small_holder_raw_mail_factorization as proof
from experiments.fixed_rule.audit_small_holder_position_events import evaluate, sha


def ages():
    events={0,f.U-1,*c.RESET_AGES,*c.ACTIVE_ENDS,*c.VOTE_AGES,c.CAPTURE_AGE-1,c.WF_START-1,c.WF_END-1}
    return tuple(sorted({age+delta for age in events for delta in (-1,0,1) if 0<=age+delta<f.U}))


def assignment(terms,phase,age,address,mode,rng):
    result={node[1]:rng.getrandbits(node[2]) for node in terms.nodes if node[0]=='variable'}
    result.update(physical_age=age,base_address=address)
    if mode=='raw':return result
    def packet(site,name):
        channel,suffix=name.split('_',1);at=(address+site)%f.Q;sign=-1 if channel=='lp' else 1
        return {'target':(at+sign)%f.Q,'data':(0x1000 if channel=='lp' else 0x2000)+site,
                'remaining':int(at==(0 if sign<0 else f.Q-1)),'valid':1}[suffix]
    for node in terms.nodes:
        if node[0]!='variable':continue
        name=node[1]
        if name.startswith('physical_') and name!='physical_age':
            result[name]=0
        elif name.startswith('meta_'):
            _,site,field=name.split('_',2);site=int(site)
            if field=='kind':result[name]=c.MEM
            elif field=='index':result[name]=(address+site)%f.Q
            elif field in ('first','last'):result[name]=0
            elif field=='a':result[name]=(c.VOTE|c.INFO) if site%3==0 else (31 if site%3==1 else 0)
        elif name.startswith('proc_'):
            _,site,field=name.split('_',2);site=int(site)
            if field=='data':result[name]=0x3000+site
        elif name.startswith('mail_'):
            _,holder,slot,field=name.split('_',3);holder,slot=int(holder),int(slot);site=holder+slot-2
            value=packet(site,field)
            if mode=='two_bad' and holder-site in (-2,-1):value^=(1<<node[2])-1
            result[name]=value
    if phase is not None:
        result.update(old_direction=c.RIGHT,old_ra=address,old_rb=address,
                      old_rd=(age%16) if phase==c.TRANSMIT else address,old_value=0x4000,old_alu=c.ADD)
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--certificate',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    started=time.perf_counter();cert=json.loads(Path(args.certificate).read_text())
    assert cert['passed'] and not cert['pilot'] and cert['all_clock_ages']==f.U
    assert cert['descriptor_sha256']==f.self_description().digest()
    for path,wanted in cert['source_sha256'].items():assert sha(path)==wanted,path
    assert len(cert['cases'])==cert['case_count']==9
    assert {row['phase'] for row in cert['cases']}=={None,*range(8)}
    assert all(row['passed'] and row['independent_raw_mail_replicas'] for row in cert['cases'])
    rng=random.Random(2026092802);count=flagged=mixed=0;digest=hashlib.sha256();by_mode={mode:0 for mode in ('raw','dense','two_bad')}
    sampled_ages=ages();addresses=(0,1,3,4,f.Q-5,f.Q-3,f.Q-1,100)
    for phase in (None,*range(8)):
        terms,raw,local=proof.prepare(phase);holders=tuple(range(-4,5)) if phase is not None else (0,)
        old=[tuple(raw(pos+j) for j in f.NEIGHBORHOOD) for pos in holders]
        erased=[tuple(raw(pos+j,mail=False) for j in f.NEIGHBORHOOD) for pos in holders]
        changes=[{flag:{f.COL[f's{delta+2}_{name}']:value for delta in f.OFFSETS
                        for name,value in local(pos+delta,terms.const(flag)).items()} for flag in (0,1)} for pos in holders]
        for index,age in enumerate(sampled_ages):
            address=addresses[index%len(addresses)]
            for mode in ('raw','dense','two_bad'):
                values=evaluate(terms,assignment(terms,phase,age,address,mode,rng))
                assert values[terms.variable('physical_age',32)]==age
                assert values[terms.variable('base_address',15)]==address
                for pos,rows,clean_rows,replacement in zip(holders,old,erased,changes):
                    neighbors=tuple(f.decode_cell(tuple(values[x] for x in row)) for row in rows)
                    clean=tuple(f.decode_cell(tuple(values[x] for x in row)) for row in clean_rows)
                    actual=f.local_step(neighbors);baseline=f.local_step(clean)
                    assert actual==native.local_step(neighbors),(phase,age,pos,mode,'full native')
                    assert baseline==native.local_step(clean),(phase,age,pos,mode,'baseline native')
                    assert (actual.address,actual.age)==((address+pos)%f.Q,(age+1)%f.U)
                    wanted=list(f.encode_cell(baseline))
                    for field,term in replacement[baseline.f1].items():wanted[field]=values[term]
                    assert f.encode_cell(actual)==tuple(wanted),(phase,age,pos,mode)
                    digest.update(np.array(wanted,dtype=np.uint64).tobytes());count+=1;by_mode[mode]+=1
                    flagged+=actual.f1
        print(json.dumps(dict(phase=phase,complete_outputs=count,seconds=time.perf_counter()-started)),flush=True)
    paths=[Path(__file__),Path(proof.__file__),Path(proof.clock.__file__),
           Path('tests/fixed_rule/test_small_holder_clock_mail_factorization.py'),Path('tests/fixed_rule/test_small_holder_raw_mail_factorization.py'),
           Path('experiments/fixed_rule/audit_small_holder_position_events.py')]
    result=dict(passed=True,complete_scalar_native_outputs=count,mail_erased_scalar_native_outputs=count,
                outputs_by_mode=by_mode,outputs_with_computed_Flag1=flagged,sampled_clock_ages=sampled_ages,
                address_patterns=addresses,raw_words_per_output=f.FIELDS,output_sha256=digest.hexdigest(),
                certificate_sha256=sha(args.certificate),source_sha256={str(path):sha(path) for path in paths},
                seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                limitation='Finite audit at all selected clock boundaries and neighbors, with raw random mail/flags and dense coherent or two-corrupt-copy mail. Not a global work-period or nested/noise execution.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
