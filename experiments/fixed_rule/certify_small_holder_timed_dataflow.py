"""Symbolic timed memory events versus the existing batch ROM calculation.

Diagnostic proof checker only. Events are justified separately by physical
instruction/packet lemmas; this module is never an evolution backend.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time

from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c, small_holder_program as p
from gacsca.fixed_rule.wordcode import LIT
from experiments.fixed_rule import certify_small_holder_rom_dataflow as batch
from experiments.fixed_rule import certify_small_holder_mail_schedule as schedule
from experiments.fixed_rule.audit_small_holder_position_events import sha


class TraceBank(list):
    def __init__(self, values):
        super().__init__(values);self.tracking=False;self.reads=[];self.writes=[]
    def __getitem__(self, address):
        value=super().__getitem__(address)
        if self.tracking:self.reads.append((address,value))
        return value
    def __setitem__(self,address,value):
        if self.tracking:self.writes.append((address,value))
        super().__setitem__(address,value)


def events(phase,g):
    stop,rows=g.schedule(phase['start'],phase['end']);out=[];packets=[]
    for pc,times in zip(range(phase['start'],phase['end']),rows):
        op=g.instructions[pc]
        if op.kind in c.ALU_KINDS:
            out.extend(((times[1],0,pc,'read_a'),(times[2],0,pc,'read_b'),(times[3],2,pc,'write_alu')))
        elif op.kind==LIT:out.append((times[-1],2,pc,'literal'))
        elif op.kind==c.LOAD:out.append((times[-1],0,pc,'load'))
        elif op.kind==c.META:out.append((times[-1],2,pc,'metadata'))
        elif op.kind==c.SEND:
            birth=times[-1];hops,direction=op.d>>1,op.d&1
            distance=hops*f.Q+(op.a-op.b if direction else op.b-op.a)
            assert distance>0
            out.extend(((birth,0,pc,'send'),(birth+distance,1,pc,'deliver')))
            packets.append((pc,phase['origin']+birth,op.a,op.b,op.d,distance,phase['origin']+birth+distance))
        else:assert op.kind in (c.HALT,c.IF_THIRD)
    assert stop+phase['origin']==phase['head_stopped']
    assert packets==[tuple(row) for row in phase['packets']]
    return sorted(out),stop


class Timed:
    def __init__(self,reference):
        self.reference=reference;self.t=reference.t;self.g=reference.g;self.n=reference.n
        self.memory=[list(bank) for bank in reference.memory];self.phases=[]
        self.read_count=self.write_count=self.delivery_count=0

    def reset(self,stage):
        for address in range(f.Q):
            row=self.reference.rom[address] if address<len(self.reference.rom) else tuple(c.fallback(address,i) for i in range(7))
            if row[5] or (row[0]==c.MEM and (int(row[2])>>stage)&1):
                for bank in self.memory:bank[address]=self.reference.zero

    def vote(self):
        for bank in self.memory:
            for at in self.g.votes:
                a,b,d=(bank[at+j] for j in (-1,1,2))
                assert a==b==d,'noiseless histories differ'
                bank[at]=a

    def phase(self,phase):
        ref=self.reference;runs=[];ref_reads=[];ref_writes=[]
        for col in range(self.n):
            bank=TraceBank(ref.memory[col]);ref.memory[col]=bank;bank.tracking=True
            run=ref.execute(col,phase['start'],third=phase['third']);bank.tracking=False
            runs.append(run);ref_reads.append(bank.reads);ref_writes.append(bank.writes)
        deadline=phase['deadline']-phase['origin']
        ref.deliver(runs,deadline=deadline,protected=phase['name'].startswith('gather'))
        timeline,stop=events(phase,self.g)
        assert all(run['ticks']==stop for run in runs)
        reads=[[] for _ in range(self.n)];writes=[[] for _ in range(self.n)]
        left=[None]*self.n;value=[None]*self.n;query=[None]*self.n;packets={}
        def read(col,address):
            assert ref.mem(address);word=self.memory[col][address]
            reads[col].append((address,word));self.read_count+=1;return word
        def write(col,address,word):
            assert ref.mem(address);self.memory[col][address]=word
            writes[col].append((address,word));self.write_count+=1
        for tick,priority,pc,kind in timeline:
            assert tick<deadline
            op=self.g.instructions[pc]
            if kind=='deliver':
                payload=packets.pop(pc);hops,direction=op.d>>1,op.d&1
                for col,word in enumerate(payload):
                    dest=(col+(-hops if direction else hops))%self.n
                    self.memory[dest][op.b]=word;self.delivery_count+=1
                continue
            if kind=='send':
                assert pc not in packets;packets[pc]=tuple(read(col,op.a) for col in range(self.n));continue
            for col in range(self.n):
                if kind=='read_a':left[col]=read(col,op.a)
                elif kind=='read_b':
                    assert left[col] is not None
                    value[col]=self.t.op(op.kind,left[col],read(col,op.b))
                elif kind=='write_alu':
                    assert value[col] is not None;write(col,op.d,value[col])
                elif kind=='literal':write(col,op.d,self.t.const(op.a))
                elif kind=='load':query[col]=read(col,op.a)
                elif kind=='metadata':
                    assert query[col] is not None;write(col,op.a,self.t.lookup(query[col],op.b))
                else:raise AssertionError(kind)
        assert not packets,'live packet at phase boundary'
        assert reads==ref_reads,'timed instruction read differs from batch interpretation'
        assert writes==ref_writes,'timed instruction write differs from batch interpretation'
        self.equal_memory()
        result=dict(name=phase['name'],passed=True,timed_events=len(timeline),
                    reads=sum(map(len,reads)),writes=sum(map(len,writes)),
                    deliveries=self.n*len(phase['packets']),head_stopped=phase['head_stopped'],
                    last_memory_event=phase['origin']+max((row[0] for row in timeline),default=stop),
                    no_pending_packets=True,all_instruction_reads_and_writes_match=True,
                    all_Data_words_match=self.n*f.Q)
        self.phases.append(result);return result

    def equal_memory(self):
        assert all(actual==expected for actual,expected in zip(self.memory,self.reference.memory)), 'timed/batch Data mismatch'


def prove(schedule_doc):
    ref=batch.Checker(p.base_rom());timed=Timed(ref);g=ref.g
    phases={row['name']:row for row in schedule_doc['phases']}
    for stage in range(3):
        ref.reset(stage);timed.reset(stage);timed.equal_memory()
        timed.phase(phases[f'gather_{stage}'])
        for col in range(ref.n):
            assert tuple(timed.memory[col][a] for a in g.info)==ref.normal[col]
            for prior in range(stage+1):
                for neighbor in range(-7,8):
                    assert tuple(timed.memory[col][g.history(prior,neighbor,k)] for k in range(f.FIELDS))==ref.normal[(col+neighbor)%ref.n]
    ref.vote();timed.vote();timed.equal_memory()
    expected=tuple(tuple(ref.t.normalize(ref.t.expression(f.self_description(),tuple(w for j in range(-7,8) for w in ref.normal[(col+j)%ref.n])))) for col in range(ref.n))
    timed.phase(phases['third_evaluation'])
    for col in range(ref.n):
        assert tuple(timed.memory[col][a] for a in g.hold)==expected[col]
        for address in range(1,6):assert timed.memory[col][address]==expected[col][f.COL['f2']]
        for address in range(f.Q-5,f.Q):assert timed.memory[col][address]==expected[col][f.COL['f1']]
    ref.reset(3);timed.reset(3);timed.phase(phases['precommit_halt'])
    ref.reset(4);timed.reset(4);ref.vote();timed.vote();timed.equal_memory()
    timed.phase(phases['final_evaluation'])
    for col in range(ref.n):
        assert tuple(timed.memory[col][a] for a in g.hold)==expected[col]
        for a in g.info:
            ref.memory[col][a]=ref.memory[col][a+1];timed.memory[col][a]=timed.memory[col][a+1]
        assert tuple(timed.memory[col][a] for a in g.info)==expected[col]
    # Post-commit scratch is allowed by the proposed Age-0 entry relation.
    # The next literal reset clears it before any completed instruction.
    ref.reset(0);timed.reset(0);timed.equal_memory()
    info={a:i for i,a in enumerate(g.info)}
    for col,bank in enumerate(timed.memory):
        for address,word in enumerate(bank):
            assert word==(expected[col][info[address]] if address in info else ref.zero)
    return dict(passed=True,colonies=ref.n,input_raw_words=ref.n*f.FIELDS,
                phases=timed.phases,instruction_reads_checked=timed.read_count,
                instruction_writes_checked=timed.write_count,packet_deliveries_checked=timed.delivery_count,
                raw_outputs_per_colony=f.FIELDS,commit_matches_normalized_complete_rule=True,
                next_reset_clears_all_nonInfo_Data=True,symbolic_terms=len(ref.t.nodes),
                limitation='Exact symbolic timed-event/batch equivalence and Data-flow identity. Events still rely on the separately checked physical instruction/packet refinements; this diagnostic is not a physical evolution backend or by itself the full macrostep theorem.')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--schedule',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();doc=json.loads(Path(args.schedule).read_text());assert doc['passed']
    for path,wanted in doc['source_sha256'].items():assert sha(path)==wanted,path
    replay=json.loads(json.dumps(schedule.check(schedule.load_inputs())))
    assert replay['phases']==doc['phases'] and replay['trace_sha256']==doc['trace_sha256']
    result=prove(doc)
    result.update(descriptor_sha256=f.self_description().digest(),schedule_sha256=sha(args.schedule),
                  source_sha256={str(path):sha(path) for path in (Path(__file__),Path(batch.__file__),Path(schedule.__file__))},
                  seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
