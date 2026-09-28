"""Conditional travel to matching FETCH for actual fixed-ROM entries/successors.

Diagnostic only. SEND successors are explicitly tagged as requiring a future
mail-composition lemma; their lengths do not erase their real emitted packets.
"""
import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import resource
import time

import numpy as np
from gacsca.fixed_rule import small_holder_rule as f,small_holder_core as c,small_holder_program as p
from gacsca.fixed_rule.wordcode import EQ
from experiments.fixed_rule import certify_small_holder_clock_events as clock
from experiments.fixed_rule import certify_small_holder_meta_paths as meta
from experiments.fixed_rule import certify_small_holder_instruction_paths as ordinary
from experiments.fixed_rule import certify_small_holder_event_support as support
from experiments.fixed_rule.audit_small_holder_position_events import sha

SOURCES={
    'clock':'small_holder_clock_events_v2.json','clock_audit':'small_holder_clock_events_audit_v1.json',
    'meta':'small_holder_meta_paths_v2.json','meta_audit':'small_holder_meta_paths_audit_v1.json',
    'ordinary':'small_holder_instruction_paths_v1.json','ordinary_audit':'small_holder_instruction_paths_audit_v1.json',
    'support':'small_holder_event_support_v1.json',
}


def leaf_prepare(memory,interval):
    terms,original=clock.prepare(meta.EVENTS[('scan','right_flight_0')],interval)
    if not memory:return terms,original
    terms.disequalities.clear()
    def raw(pos,after=False):
        values=list(original(pos,after=after))
        for delta in f.STATIC_OFFSETS:
            if pos+delta==0:values[f.COL[f'p{delta+3}_kind']]=terms.const(c.MEM)
        return tuple(values)
    return terms,raw


def prove_memory_leaf(interval):
    terms,raw=leaf_prepare(True,interval)
    for pos in range(-4,5):
        actual=terms.expression(f.self_description(),tuple(w for j in f.NEIGHBORHOOD for w in raw(pos+j)))
        assert actual==raw(pos,after=True),('memory FETCH flight',interval,pos)
    return dict(interval=interval,passed=True,full_raw_outputs=9*f.FIELDS)


@lru_cache(None)
def template(memory):
    terms,raw=leaf_prepare(memory,clock.regular_intervals()[0])
    assert terms.value(raw(1,after=True)[f.COL['s2_head']])==1
    return terms,raw(0),raw(1,after=True),raw(0,after=True)


class DispatchPath:
    def __init__(self,start,pc):
        self.g=p.layout();self.rom=p.base_rom();self.start=start;self.pc=pc;self.target=self.g.memory_count+pc
        assert type(start) is int and type(pc) is int and 0<=pc<len(self.g.instructions)
        assert 0<=start<=self.target<len(self.rom)-1
        self.t=meta.Words(self.rom)
        self.control={name:self.t.variable('retained_'+name,dict(c.SCHEMA)[name]) for name in c.CONTROL}
        self.control.update(phase=self.t.const(c.FETCH),pc=self.t.const(pc),direction=self.t.const(c.RIGHT))
        self.position=start;self.elapsed=0;self.segments=[]

    def flight(self,stop,memory):
        count=stop-self.position;assert count>=0
        if not count:return
        lo,hi=self.position,stop-1
        terms,before,after,own_after=template(memory)
        head=self.t.const(lo) if lo==hi else self.t.bounded('head_'+str(len(self.segments)),15,lo,hi)
        data=self.t.variable('data_'+str(len(self.segments)),64);mapping={}
        def transfer(x):
            if x in mapping:return mapping[x]
            node=terms.nodes[x]
            if node[0]=='const':y=self.t.const(node[1])
            elif node[0]=='variable':
                name=node[1]
                if name.startswith('old_'):y=self.control[name[4:]]
                elif name=='base_address':y=head
                elif name.startswith('meta_0_'):y=self.t.lookup(head,c.STATIC.index(name[7:]))
                elif name=='data_0':y=data
                else:raise AssertionError(('unexpected leaf dependency',node))
            elif node[0]=='op':y=self.t.op(node[1],transfer(node[2]),transfer(node[3]))
            elif node[0]=='not':y=self.t.inv(transfer(node[1]))
            elif node[0]=='modadd':y=self.t.modular_add(transfer(node[1]),node[2],node[3])
            else:raise AssertionError(node)
            mapping[x]=y;return y
        for name in c.CONTROL:
            assert transfer(before[f.COL['s2_'+name]])==self.control[name],('old controller',name)
            assert transfer(after[f.COL['s2_'+name]])==self.control[name],('changed controller',name)
        for selector,name in enumerate(c.STATIC):
            assert transfer(before[f.COL['p3_'+name]])==self.t.lookup(head,selector),('ROM precondition',name,lo,hi)
        for a,b in terms.disequalities:
            a,b=transfer(a),transfer(b)
            if self.t.value(self.t.op(EQ,a,b))==0:continue
            assert {a,b}=={self.control['pc'],self.t.lookup(head,1)}
            assert np.all(self.rom[lo:hi+1,1]!=self.pc),'flight includes a matching instruction'
        assert transfer(own_after[f.COL['s2_data']])==data,'flight changed Data'
        for name in ordinary.PACKETS:assert self.t.value(transfer(own_after[f.COL['s2_'+name]]))==0,'flight emitted mail'
        self.segments.append(dict(memory=memory,start=lo,stop=stop,ticks=count))
        self.position=stop;self.elapsed+=count

    def check(self):
        if self.position<self.g.memory_count:self.flight(self.g.memory_count,True)
        self.flight(self.target,False)
        assert self.position==self.target and self.elapsed==self.target-self.start
        record=self.rom[self.target]
        assert int(record[1])==self.pc and not record[5] and not record[6]
        assert self.t.value(self.control['phase'])==c.FETCH and self.t.value(self.control['direction'])==c.RIGHT
        intervals=[(lo,hi-self.elapsed+1) for lo,hi in clock.regular_intervals() if self.elapsed and hi-lo+1>=self.elapsed]
        return dict(start=self.start,pc=self.pc,target=self.target,duration=self.elapsed,
                    complete_controller_and_Data_preserved=True,segments=self.segments,
                    legal_start_age_intervals=intervals,zero_duration_needs_no_clock_step=not bool(self.elapsed))


def inputs():
    root=Path('figs/fixed_rule');loaded={name:json.loads((root/filename).read_text()) for name,filename in SOURCES.items()}
    for name,data in loaded.items():
        assert data['passed'],name
        if 'descriptor_sha256' in data:assert data['descriptor_sha256']==f.self_description().digest(),name
    for name,module in (('clock',clock),('meta',meta),('ordinary',ordinary),('support',support)):
        assert loaded[name]['source_sha256']==sha(module.__file__),name
    for name in ('clock','meta','ordinary'):
        audit=loaded[name+'_audit'];assert audit['certificate_sha256']==sha(root/SOURCES[name])
        for path,wanted in audit['source_sha256'].items():assert sha(path)==wanted,path
    covered={tuple(row['interval']) for row in loaded['clock']['cases'] if row['family']=='scan' and row['name']=='right_flight_0' and row['passed'] and row['full_raw_outputs']==9*f.FIELDS}
    assert covered==set(clock.regular_intervals())
    assert set(loaded['support']['logical_procedure_offsets'])<=set(range(-4,5))
    meta.verify_rom()
    return loaded


def routes(loaded):
    g=p.layout();result=[];seen=set()
    for pc,kind,third,duration,head,segments in loaded['ordinary']['rows']:
        if head<0:continue
        assert pc not in seen;seen.add(pc)
        result.append(dict(origin='ordinary',origin_id=pc,start=head,pc=pc+1,requires_mail_composition=kind==c.SEND))
    metadata={}
    for row in loaded['meta']['paths']:
        value=(row['destination']+1,row['pc']+1)
        assert row['pc'] not in metadata or metadata[row['pc']]==value
        metadata[row['pc']]=value
    for pc,(start,target) in sorted(metadata.items()):
        assert pc not in seen;seen.add(pc)
        result.append(dict(origin='META',origin_id=pc,start=start,pc=target,requires_mail_composition=False))
    expected={pc for pc,op in enumerate(g.instructions) if op.kind!=c.HALT}
    assert seen==expected,'missing successor route'
    for stage,pc in enumerate(g.entries):result.append(dict(origin='reset_entry',origin_id=stage,start=0,pc=pc,requires_mail_composition=False))
    result.append(dict(origin='vote_entry',origin_id=0,start=0,pc=g.entries[4],requires_mail_composition=False))
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    started=time.perf_counter();loaded=inputs();leaves=[prove_memory_leaf(interval) for interval in clock.regular_intervals()]
    rows=[];samples={};digest=hashlib.sha256()
    for route in routes(loaded):
        result=DispatchPath(route['start'],route['pc']).check();combined=dict(route,**{k:v for k,v in result.items() if k not in ('start','pc')})
        rows.append((route['origin'],route['origin_id'],route['start'],route['pc'],result['duration'],int(route['requires_mail_composition'])))
        digest.update(json.dumps(combined,sort_keys=True).encode())
        key=(route['origin'],bool(result['duration']),route['requires_mail_composition'])
        if str(key) not in samples:samples[str(key)]=combined
    result=dict(passed=True,route_count=len(rows),row_columns=['origin','origin_id','start','pc','duration','requires_mail_composition'],rows=rows,samples=samples,
                SEND_successors_requiring_mail_composition=sum(row[-1] for row in rows),new_full_raw_memory_FETCH_cases=leaves,trace_sha256=digest.hexdigest(),
                descriptor_sha256=f.self_description().digest(),source_sha256=sha(__file__),input_sha256={name:sha(Path('figs/fixed_rule')/filename) for name,filename in SOURCES.items()},
                seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                limitation='Mail-free canonical coherent dispatch preserves full controller/Data up to matching FETCH; actual SEND successors retain mail and are only catalogued conditionally. No incoming-mail or whole-period/nested/noisy theorem.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('rows','samples','new_full_raw_memory_FETCH_cases')},indent=2),flush=True)


if __name__=='__main__':main()
