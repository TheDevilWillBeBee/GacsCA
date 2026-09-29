"""Full raw physical event identities with symbolic operand/controller words.

Diagnostic only. Concrete ROM positions and event ages are stated per case;
this is not yet a certificate of all scan positions, clock phases, or a period.
"""
import argparse,hashlib,json,resource,time
from pathlib import Path
from gacsca.fixed_rule import small_holder_rule as f,small_holder_core as c
from gacsca.fixed_rule import small_holder_projected as r,small_holder_program as p
from gacsca.fixed_rule.wordcode import NAND,ADD,SHR,EQ,LT,LIT,MASK,arithmetic
from experiments.fixed_rule.certify_small_holder_rom_dataflow import Terms
from experiments.fixed_rule.prove_small_holder_boundary import validate


class Algebra(Terms):
    def inv(self,a):
        v=self.value(a)
        if v is not None:return self.const(v^MASK)
        node=self.nodes[a]
        return node[1] if node[0]=='not' else self.intern(('not',a))
    def op(self,kind,a,b):
        if kind==NAND:
            av,bv=self.value(a),self.value(b)
            if av==0 or bv==0:return self.const(MASK)
            if av==MASK:return self.inv(b)
            if bv==MASK:return self.inv(a)
            if a==b:return self.inv(a)
        return super().op(kind,a,b)
    def variable(self,name,width):return self.intern(('variable',name,width))
    def mask(self,x,width):return self.band(x,self.const((1<<width)-1))


def cases():
    result=[dict(name='quiet',role='quiet',at=100,age=c.VOTE_AGES[0]+10)]
    for opcode in c.ALU_KINDS:result.append(dict(name=f'read_b_{opcode}',role='read_b',opcode=opcode,at=100,age=c.VOTE_AGES[0]+10))
    for role in ('read_a','write','load'):result.append(dict(name=role,role=role,at=100,age=c.VOTE_AGES[0]+10))
    for direction in (0,1):
        for hops in range(8):result.append(dict(name=f'send_{direction}_{hops}',role='send',direction=direction,hops=hops,at=100,age=1))
    for kind in (*c.ALU_KINDS,LIT,c.SEND,c.LOAD,c.META,c.HALT,c.IF_THIRD):
        pc=next(i for i,op in enumerate(p.layout().instructions) if op.kind==kind)
        for late in ((False,True) if kind==c.IF_THIRD else (False,)):
            result.append(dict(name=f'fetch_{kind}_{int(late)}',role='fetch',kind=kind,pc=pc,at=p.layout().memory_count+pc,age=(c.RESET_AGES[4] if late else c.VOTE_AGES[0])+10))
    for selector in range(7):result.append(dict(name=f'meta_read_{selector}',role='meta_read',selector=selector,at=p.layout().memory_count+17,age=c.VOTE_AGES[0]+10))
    result.append(dict(name='reflect_ready',role='reflect_ready',at=0,age=c.VOTE_AGES[0]+10))
    result.append(dict(name='reflect_value',role='reflect_value',at=0,age=c.VOTE_AGES[0]+10))
    for query in (len(p.base_rom()),f.Q-5,f.Q-1):
        for selector in range(7):result.append(dict(name=f'fallback_{query}_{selector}',role='fallback',query=query,selector=selector,at=0,age=c.VOTE_AGES[0]+10))
    return tuple(result)


def prepare(case):
    t=Algebra(p.base_rom());z=t.const(0);one=t.const(1);at=case['at'];age=case['age'];role=case['role']
    widths=dict(c.SCHEMA)
    ctrl={name:t.variable('old_'+name,widths[name]) for name in c.CONTROL}
    ctrl.update(direction=z,phase=z)
    data={pos:t.variable(f'data_{pos-at}',64) if r.record(pos%f.Q)['kind']==c.MEM else z for pos in range(at-16,at+17)}
    old=dict(ctrl);new=None;new_at=at+1;new_data=dict(data);packet={}
    if role=='quiet':old={name:z for name in c.CONTROL}
    elif role=='read_b':
        old.update(phase=t.const(c.READ_B),rb=t.const(at),alu=t.const(case['opcode']))
        new=dict(old,phase=t.const(c.WRITE),value=t.op(case['opcode'],old['value'],data[at]))
    elif role=='read_a':
        old.update(phase=t.const(c.READ_A),ra=t.const(at));new=dict(old,phase=t.const(c.READ_B),value=data[at])
    elif role=='write':
        old.update(phase=t.const(c.WRITE),rd=t.const(at));new=dict(old,phase=z,pc=t.mask(t.op(ADD,old['pc'],one),32));new_data[at]=old['value']
    elif role=='load':
        old.update(phase=t.const(c.READ_LOAD),ra=t.const(at));new=dict(old,phase=z,rd=data[at],pc=t.mask(t.op(ADD,old['pc'],one),32))
    elif role=='send':
        old.update(phase=t.const(c.TRANSMIT),ra=t.const(at),rd=t.const(2*case['hops']+case['direction']))
        new=dict(old,phase=z,pc=t.mask(t.op(ADD,old['pc'],one),32))
        track='lp' if case['direction'] else 'rp'
        packet={track+'_target':t.mask(old['rb'],32),track+'_data':data[at],track+'_remaining':t.const(case['hops']),track+'_valid':one}
    elif role=='fetch':
        old.update(phase=z,pc=t.const(case['pc']));new=dict(old);kind=case['kind'];rom=r.record(at)
        if kind in c.ALU_KINDS:new.update(phase=t.const(c.READ_A),ra=t.const(rom['a']&0xFFFFFFFF),rb=t.const(rom['b']),rd=t.const(rom['d']),alu=t.const(kind))
        elif kind==LIT:new.update(phase=t.const(c.WRITE),rd=t.const(rom['d']),value=t.const(rom['a']))
        elif kind==c.SEND:new.update(phase=t.const(c.TRANSMIT),ra=t.const(rom['a']&0xFFFFFFFF),rb=t.const(rom['b']),rd=t.const(rom['d']))
        elif kind==c.LOAD:new.update(phase=t.const(c.READ_LOAD),ra=t.const(rom['a']&0xFFFFFFFF))
        elif kind==c.META:new.update(phase=t.const(c.READ_META),ra=t.const(rom['a']&0xFFFFFFFF),rb=t.const(rom['b']),value=z)
        elif kind==c.HALT or not c.RESET_AGES[2]<=age<c.ACTIVE_ENDS[2]:new=None
        else:new['pc']=t.const(case['pc']+1)
    elif role=='meta_read':
        old.update(phase=t.const(c.READ_META),rd=t.const(at),rb=t.const(case['selector']),value=one)
        new=dict(old,phase=t.const(c.WAIT_META),rd=old['ra'],value=t.const(r.record(at)[c.STATIC[case['selector']]]))
    elif role in ('reflect_ready','reflect_value','fallback'):
        old['direction']=one;new_at=at
        if role=='reflect_value':old['phase']=t.const(c.WAIT_META);new=dict(old,phase=t.const(c.WRITE),direction=z)
        elif role=='reflect_ready':old.update(phase=t.const(c.READ_META),value=z);new=dict(old,value=one,direction=z)
        else:
            old.update(phase=t.const(c.READ_META),value=one,rd=t.const(case['query']),rb=t.const(case['selector']))
            new=dict(old,phase=t.const(c.WRITE),rd=old['ra'],value=t.const(c.fallback(case['query'],case['selector'])),direction=z)
    else:raise ValueError(role)
    def raw(pos,after=False):
        address=pos%f.Q;values={name:z for name,_ in f.SCHEMA}
        for d in f.STATIC_OFFSETS:
            for name,value in r.record((address+d)%f.Q).items():values[f'p{d+3}_{name}']=t.const(value)
        values.update(address=t.const(address),age=t.const(age+int(after)))
        for d in f.OFFSETS:
            logical=pos+d;prefix=f's{d+2}_'
            values[prefix+'data']=(new_data if after else data).get(logical,z)
            if after and new is not None and logical==new_at:
                values[prefix+'head']=one
                for name,value in new.items():values[prefix+name]=value
            elif not after and role!='quiet' and logical==at:
                values[prefix+'head']=one
                for name,value in old.items():values[prefix+name]=value
            if after and logical==at:
                for name,value in packet.items():values[prefix+name]=value
        return tuple(values[name] for name,_ in f.SCHEMA)
    return t,raw


def certify_case(case,description=None):
    desc=f.self_description() if description is None else description;validate(desc)
    t,raw=prepare(case);checked=0
    for position in range(case['at']-4,case['at']+5):
        inputs=tuple(word for j in f.NEIGHBORHOOD for word in raw(position+j))
        actual=t.expression(desc,inputs);expected=raw(position,after=True)
        for (name,_),a,b in zip(f.SCHEMA,actual,expected):
            if a!=b:raise AssertionError((case['name'],position-case['at'],name,t.nodes[a],t.nodes[b]))
        checked+=1
    return dict(name=case['name'],at=case['at'],age=case['age'],passed=True,full_raw_outputs=checked*f.FIELDS,symbolic_variables=sum(n[0]=='variable' for n in t.nodes),symbolic_terms=len(t.nodes))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();rows=[certify_case(case) for case in cases()]
    result=dict(passed=True,cases=rows,case_count=len(rows),complete_raw_output_words=sum(x['full_raw_outputs'] for x in rows),descriptor_sha256=f.self_description().digest(),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,scope='Full raw local event identities at stated actual ROM positions and clock phases, for arbitrary specified operand/stale-controller words and surrounding MEM Data; coherent zero-flag, zero-Signal, no-incoming-mail domain.',limitation='Not all ROM locations or clock phases, not a scan-duration theorem, not a whole-period or noisy simulation theorem. Expected motion/effects are specified independently of the full descriptor. Diagnostic only.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
