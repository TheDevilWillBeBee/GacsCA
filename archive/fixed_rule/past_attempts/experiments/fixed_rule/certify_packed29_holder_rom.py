"""Conditional complete self-ROM dataflow for the fixed early-Flag branch.

The third stage computes only Flag1/Flag2 and sends them. The fifth stage
recomputes and commits every raw field, including all controller copies.
"""
from types import FunctionType
from gacsca.fixed_rule import packed29_holder_rule as f, packed29_holder_core as c
from gacsca.fixed_rule import packed29_holder_program as p
from gacsca.fixed_rule.wordcode_and import ADD, AND, LIT
from experiments.fixed_rule.certify_and_holder_rom import (
    Terms as PreviousTerms, Checker as PreviousChecker,
)


class Terms(PreviousTerms):
    def lookup(self, address, selector):
        if selector >= len(c.STATIC):return self.const(0)
        value=self.value(address)
        if value is None:return self.intern(('rom',address,selector))
        return self.const(self.rom[value,selector] if value<len(self.rom)
                          else c.fallback(value,selector))

    def normalize(self, raw):
        result=list(raw)
        for offset in f.STATIC_OFFSETS:
            source=raw[f.COL['address']]
            if offset:source=self.op(ADD,source,self.const(offset))
            address=self.band(source,self.const(f.Q-1))
            for selector,name in enumerate(c.STATIC):
                result[f.COL[f'p{offset+3}_{name}']]=self.lookup(address,selector)
        return result


def bind(function):
    namespace=dict(function.__globals__)
    namespace.update(f=f,c=c,p=p,Terms=Terms)
    result=FunctionType(function.__code__,namespace,function.__name__,
                        function.__defaults__,function.__closure__)
    result.__kwdefaults__=function.__kwdefaults__
    return result


class Checker(PreviousChecker):
    __init__=bind(PreviousChecker.__init__)
    _base_reset=bind(PreviousChecker.reset)

    def reset(self,stage):
        self._gather_stage=stage
        return self._base_reset(stage)
    mem=bind(PreviousChecker.mem)
    deliver=bind(PreviousChecker.deliver)
    vote=bind(PreviousChecker.vote)

    def execute(self,col,entry,*,third=False):
        bank=self.memory[col];query=None;messages=[];accesses=set();writes=set()
        pc=entry;phase=0;ticks=1;cycle=2*len(self.rom)
        def read(address):
            if not self.mem(address):raise AssertionError(('non-MEM read',pc,address))
            accesses.add(address);return bank[address]
        def write(address,value):
            if not self.mem(address):raise AssertionError(('non-MEM write',pc,address))
            accesses.add(address);writes.add(address);bank[address]=value
        for _ in range(len(self.g.instructions)+1):
            pos=self.g.physical_position(pc)
            if not self.g.memory_count<=pos<len(self.rom)-1:
                raise AssertionError('head leaves fixed instruction core')
            kind,index,a,b,d,first,last=map(int,self.rom[pos])
            if kind==c.PACK3:
                count=(b>>40)&3
                slot=(pc-index)&0xffffffff
                if count not in (2,3) or slot>=count:
                    raise AssertionError(('invalid physical packed row',pc,pos,count,slot))
                if slot<2:
                    word=(a if slot==0 else b)&((1<<40)-1)
                    kind,a,b,d=word&15,(word>>4)&4095,(word>>16)&4095,(word>>28)&4095
                else:
                    kind,a,b,d=d&15,(d>>4)&4095,(d>>16)&4095,(a>>40)&4095
                if kind not in c.ALU_KINDS:
                    raise AssertionError(('invalid packed ALU kind',pc,pos,kind))
            elif index!=pc:
                raise AssertionError(('instruction identity changed',pc,pos,index))
            if kind in c.ALU_KINDS and d&c.PHASE_MARK:
                if self._gather_stage not in range(3):raise AssertionError('marked ALU outside gather stage')
                d=(d&~c.PHASE_MARK)+c.GATHER_OFFSETS[self._gather_stage]
            if kind==c.SEND and b&c.PHASE_MARK:
                if self._gather_stage not in range(3):raise AssertionError('marked SEND outside gather stage')
                b=(b&~c.PHASE_MARK)+c.GATHER_OFFSETS[self._gather_stage]
            if first or last:
                raise AssertionError('instruction identity/geometry changed')
            targets=[pos]
            if kind in c.ALU_KINDS:targets.extend((a,b,d))
            elif kind==LIT:targets.append(d)
            elif kind in (c.SEND,c.LOAD):targets.append(a)
            for target in targets:
                ticks+=(target-phase)%cycle+1;phase=(target+1)%cycle
            if kind==c.META:
                ticks+=4*len(self.rom)+a-pos;phase=a+1
            self.instructions+=1
            if kind in c.ALU_KINDS:
                write(d,self.t.op(kind,read(a),read(b)))
            elif kind==LIT:write(d,self.t.const(a))
            elif kind==c.LOAD:query=read(a)
            elif kind==c.META:
                if query is None:raise AssertionError('META without LOAD')
                write(a,self.t.lookup(query,b));self.queries+=1
            elif kind==c.SEND:
                if d>15 or not self.mem(b):raise AssertionError('invalid packet target/hops')
                hops,direction=d>>1,d&1
                distance=hops*f.Q+(a-b if direction else b-a)
                if distance<=0:raise AssertionError('packet does not arrive after send')
                dest=(col+(-hops if direction else hops))%self.n
                messages.append((ticks+distance,dest,b,read(a),direction,ticks,col,a,hops))
                self.packets+=1
            elif kind==c.BRANCH_THIRD:
                if pc!=self.g.branch_instruction or a!=self.g.signal_entry:
                    raise AssertionError('branch target differs from own ROM')
                pc=a if third else pc+1
                continue
            elif kind==c.HALT or (kind==c.IF_THIRD and not third):
                return dict(ticks=ticks,messages=messages,accesses=accesses,
                            writes=writes,stop_pc=pc)
            elif kind==c.IF_THIRD:pass
            else:raise AssertionError(('unsupported fixed instruction',kind,pc))
            pc+=1
        raise AssertionError('no program stop')

    def check(self):
        g=self.g
        assert len(g.info)==len(g.hold)==f.FIELDS
        histories_checked=0
        for stage in range(3):
            self.reset(stage)
            runs=[self.execute(col,self.entries[stage]) for col in range(self.n)]
            deadline=(c.VOTE_AGES[0] if stage==2 else c.ACTIVE_ENDS[stage])-c.RESET_AGES[stage]
            last=self.deliver(runs,deadline=deadline,protected=True)
            assert max(x['ticks'] for x in runs)<deadline
            for col in range(self.n):
                assert tuple(self.memory[col][at] for at in g.info)==self.inputs[col]
                for prior in range(stage+1):
                    for wire in g.gathered_inputs:
                        neighbor,field=divmod(wire,f.FIELDS)
                        got=self.memory[col][g.history(prior,neighbor-7,field)]
                        want=self.normal[(col+neighbor-7)%self.n][field]
                        assert got==want,('gathered history mismatch',stage,col,wire)
                        histories_checked+=1
            self.phases.append(dict(kind='gather',stage=stage,
                                    head_stop=max(x['ticks'] for x in runs),
                                    last_delivery=last))
        self.vote()
        expected=tuple(tuple(self.t.normalize(self.t.expression(
            f.self_description(),tuple(w for j in range(-7,8)
                                       for w in self.normal[(col+j)%self.n]))))
            for col in range(self.n))
        first=[self.execute(col,self.entries[4],third=True) for col in range(self.n)]
        last=self.deliver(first,deadline=c.CAPTURE_AGE-c.VOTE_AGES[0])
        assert max(x['ticks'] for x in first)<c.ACTIVE_ENDS[2]-c.VOTE_AGES[0]
        for col in range(self.n):
            for name in ('f1','f2'):
                assert self.memory[col][g.hold[f.COL[name]]]==expected[col][f.COL[name]],(col,name)
            assert all(self.memory[col][at]==expected[col][f.COL['f2']] for at in range(1,6))
            assert all(self.memory[col][at]==expected[col][f.COL['f1']] for at in range(f.Q-5,f.Q))
        self.phases.append(dict(kind='Flag_only_evaluation',
                                head_stop=max(x['ticks'] for x in first),last_delivery=last))
        self.reset(3)
        idle=[self.execute(col,self.entries[3]) for col in range(self.n)]
        assert not any(x['messages'] or x['writes'] for x in idle)
        self.reset(4)
        self.vote()
        final=[self.execute(col,self.entries[4]) for col in range(self.n)]
        assert not any(x['messages'] for x in final)
        assert max(x['ticks'] for x in final)<c.ACTIVE_ENDS[4]-c.RESET_AGES[4]
        for col in range(self.n):
            assert tuple(self.memory[col][at] for at in g.hold)==expected[col],('final raw Hold',col)
            for at in g.info:self.memory[col][at]=self.memory[col][at+1]
        self.reset(0)
        positions={at:i for i,at in enumerate(g.info)}
        for col in range(self.n):
            for at,value in enumerate(self.memory[col]):
                want=expected[col][positions[at]] if at in positions else self.zero
                assert value==want,('complete commit/reset mismatch',col,at)
        self.phases.append(dict(kind='full_final_evaluation',
                                head_stop=max(x['ticks'] for x in final)))
        return dict(passed=True,colonies=self.n,complete_encoded_fields=f.FIELDS,
                    complete_raw_outputs_per_colony=f.FIELDS,
                    histories_checked=histories_checked,
                    instructions_checked=self.instructions,
                    metadata_queries=self.queries,packets=self.packets,
                    symbolic_terms=len(self.t.nodes),phases=self.phases,
                    early_only_flags=True,all_controller_outputs_checked_at_commit=True,
                    scope='Conditional full raw own-ROM data flow, not physical execution.')


def equivalence():
    original=f.self_description();compiled=p.compiled_description()
    terms=Terms(p.base_rom())
    inputs=tuple(terms.variable('input_'+str(i),width)
                 for i,(_,width) in enumerate(f.SCHEMA*15))
    expected=terms.expression(original,inputs)
    actual=terms.expression(compiled,inputs)
    assert len(expected)==len(actual)==f.FIELDS
    for (name,_),got,want in zip(f.SCHEMA,actual,expected):
        assert got==want,('complete optimized output mismatch',name)
    return dict(passed=True,complete_raw_outputs=f.FIELDS,
                original_sha256=original.digest(),compiled_sha256=compiled.digest())


def check():
    equal=equivalence();flow=Checker().check();g=p.layout();timing=g.timing_certificate()
    assert timing['fits']
    path_ticks=sum(g.gather_schedule(i)[0] for i in range(3))
    path_ticks+=sum(g.schedule(*span)[0] for span in g.stage_ranges[3:])
    path_ticks+=g.stage3_schedule()[0]
    return dict(passed=True,equivalence=equal,dataflow=flow,timing=timing,
                Q=f.Q,U=f.U,core_cells=g.computation_cells,
                instruction_cells=len(g.packed.rows),virtual_instructions=len(g.instructions),
                controller_path_ticks=path_ticks,
                physical_period_executed=False,depth2_macrostep_executed=False)


if __name__=='__main__':
    import json
    print(json.dumps(check(),indent=2))
