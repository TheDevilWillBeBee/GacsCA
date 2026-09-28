"""Complete word description of controller, transport and printed maintenance."""
from .wordcode import Builder
from . import word_rule as r


def build(*,healthy_domain=False):
    b=Builder(11*r.FIELDS);records={}
    for offset in range(-5,6):
        records[offset]={name:(offset+5)*r.FIELDS+i for i,(name,_) in enumerate(r.SCHEMA)}
    left,c,right=records[-1],records[0],records[1]
    zero,one=b.const(0),b.const(1)
    def eq(x,name,value):return b.eq(x[name],b.const(value))
    def condition(x,phase,field):return b.all(eq(x,'kind',r.MEM),eq(x,'phase',phase),b.eq(x['index'],x[field]))
    def waiting(x):return b.all(x['head'],b.not_(x['direction']),eq(x,'phase',r.FETCH),eq(x,'kind',r.WAIT),b.eq(x['index'],x['pc']),b.nonzero(x['rd']))
    def meta(x):
        result=zero
        for selector,name in enumerate(r.STATIC):result=b.select(eq(x,'rb',selector),x[name],result)
        return result
    def fallback(x):return b.select(eq(x,'rb',0),b.const(r.LOOP),b.select(eq(x,'rb',1),x['rd'],zero))
    def advanced(x):
        fetch=b.all(eq(x,'phase',r.FETCH),b.eq(x['index'],x['pc']))
        operations=b.any(*(eq(x,'kind',op) for op in r.ALU_KINDS))
        gate=b.band(fetch,operations)
        send,loop,load,metadata,wait,literal=(b.band(fetch,eq(x,'kind',k)) for k in (r.SEND,r.LOOP,r.LOAD,r.META,r.WAIT,r.LIT))
        a,bb,d,sent,loaded=(condition(x,p,name) for p,name in ((r.READ_A,'ra'),(r.READ_B,'rb'),(r.WRITE,'rd'),(r.TRANSMIT,'ra'),(r.READ_LOAD,'ra')))
        readmeta=b.all(eq(x,'phase',r.READ_META),b.nonzero(x['value']),b.eq(x['address'],x['rd']))
        done=b.any(d,sent,loaded,b.band(wait,eq(x,'rd',0)))
        result={name:x[name] for name in r.CONTROL[:-1]}
        result['ra']=b.select(b.any(gate,send,load,metadata),b.mask(x['a'],32),x['ra'])
        result['rb']=b.select(b.any(gate,send,metadata),x['b'],x['rb'])
        result['alu']=b.select(gate,b.mask(x['kind'],3),x['alu'])
        rd=b.select(b.any(gate,send,literal),x['d'],x['rd'])
        rd=b.select(loaded,x['data'],rd)
        rd=b.select(b.all(wait,b.nonzero(x['rd'])),b.add(x['rd'],b.const(-1)),rd)
        result['rd']=b.select(readmeta,x['ra'],rd)
        phase=x['phase']
        for predicate,value in ((gate,r.READ_A),(send,r.TRANSMIT),(load,r.READ_LOAD),(metadata,r.READ_META),(literal,r.WRITE),(a,r.READ_B),(bb,r.WRITE),(done,r.FETCH),(readmeta,r.WAIT_META)):
            phase=b.select(predicate,b.const(value),phase)
        result['phase']=phase
        result['pc']=b.select(loop,zero,b.select(done,b.mask(b.add(x['pc'],one),32),x['pc']))
        calculated=zero
        for opcode in r.ALU_KINDS:
            calculated=b.select(eq(x,'alu',opcode),b.op(opcode,x['value'],x['data']),calculated)
        value=b.select(bb,calculated,b.select(a,x['data'],x['value']))
        value=b.select(metadata,zero,value);value=b.select(literal,x['a'],value)
        result['value']=b.select(readmeta,meta(x),value)
        return result
    def reflected(x):
        scanning=eq(x,'phase',r.READ_META)
        missing=b.band(scanning,b.nonzero(x['value']))
        ready=b.band(scanning,b.not_(x['value']))
        result={name:x[name] for name in r.CONTROL[:-1]}
        result['phase']=b.select(b.any(missing,eq(x,'phase',r.WAIT_META)),b.const(r.WRITE),x['phase'])
        result['rd']=b.select(missing,x['ra'],x['rd'])
        result['value']=b.select(missing,fallback(x),b.select(ready,one,x['value']))
        return result
    from_left=b.all(left['head'],b.not_(left['direction']),b.not_(left['last']),b.not_(waiting(left)))
    from_right=b.all(right['head'],right['direction'],b.not_(right['first']))
    reflect=b.band(c['head'],b.select(c['direction'],c['first'],c['last']))
    hold=waiting(c);own=b.any(reflect,hold)
    lc,cc,reflection=advanced(left),advanced(c),reflected(c)
    out=dict(c);out['head']=b.any(from_left,from_right,own)
    for name in r.CONTROL[:-1]:
        value=b.select(from_right,right[name],zero)
        value=b.select(from_left,lc[name],value)
        out[name]=b.select(own,b.select(c['direction'],reflection[name],cc[name]),value)
    out['direction']=b.select(hold,zero,b.select(reflect,b.not_(c['direction']),b.all(b.not_(from_left),from_right)))
    executing=b.all(c['head'],b.not_(c['direction']))
    sending=b.band(executing,condition(c,r.TRANSMIT,'ra'))
    data=c['data']
    for channel,source,edge in (('lp',right,eq(right,'address',0)),('rp',left,eq(left,'address',r.Q-1))):
        count=source[channel+'_remaining']
        valid=b.all(source[channel+'_valid'],b.not_(b.all(edge,b.not_(count))))
        remaining=b.select(b.all(edge,b.nonzero(count)),b.add(count,b.const(-1)),count)
        hit=b.all(valid,b.not_(remaining),eq(c,'kind',r.MEM),b.eq(c['index'],source[channel+'_target']))
        moving=b.all(valid,b.not_(hit));data=b.select(hit,source[channel+'_data'],data)
        direction=b.band(c['rd'],one)
        emit=b.band(sending,direction if channel=='lp' else b.not_(direction))
        for suffix,value,fresh in (('target',source[channel+'_target'],b.mask(c['rb'],32)),('data',source[channel+'_data'],c['data']),('remaining',remaining,b.mask(b.shr(c['rd'],one),3)),('valid',one,one)):
            out[channel+'_'+suffix]=b.select(emit,fresh,b.select(moving,value,zero))
    out['data']=b.select(b.band(executing,condition(c,r.WRITE,'rd')),c['value'],data)

    if healthy_domain:
        # Exact specialization only when Address is canonical, Age is uniform,
        # and all four structural/workspace flags are zero. It is not the rule
        # description used by the self-simulator; build() above remains complete.
        out['address']=c['address'];out['age']=b.mask(b.add(c['age'],one),30)
        for name in ('f1','f2','wf1','wf2'):out[name]=zero
        full=b.finish(tuple(out[name] for name,_ in r.SCHEMA))
        from .wordcode import Program,LIT
        def remap(w):
            if w<full.inputs:
                if not 4*r.FIELDS<=w<7*r.FIELDS:raise AssertionError('nonlocal healthy specialization')
                return w-4*r.FIELDS
            return w-full.inputs+3*r.FIELDS
        operations=tuple((op,a,bb) if op==LIT else (op,remap(a),remap(bb)) for op,a,bb in full.operations)
        return Program(3*r.FIELDS,operations,tuple(map(remap,full.outputs)))

    # Full printed Gray local-structure rule: all eleven raw records are inputs.
    def majority(values,default):
        result,exists=default,zero
        for candidate in values:
            valid=b.count([b.eq(candidate,other) for other in values],3)
            result=b.select(valid,candidate,result);exists=b.bor(exists,valid)
        return result,exists
    def add_address(value,delta):return b.mask(b.add(value,b.const(delta)),23)
    R,L=range(1,6),range(-1,-6,-1)
    adjusted={j:add_address(records[j]['address'],-j) for j in (*L,*R)}
    v,exists=majority([adjusted[j] for j in R],c['address'])
    inside={0:exists}
    for j in R:inside[j]=b.band(exists,b.lt(v,b.const(r.Q-j)))
    for j in L:inside[j]=b.band(exists,b.not_(b.lt(v,b.const(-j))))
    age_r,age_exists=majority([records[j]['age'] for j in R],c['age'])
    age_l,_=majority([records[j]['age'] for j in L],c['age'])
    incons=b.any(b.not_(exists),b.not_(age_exists),
        b.count([b.all(inside[j],b.not_(b.eq(records[j]['address'],add_address(v,j)))) for j in L],3),
        b.count([b.all(inside[j],b.not_(b.eq(records[j]['age'],age_r))) for j in L],3))
    wf1=b.count([b.band(inside[j],records[j]['wf1']) for j in range(-5,6)],3)
    flags=[b.band(inside[j],records[j]['f1']) for j in R]
    f1=b.any(incons,wf1,b.count(flags,3),b.band(c['f1'],b.count(flags,2)))
    d3=b.all(b.not_(exists),b.eq(b.mask(b.add(age_l,one),4),zero))
    d4=b.count([b.band(inside[j],records[j]['wf2']) for j in range(-5,6)],3)
    left_flags=[records[j]['f2'] for j in L]
    on=b.any(b.count([b.band(inside[j],records[j]['f2']) for j in L],4),b.band(f1,b.count(left_flags,4)),d3,d4)
    erase=b.any(b.all(b.not_(f1),b.all(*(b.any(b.not_(inside[j]),records[j]['f2']) for j in L))),b.all(f1,b.not_(b.any(*left_flags))))
    f2=b.select(c['f2'],b.any(d3,d4,b.not_(erase)),on)
    addr_l,_=majority([adjusted[j] for j in L],c['address'])
    vote_right=b.all(exists,b.any(b.not_(f1),f2))
    out['address']=b.select(vote_right,v,addr_l)
    out['age']=b.mask(b.add(b.select(vote_right,age_r,age_l),one),30)
    out['f1'],out['f2']=f1,f2
    clear=b.all(f1,b.not_(b.eq(out['address'],c['address'])))
    for name,_ in r.SCHEMA:
        if name.startswith(('lp_','rp_')):out[name]=b.select(f1,zero,out[name])
    for name in ('data','head',*r.CONTROL,'wf1','wf2'):out[name]=b.select(clear,zero,out[name])
    return b.finish(tuple(out[name] for name,_ in r.SCHEMA))
