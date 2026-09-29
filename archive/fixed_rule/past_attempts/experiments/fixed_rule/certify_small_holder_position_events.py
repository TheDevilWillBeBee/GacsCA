"""Position-independent full raw event identities under canonical geometry.

Both the base physical Address and local metadata are symbolic. This diagnostic
is not a physical executor and leaves full scan/period composition unproved.
"""
import argparse,hashlib,json,resource,time
from pathlib import Path
from gacsca.fixed_rule import small_holder_rule as f,small_holder_core as c,small_holder_program as p
from gacsca.fixed_rule.wordcode import NAND,ADD,SHR,EQ,LT,LIT,MASK,arithmetic
from experiments.fixed_rule.certify_small_holder_local_events import Algebra
from experiments.fixed_rule.prove_small_holder_boundary import validate


class Modular(Algebra):
    def width(self,x):
        node=self.nodes[x]
        if node[0]=='const':return node[1].bit_length()
        if node[0]=='variable':return node[2]
        if node[0]=='modadd':return node[3]
        if node[0]=='op' and node[1] in (EQ,LT):return 1
        return 64
    def modular_add(self,x,delta,width):
        mask=(1<<width)-1;delta&=mask;node=self.nodes[x]
        if node[0]=='const':return self.const((node[1]+delta)&mask)
        if node[0]=='modadd' and node[3]==width:
            x,delta=node[1],(node[2]+delta)&mask
        if delta==0 and self.width(x)<=width:return x
        return self.intern(('modadd',x,delta,width))
    def masked(self,x,width):
        node=self.nodes[x]
        if self.width(x)<=width:return x
        if node[0]=='op' and node[1]==ADD:
            a,b=node[2:];av,bv=self.value(a),self.value(b)
            if av is not None:return self.modular_add(b,av,width)
            if bv is not None:return self.modular_add(a,bv,width)
        return self.modular_add(x,0,width)
    def inv(self,x):
        node=self.nodes[x]
        if node[0]=='op' and node[1]==NAND:
            a,b=node[2:];av,bv=self.value(a),self.value(b)
            for value,term in ((av,b),(bv,a)):
                if value is not None and value<MASK and value&(value+1)==0:
                    return self.masked(term,(value+1).bit_length()-1)
        return super().inv(x)
    def op(self,kind,a,b):
        # A nonzero cyclic shift has no fixed point on a width-bounded word.
        if kind==EQ:
            for x,y in ((a,b),(b,a)):
                node=self.nodes[y]
                if node[0]=='modadd' and node[1]==x and node[2]!=0 and self.width(x)<=node[3]:return self.const(0)
        return super().op(kind,a,b)


def cases():
    out=[dict(name='quiet',role='quiet')]
    out.extend(dict(name=f'read_b_{kind}',role='read_b',opcode=kind) for kind in c.ALU_KINDS)
    out.extend(dict(name=role,role=role) for role in ('read_a','write','load','left_flight'))
    out.extend(dict(name=f'send_{d}_{h}',role='send',direction=d,hops=h) for d in (0,1) for h in range(8))
    out.extend(dict(name=f'meta_hit_{s}',role='meta_hit',selector=s) for s in range(7))
    out.extend(dict(name=f'right_flight_{phase}',role='right_flight',phase=phase) for phase in range(8))
    out.extend(dict(name=f'right_reflect_{phase}',role='right_reflect',phase=phase) for phase in range(8))
    return tuple(out)


def prepare(event):
    t=Modular(p.base_rom());zero=t.const(0);one=t.const(1);A=t.variable('base_address',15);age=c.VOTE_AGES[0]+10;role=event['role']
    metadata={i:{name:t.variable(f'meta_{i}_{name}',dict(c.SCHEMA)[name]) for name in c.STATIC} for i in range(-16,17)}
    data={i:t.variable(f'data_{i}',64) for i in range(-16,17)}
    ctrl={name:t.variable('old_'+name,dict(c.SCHEMA)[name]) for name in c.CONTROL}
    ctrl['direction']=zero;old=dict(ctrl);new=None;new_at=1;next_data=dict(data);packet={}
    # A right-moving ordinary event requires no right endpoint at its source.
    metadata[0]['last']=zero
    if role in ('read_b','read_a','write','load','send'):metadata[0]['kind']=t.const(c.MEM)
    index=metadata[0]['index']
    if role=='quiet':old={name:zero for name in c.CONTROL}
    elif role=='read_b':
        old.update(phase=t.const(c.READ_B),rb=index,alu=t.const(event['opcode']))
        new=dict(old,phase=t.const(c.WRITE),value=t.op(event['opcode'],old['value'],data[0]))
    elif role=='read_a':old.update(phase=t.const(c.READ_A),ra=index);new=dict(old,phase=t.const(c.READ_B),value=data[0])
    elif role=='write':
        old.update(phase=t.const(c.WRITE),rd=index);new=dict(old,phase=zero,pc=t.modular_add(old['pc'],1,32));next_data[0]=old['value']
    elif role=='load':old.update(phase=t.const(c.READ_LOAD),ra=index);new=dict(old,phase=zero,rd=data[0],pc=t.modular_add(old['pc'],1,32))
    elif role=='send':
        old.update(phase=t.const(c.TRANSMIT),ra=index,rd=t.const(2*event['hops']+event['direction']))
        new=dict(old,phase=zero,pc=t.modular_add(old['pc'],1,32));track='lp' if event['direction'] else 'rp'
        packet={track+'_target':t.mask(old['rb'],32),track+'_data':data[0],track+'_remaining':t.const(event['hops']),track+'_valid':one}
    elif role=='meta_hit':
        old.update(phase=t.const(c.READ_META),rd=A,rb=t.const(event['selector']),value=one)
        new=dict(old,phase=t.const(c.WAIT_META),rd=old['ra'],value=metadata[0][c.STATIC[event['selector']]])
    elif role=='left_flight':
        metadata[0]['first']=zero;old['direction']=one;new=dict(old);new_at=-1
    elif role in ('right_flight','right_reflect'):
        phase=event['phase'];old['phase']=t.const(phase)
        if phase==c.FETCH:old['pc']=t.modular_add(index,1,32)
        elif phase in (c.READ_A,c.TRANSMIT,c.READ_LOAD):old['ra']=t.modular_add(index,1,32)
        elif phase==c.READ_B:old['rb']=t.modular_add(index,1,32)
        elif phase==c.WRITE:old['rd']=t.modular_add(index,1,32)
        elif phase==c.READ_META:old.update(rd=t.modular_add(A,1,15),value=one)
        new=dict(old)
        if role=='right_reflect':metadata[0]['last']=one;new['direction']=one;new_at=0
    else:raise ValueError(role)
    def raw(pos,after=False):
        values={name:zero for name,_ in f.SCHEMA}
        for d in f.STATIC_OFFSETS:
            for name,value in metadata[pos+d].items():values[f'p{d+3}_{name}']=value
        values.update(address=t.modular_add(A,pos,15),age=t.const(age+int(after)))
        for d in f.OFFSETS:
            site=pos+d;prefix=f's{d+2}_';values[prefix+'data']=(next_data if after else data)[site]
            if after and new is not None and site==new_at:
                values[prefix+'head']=one
                for name,value in new.items():values[prefix+name]=value
            elif not after and role!='quiet' and site==0:
                values[prefix+'head']=one
                for name,value in old.items():values[prefix+name]=value
            if after and site==0:
                for name,value in packet.items():values[prefix+name]=value
        return tuple(values[name] for name,_ in f.SCHEMA)
    return t,raw


def certify_case(event,description=None):
    desc=f.self_description() if description is None else description;validate(desc);t,raw=prepare(event)
    for pos in range(-4,5):
        actual=t.expression(desc,tuple(w for j in f.NEIGHBORHOOD for w in raw(pos+j)))
        expected=raw(pos,after=True)
        for (name,_),a,b in zip(f.SCHEMA,actual,expected):
            if a!=b:raise AssertionError((event['name'],pos,name,t.nodes[a],t.nodes[b]))
    return dict(name=event['name'],passed=True,all_base_addresses=f.Q,full_raw_outputs=9*f.FIELDS,symbolic_variables=sum(x[0]=='variable' for x in t.nodes),symbolic_terms=len(t.nodes))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();rows=[certify_case(event) for event in cases()]
    result=dict(passed=True,cases=rows,case_count=len(rows),complete_raw_output_words=sum(x['full_raw_outputs'] for x in rows),all_base_addresses=f.Q,arbitrary_surrounding_static_and_Data_words=True,event_age=c.VOTE_AGES[0]+10,descriptor_sha256=f.self_description().digest(),source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,scope='Position-independent full raw event identities with coherent procedure fields and canonical geometry, arbitrary surrounding static/Data and specified stale control words; structural hypotheses are stated by prepare().',limitation='One stated active clock value, zero flags/Signal/Wf and no incoming mail. Generic non-hit flights use explicit distinct-operand witnesses, not yet all unequal operands. No whole scan/period or noisy simulation theorem; diagnostic only.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
