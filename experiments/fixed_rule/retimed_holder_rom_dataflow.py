"""Symbolic data-flow certificate for the actual fixed colony ROM.

Diagnostic checker only, never an evolution backend. The abstraction of a
completed physical instruction (and its schedule recipe) is an explicit premise;
this does not establish the missing physical instruction-refinement theorem.
"""
import argparse,hashlib,json,resource,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_core as c,retimed_holder_program as p
from gacsca.fixed_rule.wordcode import NAND,ADD,SHR,EQ,LT,LIT,MASK,arithmetic


class Terms:
    def __init__(self,rom):self.rom=rom;self.nodes=[];self.ids={}
    def intern(self,node):
        if node not in self.ids:self.ids[node]=len(self.nodes);self.nodes.append(node)
        return self.ids[node]
    def const(self,value):return self.intern(('const',int(value)&MASK))
    def value(self,term):
        node=self.nodes[term];return node[1] if node[0]=='const' else None
    def op(self,kind,a,b):
        av,bv=self.value(a),self.value(b)
        if av is not None and bv is not None:return self.const(arithmetic(kind,av,bv))
        if kind==ADD and av==0:return b
        if kind==ADD and bv==0:return a
        if kind==SHR and bv==0:return a
        if kind==EQ and a==b:return self.const(1)
        if kind in (ADD,NAND,EQ) and a>b:a,b=b,a
        return self.intern(('op',kind,a,b))
    def band(self,a,b):
        x=self.op(NAND,a,b);return self.op(NAND,x,x)
    def lookup(self,address,selector):
        if selector>=len(c.STATIC):return self.const(0)
        value=self.value(address)
        if value is None:return self.intern(('rom',address,selector))
        return self.const(self.rom[value,selector] if value<len(self.rom) else c.fallback(value,selector))
    def normalize(self,raw):
        result=list(raw);address=raw[f.COL['address']]
        for offset in f.STATIC_OFFSETS:
            at=address if not offset else self.band(self.op(ADD,address,self.const(offset)),self.const(f.Q-1))
            for selector,name in enumerate(c.STATIC):result[f.COL[f'p{offset+3}_{name}']]=self.lookup(at,selector)
        return result
    def expression(self,description,inputs):
        values=list(inputs)
        for kind,a,b in description.operations:values.append(self.const(a) if kind==LIT else self.op(kind,values[a],values[b]))
        return tuple(values[i] for i in description.outputs)


class Checker:
    def __init__(self,rom):
        self.rom=np.asarray(rom,dtype=np.uint64);self.g=p.layout();self.n=15
        if self.rom.shape!=p.base_rom().shape:raise AssertionError('fixed ROM shape required')
        self.t=Terms(self.rom);self.zero=self.t.const(0)
        self.memory=[[self.zero]*f.Q for _ in range(self.n)]
        self.inputs=tuple(tuple(self.t.intern(('input',col,name,width)) for name,width in f.SCHEMA) for col in range(self.n))
        self.normal=tuple(tuple(self.t.normalize(row)) for row in self.inputs)
        for col in range(self.n):
            for at,value in zip(self.g.info,self.inputs[col]):self.memory[col][at]=value
        header=self.rom[0];self.entries=tuple(int((int(header[2 if stage<2 else 3])>>(32*(stage%2)))&0xFFFFFFFF) if stage<4 else int(header[4]) for stage in range(5))
        if self.entries!=self.g.entries:raise AssertionError('entry header differs from fixed phase layout')
        self.instructions=0;self.queries=0;self.packets=0;self.phases=[]
    def mem(self,address):
        return 0<=address<self.g.memory_count or f.Q-5<=address<f.Q
    def reset(self,stage):
        for a in range(f.Q):
            record=self.rom[a] if a<len(self.rom) else tuple(c.fallback(a,k) for k in range(7))
            if record[5] or (record[0]==c.MEM and (int(record[2])>>stage)&1):
                for bank in self.memory:bank[a]=self.zero
    def execute(self,col,entry,*,third=False):
        bank=self.memory[col];query=None;messages=[];accesses=set();writes=set();pc=entry;phase=0;ticks=1;cycle=2*len(self.rom)
        def read(address):
            if not self.mem(address):raise AssertionError(('non-MEM read',pc,address))
            accesses.add(address);return bank[address]
        def write(address,value):
            if not self.mem(address):raise AssertionError(('non-MEM write',pc,address))
            accesses.add(address);writes.add(address);bank[address]=value
        for _ in range(len(self.rom)):
            pos=self.g.memory_count+pc
            if not self.g.memory_count<=pos<len(self.rom)-1:raise AssertionError('head leaves fixed instruction core')
            kind,index,a,b,d,first,last=map(int,self.rom[pos])
            if index!=pc or first or last:raise AssertionError('instruction identity/geometry changed')
            targets=[pos]
            if kind in c.ALU_KINDS:targets.extend((a,b,d))
            elif kind==LIT:targets.append(d)
            elif kind in (c.SEND,c.LOAD):targets.append(a)
            for target in targets:ticks+=(target-phase)%cycle+1;phase=(target+1)%cycle
            if kind==c.META:ticks+=4*len(self.rom)+a-pos;phase=a+1
            self.instructions+=1
            if kind in c.ALU_KINDS:write(d,self.t.op(kind,read(a),read(b)))
            elif kind==LIT:write(d,self.t.const(a))
            elif kind==c.LOAD:query=read(a)
            elif kind==c.META:
                if query is None:raise AssertionError('META without a LOAD')
                write(a,self.t.lookup(query,b));self.queries+=1
            elif kind==c.SEND:
                if d>15 or not self.mem(b):raise AssertionError('invalid physical packet target/hops')
                hops,direction=d>>1,d&1;distance=hops*f.Q+(a-b if direction else b-a)
                if distance<=0:raise AssertionError('packet does not arrive after send')
                dest=(col+(-hops if direction else hops))%self.n
                messages.append((ticks+distance,dest,b,read(a),direction,ticks,col,a,hops));self.packets+=1
            elif kind==c.HALT or (kind==c.IF_THIRD and not third):
                return dict(ticks=ticks,messages=messages,accesses=accesses,writes=writes,stop_pc=pc)
            elif kind==c.IF_THIRD:pass
            else:raise AssertionError(('unsupported fixed-program instruction',kind,pc))
            pc+=1
        raise AssertionError('no program stop')
    def deliver(self,runs,*,deadline,protected=False):
        messages=[m for run in runs for m in run['messages']];lines={};destinations=set()
        for arrival,dest,target,value,direction,birth,source,address,hops in messages:
            if arrival>=deadline:raise AssertionError('delivery reaches clock deadline')
            key=(direction,(source*f.Q+address+(birth if direction else -birth))%(self.n*f.Q))
            lines.setdefault(key,[]).append((birth,arrival))
            if protected and target in runs[dest]['accesses']:raise AssertionError('controller/foreign-mail dependence')
            if (dest,target) in destinations:raise AssertionError('two deliveries to same phase destination')
            destinations.add((dest,target))
        for intervals in lines.values():
            intervals.sort()
            if any(a[1]>b[0] for a,b in zip(intervals,intervals[1:])):raise AssertionError('same-track packet overlap')
        for arrival,dest,target,value,*_ in sorted(messages):self.memory[dest][target]=value
        return max((m[0] for m in messages),default=0)
    def vote(self):
        for col in range(self.n):
            for at in self.g.votes:
                a,b,d=(self.memory[col][at+j] for j in (-1,1,2))
                if not a==b==d:raise AssertionError('three retrieved histories disagree')
                self.memory[col][at]=a # exact idempotence of bitwise majority
    def check(self):
        # Three real gather bodies, including executed input META regeneration.
        for stage in range(3):
            self.reset(stage);runs=[self.execute(col,self.entries[stage]) for col in range(self.n)]
            deadline=(c.VOTE_AGES[0] if stage==2 else c.ACTIVE_ENDS[stage])-c.RESET_AGES[stage]
            last=self.deliver(runs,deadline=deadline,protected=True)
            if max(x['ticks'] for x in runs)>=deadline:raise AssertionError('gather head exceeds phase')
            for col in range(self.n):
                if tuple(self.memory[col][a] for a in self.g.info)!=self.normal[col]:raise AssertionError('Info not fully regenerated')
                for prior in range(stage+1):
                    for neighbor in range(-7,8):
                        got=tuple(self.memory[col][self.g.history(prior,neighbor,k)] for k in range(f.FIELDS))
                        if got!=self.normal[(col+neighbor)%self.n]:raise AssertionError(('retrieved raw history mismatch',stage,col,neighbor))
            self.phases.append(dict(kind='gather',stage=stage,head_stop=max(x['ticks'] for x in runs),last_delivery=last,deadline=deadline))
        self.vote()
        expected=tuple(tuple(self.t.normalize(self.t.expression(f.self_description(),tuple(w for j in range(-7,8) for w in self.normal[(col+j)%self.n])))) for col in range(self.n))
        first=[self.execute(col,self.entries[4],third=True) for col in range(self.n)]
        last=self.deliver(first,deadline=c.CAPTURE_AGE-c.VOTE_AGES[0])
        if max(x['ticks'] for x in first)>=c.ACTIVE_ENDS[2]-c.VOTE_AGES[0]:raise AssertionError('third stage head misses stop')
        for col in range(self.n):
            if tuple(self.memory[col][a] for a in self.g.hold)!=expected[col]:raise AssertionError(('first computed raw Hold mismatch',col))
            for a in range(1,6):
                if self.memory[col][a]!=expected[col][f.COL['f2']]:raise AssertionError('left Signal payload mismatch')
            for a in range(f.Q-5,f.Q):
                if self.memory[col][a]!=expected[col][f.COL['f1']]:raise AssertionError('right Signal payload mismatch')
        # The local capture/flag/reset identities are separate physical premises.
        self.phases.append(dict(kind='third_evaluation',head_stop=max(x['ticks'] for x in first),last_delivery=last,capture_deadline=c.CAPTURE_AGE-c.VOTE_AGES[0]))
        self.reset(3)
        idle=[self.execute(col,self.entries[3]) for col in range(self.n)]
        if any(x['messages'] or x['writes'] for x in idle):raise AssertionError('idle stage changes Data')
        self.reset(4);self.vote()
        final=[self.execute(col,self.entries[4]) for col in range(self.n)]
        if any(x['messages'] for x in final):raise AssertionError('late signal delivery')
        if max(x['ticks'] for x in final)>=c.ACTIVE_ENDS[4]-c.RESET_AGES[4]:raise AssertionError('final evaluator exceeds phase')
        for col in range(self.n):
            if tuple(self.memory[col][a] for a in self.g.hold)!=expected[col]:raise AssertionError(('final computed raw Hold mismatch',col))
            for a in self.g.info:self.memory[col][a]=self.memory[col][a+1]
        self.reset(0)
        for col in range(self.n):
            for a,value in enumerate(self.memory[col]):
                want=expected[col][self.g.info.index(a)] if a in self.g.info else self.zero
                if value!=want:raise AssertionError(('noncanonical final Data',col,a))
        self.phases.append(dict(kind='final_evaluation',head_stop=max(x['ticks'] for x in final),deadline=c.ACTIVE_ENDS[4]-c.RESET_AGES[4]))
        return dict(passed=True,colonies=self.n,input_raw_words=self.n*f.FIELDS,complete_raw_outputs_per_colony=f.FIELDS,instructions_checked=self.instructions,metadata_queries=self.queries,packets=self.packets,symbolic_terms=len(self.t.nodes),phases=self.phases,descriptor_sha256=f.self_description().digest(),rom_sha256=hashlib.sha256(self.rom.tobytes()).hexdigest(),claim='Exact all-input ROM Data-flow identity including raw-controller outputs, both metadata regenerations, all three histories, votes, two evaluations, signal payloads, commit and scratch clearing; conditional on completed-instruction and timing abstractions.',missing_physical_obligations=['all-input local-controller refinement of each instruction and constant scan duration, especially LOAD/META','full coherent physical evolution and head/mail stopping across barriers','integration with physical signal capture/flag clearing and full reset certificate','noisy histories and intermediate physical time reconstruction'],not_an_execution_backend=True)


def certify(rom=None):return Checker(p.base_rom() if rom is None else rom).check()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();result=certify();result.update(seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
