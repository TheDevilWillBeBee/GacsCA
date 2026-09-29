"""Full scalar/native checks of context reduction and quiet clock barriers."""
import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import random
import resource
import time

from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c, small_holder_projected as r, small_holder_native as native
from experiments.fixed_rule import certify_small_holder_procedure_context as context
from experiments.fixed_rule import certify_small_holder_quiet_barriers as barrier
from experiments.fixed_rule.audit_small_holder_clock_mail_factorization import ages,assignment
from experiments.fixed_rule import certify_small_holder_raw_mail_factorization as raw_mail
from experiments.fixed_rule.audit_small_holder_position_events import evaluate,sha


def erase(cell):return replace(cell,**{name:0 for name in context.CONTEXT})


def audit_context(cells):
    clean=tuple(map(erase,cells));actual=f.local_step(cells);base=f.local_step(clean)
    assert actual==native.local_step(cells) and base==native.local_step(clean)
    assert actual.address==base.address==cells[7].address
    assert actual.age==base.age==(cells[7].age+1)%f.U
    count=0
    for delta in f.OFFSETS:
        for name,_ in f.PROCEDURE:
            key=f's{delta+2}_{name}'
            wanted=0 if name in context.MAIL and actual.f1 else getattr(base,key)
            assert getattr(actual,key)==wanted,('context relation',key);count+=1
    return actual,count


def quiet_expected(cells):
    center=cells[7];age=center.age;out={};mask=(1<<32)-1
    def data(site):return f.majority5(tuple(getattr(cells[7+site+e],f's{2-e}_data') for e in f.OFFSETS))
    for delta in f.OFFSETS:
        meta={name:getattr(center,f'p{delta+3}_{name}') for name in c.STATIC}
        values={name:0 for name,_ in f.PROCEDURE};values['data']=data(delta)
        if age in c.RESET_AGES:
            stage=c.RESET_AGES.index(age)
            if meta['first'] or (meta['kind']==c.MEM and (meta['a']>>stage)&1):values['data']=0
            if meta['first']:
                entries=(meta['a']&mask,meta['a']>>32,meta['b']&mask,meta['b']>>32,meta['d'])
                values.update(head=1,pc=entries[stage])
        if age==c.VOTE_AGES[0]:values.update(head=meta['first'],pc=meta['d'] if meta['first'] else 0)
        if meta['kind']==c.MEM and not meta['first']:
            if meta['a']&c.VOTE and age in c.VOTE_AGES:
                x,y,z=(data(delta+j) for j in (-1,1,2));values['data']=(x&y)|(x&z)|(y&z)
            if meta['a']&c.INFO and age==f.U-1:values['data']=data(delta+1)
        out.update({f's{delta+2}_{name}':value for name,value in values.items()})
    return out


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--context',required=True);parser.add_argument('--barriers',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter()
    for path in (args.context,args.barriers):
        doc=json.loads(Path(path).read_text());assert doc['passed'] and doc['descriptor_sha256']==f.self_description().digest()
        for source,wanted in doc['source_sha256'].items():assert sha(source)==wanted,source
    rng=random.Random(2026092612);digest=hashlib.sha256();count=words=flagged=quiet=0
    t,raw,_,_=context.prepare();rows=tuple(raw(j) for j in f.NEIGHBORHOOD)
    addresses=(0,1,3,100,f.Q-5,f.Q-3,f.Q-1)
    for age in ages():
        for address in addresses:
            values={node[1]:rng.getrandbits(node[2]) for node in t.nodes if node[0]=='variable'}
            values.update(base_address=address,physical_age=age);values=evaluate(t,values)
            cells=tuple(f.decode_cell(tuple(values[x] for x in row)) for row in rows)
            actual,n=audit_context(cells);count+=1;words+=n;flagged+=actual.f1
            digest.update(json.dumps(f.encode_cell(actual)).encode())
    # Force active controller patterns and dense packet delivery, not just random
    # index matches. Physical context remains independent raw input.
    for phase in range(8):
        t,raw,_=raw_mail.prepare(phase);rows=tuple(raw(j) for j in f.NEIGHBORHOOD)
        for index,age in enumerate(ages()):
            values=assignment(t,phase,age,100,'dense',rng)
            for node in t.nodes:
                if node[0]=='variable' and node[1].startswith('physical_') and node[1]!='physical_age':values[node[1]]=rng.getrandbits(node[2])
            values=evaluate(t,values);cells=tuple(f.decode_cell(tuple(values[x] for x in row)) for row in rows)
            actual,n=audit_context(cells);count+=1;words+=n;flagged+=actual.f1
            digest.update(json.dumps(f.encode_cell(actual)).encode())
    t,raw,_=barrier.prepare();rows=tuple(raw(j) for j in f.NEIGHBORHOOD)
    for age in ages():
        for address in (0,1,9,10,9248,9249,f.Q-3):
            for use_rom in (False,True):
                values={node[1]:rng.getrandbits(node[2]) for node in t.nodes if node[0]=='variable'}
                values.update(base_address=address,physical_age=age)
                if use_rom:
                    for name in values:
                        if name.startswith('meta_'):
                            _,site,field=name.split('_',2);values[name]=r.record((address+int(site))%f.Q)[field]
                values=evaluate(t,values);cells=tuple(f.decode_cell(tuple(values[x] for x in row)) for row in rows)
                actual=f.local_step(cells);assert actual==native.local_step(cells)
                for name,wanted in quiet_expected(cells).items():assert getattr(actual,name)==wanted,('quiet barrier',age,address,use_rom,name)
                assert actual.address==address and actual.age==(age+1)%f.U
                digest.update(json.dumps(f.encode_cell(actual)).encode());quiet+=1
    result=dict(passed=True,context_full_outputs=count,context_erased_outputs=count,
                context_procedure_words_checked=words,context_outputs_with_computed_Flag1=flagged,
                quiet_barrier_complete_outputs=quiet,total_complete_scalar_native_outputs=2*count+quiet,
                sampled_clock_ages=ages(),output_sha256=digest.hexdigest(),
                input_sha256={str(path):sha(path) for path in (args.context,args.barriers)},
                source_sha256={str(path):sha(path) for path in (Path(__file__),Path(context.__file__),Path(barrier.__file__))},
                seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                limitation='Finite local audits, not whole instruction or period execution. Both literal F and context-erased comparison F are diagnostics; context erasure is never inserted into physical trajectories.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
