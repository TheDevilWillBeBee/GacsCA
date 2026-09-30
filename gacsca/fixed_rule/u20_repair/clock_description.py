"""Complete description, including clocked memory operations and entry selection."""
from .. import stream28_dual_core20 as r,stream28_dual_core_word_description20 as word_description
from ..wordcode_and import Builder,Program,LIT


def build(*,healthy_domain=False):
    b=Builder(11*r.FIELDS)
    records={j:{n:(j+5)*r.FIELDS+i for i,(n,_) in enumerate(r.SCHEMA)} for j in range(-5,6)}
    c=records[0];zero,one=b.const(0),b.const(1)
    def eq(x,y):return b.eq(x,b.const(y))
    old=word_description.build(healthy_domain=healthy_domain)
    mapping=[]
    for j in (range(-1,2) if healthy_domain else range(-5,6)):
        row=dict(records[j])
        halt=b.all(row['head'],b.not_(row['direction']),eq(row['phase'],r.FETCH),b.any(eq(row['kind'],r.HALT),b.all(eq(row['kind'],r.IF_THIRD),b.not_(b.all(b.not_(b.lt(row['age'],b.const(r.RESET_AGES[2]))),b.lt(row['age'],b.const(r.ACTIVE_ENDS[2])))))),b.eq(row['index'],row['pc']))
        row['head']=b.select(halt,zero,row['head'])
        mapping.extend(row[n] for n,_ in r.SCHEMA)
    for op,a,d in old.operations:mapping.append(b.const(a) if op==LIT else b.op(op,mapping[a],mapping[d]))
    out={n:mapping[index] for (n,_),index in zip(r.SCHEMA,old.outputs)}
    stages=[b.all(b.not_(b.lt(c['age'],b.const(start))),
                  b.lt(c['age'],b.const(start+r.STREAM_FRAME)))
            for start in r.RESET_AGES[:3]]
    stream=b.any(*stages)
    tick=zero;tag=zero
    for stage,start in enumerate(r.RESET_AGES[:3]):
        elapsed=b.add(c['age'],b.const(-start))
        tick=b.select(stages[stage],elapsed,tick)
        tag=b.select(stages[stage],b.const(r.STREAM_TAG_MARK+(stage<<r.STREAM_TAG_SHIFT)),tag)
    mem=eq(c['kind'],r.MEM)
    field_code=b.shr(c['b'],b.const(r.STREAM_FIELD_SHIFT))
    field=b.add(field_code,b.const(-1))
    source=b.all(stream,mem,b.nonzero(field_code),
                 b.lt(field_code,b.const(r.STREAM_FIELDS+1)),
                 b.nonzero(tick),b.lt(tick,b.const(r.Q+1)))
    mask=b.mask(c['b'],15)
    emitted={'lp':{'target':zero,'data':zero,'remaining':zero,'valid':zero},
             'rp':{'target':zero,'data':zero,'remaining':zero,'valid':zero}}
    right_wire=b.mask(b.add(c['address'],b.add(b.inv(tick),b.const(2))),13)
    left_wire=b.mask(b.add(c['address'],b.add(tick,b.const(-1))),13)
    matches={'lp':zero,'rp':zero}
    hop_counts={'lp':zero,'rp':zero}
    for index in range(15):
        offset=index-7
        wire=b.add(b.const(index*r.STREAM_FIELDS),field)
        lane='rp' if offset<0 else 'lp'
        candidate=right_wire if offset<0 else left_wire
        selected=b.all(source,b.nonzero(b.band(mask,b.const(1<<index))),
                       b.eq(candidate,wire))
        matches[lane]=b.bor(matches[lane],selected)
        hop_counts[lane]=b.bor(hop_counts[lane],b.select(selected,b.const(abs(offset)),zero))
    for lane,candidate in (('rp',right_wire),('lp',left_wire)):
        emitted[lane]=dict(target=b.select(matches[lane],candidate,zero),
                           data=b.select(matches[lane],c['data'],zero),
                           remaining=hop_counts[lane],valid=matches[lane])
    hits={}
    incoming={}
    for prefix,neighbor,edge in (('rp',records[-1],b.all(eq(records[-1]['address'],r.Q-1),eq(c['address'],0))),
                                 ('lp',records[1],b.all(eq(records[1]['address'],0),eq(c['address'],r.Q-1)))):
        valid=neighbor[prefix+'_valid']
        old_hops=neighbor[prefix+'_remaining']
        decrement=b.all(valid,edge,b.nonzero(old_hops))
        hops=b.select(decrement,b.add(old_hops,b.const(-1)),old_hops)
        hit=b.all(valid,b.not_(hops),mem,b.eq(c['d'],b.add(tag,neighbor[prefix+'_target'])))
        hits[prefix]=hit
        moving=b.all(valid,b.not_(hit))
        incoming[prefix]={}
        for suffix,value in (('target',neighbor[prefix+'_target']),
                             ('data',neighbor[prefix+'_data']),('remaining',hops),('valid',one)):
            incoming[prefix][suffix]=b.select(moving,value,emitted[prefix][suffix])
            out[prefix+'_'+suffix]=b.select(stream,incoming[prefix][suffix],out[prefix+'_'+suffix])
    stream_data=b.select(hits['rp'],records[-1]['rp_data'],
                         b.select(hits['lp'],records[1]['lp_data'],c['data']))
    out['data']=b.select(stream,stream_data,out['data'])
    active=b.any(*(b.all(b.not_(b.lt(c['age'],b.const(lo))),b.lt(c['age'],b.const(hi))) for lo,hi in zip(r.RESET_AGES,r.ACTIVE_ENDS)))
    for name in r.SIMULATION:out[name]=b.select(active,out[name],c[name])
    reset=[eq(c['age'],age) for age in r.RESET_AGES];any_reset=b.any(*reset)
    entry=zero
    for stage,predicate in enumerate(reset):
        value=b.mask(b.shr(c['a'] if stage<2 else c['b'],b.const(32*(stage if stage<2 else stage-2))),32) if stage<4 else c['d']
        entry=b.select(predicate,value,entry)
    for name in r.SIMULATION:
        if name!='data':out[name]=b.select(any_reset,zero,out[name])
    marked=b.any(*(b.all(predicate,b.band(b.shr(c['a'],b.const(stage)),one)) for stage,predicate in enumerate(reset)))
    erase=b.all(any_reset,b.any(c['first'],b.all(eq(c['kind'],r.MEM),marked)))
    out['data']=b.select(erase,zero,out['data'])
    boot=b.all(b.any(*reset[3:]),c['first']);out['head']=b.select(boot,one,out['head']);out['pc']=b.select(boot,entry,out['pc'])
    extra=eq(c['age'],r.VOTE_AGES[0])
    for name in ('head',*r.CONTROL):out[name]=b.select(extra,zero,out[name])
    extra_boot=b.band(extra,c['first']);out['head']=b.select(extra_boot,one,out['head']);out['pc']=b.select(extra_boot,c['d'],out['pc'])
    vote=b.all(eq(c['kind'],r.MEM),b.not_(c['first']),b.nonzero(b.band(c['a'],b.const(r.VOTE))),b.any(*(eq(c['age'],age) for age in r.VOTE_AGES)))
    a,bb,d=(records[j]['data'] for j in (-1,1,2))
    majority=b.bor(b.bor(b.band(a,bb),b.band(a,d)),b.band(bb,d))
    out['data']=b.select(vote,majority,out['data'])
    commit=b.all(eq(c['kind'],r.MEM),b.not_(c['first']),b.nonzero(b.band(c['a'],b.const(r.INFO))),eq(c['age'],r.U-1))
    out['data']=b.select(commit,records[1]['data'],out['data'])
    window=b.all(b.not_(b.lt(out['age'],b.const(r.WF_START))),b.lt(out['age'],b.const(r.WF_END)))
    for name in ('wf1','wf2'):out[name]=zero if healthy_domain else b.select(window,out[name],zero)
    clear=b.all(out['f1'],b.not_(b.eq(out['address'],c['address'])))
    for name,_ in r.SCHEMA:
        if name.startswith(('lp_','rp_')):out[name]=b.select(out['f1'],zero,out[name])
    for name in ('data','head',*r.CONTROL,'wf1','wf2'):out[name]=b.select(clear,zero,out[name])
    full=b.finish(tuple(out[n] for n,_ in r.SCHEMA))
    if not healthy_domain:return full
    def remap(w):
        if w<full.inputs:
            if not 3*r.FIELDS<=w<8*r.FIELDS:raise AssertionError('outside healthy radius two')
            return w-3*r.FIELDS
        return w-full.inputs+5*r.FIELDS
    return Program(5*r.FIELDS,tuple((op,a,d) if op==LIT else (op,remap(a),remap(d)) for op,a,d in full.operations),tuple(map(remap,full.outputs)))
