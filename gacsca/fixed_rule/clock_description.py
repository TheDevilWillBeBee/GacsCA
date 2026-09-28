"""Complete description, including clocked memory operations and entry selection."""
from . import clock_rule as r,word_description
from .wordcode import Builder,Program,LIT


def build(*,healthy_domain=False):
    b=Builder(11*r.FIELDS)
    records={j:{n:(j+5)*r.FIELDS+i for i,(n,_) in enumerate(r.SCHEMA)} for j in range(-5,6)}
    c=records[0];zero,one=b.const(0),b.const(1)
    def eq(x,y):return b.eq(x,b.const(y))
    old=word_description.build(healthy_domain=healthy_domain)
    mapping=[]
    for j in (range(-1,2) if healthy_domain else range(-5,6)):
        row=dict(records[j])
        halt=b.all(row['head'],b.not_(row['direction']),eq(row['phase'],r.FETCH),eq(row['kind'],r.HALT),b.eq(row['index'],row['pc']))
        row['head']=b.select(halt,zero,row['head'])
        mapping.extend(row[n] for n,_ in r.SCHEMA)
    for op,a,d in old.operations:mapping.append(b.const(a) if op==LIT else b.op(op,mapping[a],mapping[d]))
    out={n:mapping[index] for (n,_),index in zip(r.SCHEMA,old.outputs)}
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
    boot=b.all(any_reset,c['first']);out['head']=b.select(boot,one,out['head']);out['pc']=b.select(boot,entry,out['pc'])
    extra=eq(c['age'],r.VOTE_AGES[0])
    for name in ('head',*r.CONTROL):out[name]=b.select(extra,zero,out[name])
    extra_boot=b.band(extra,c['first']);out['head']=b.select(extra_boot,one,out['head']);out['pc']=b.select(extra_boot,c['d'],out['pc'])
    vote=b.all(eq(c['kind'],r.MEM),b.not_(c['first']),b.nonzero(b.band(c['a'],b.const(r.VOTE))),b.any(*(eq(c['age'],age) for age in r.VOTE_AGES)))
    a,d,e=(records[j]['data'] for j in (-1,1,2))
    majority=b.bor(b.bor(b.band(a,d),b.band(a,e)),b.band(d,e))
    out['data']=b.select(vote,majority,out['data'])
    commit=b.all(eq(c['kind'],r.MEM),b.not_(c['first']),b.nonzero(b.band(c['a'],b.const(r.INFO))),eq(c['age'],r.U-1))
    out['data']=b.select(commit,records[1]['data'],out['data'])
    window=b.all(b.not_(b.lt(out['age'],b.const(96*r.Q))),b.lt(out['age'],b.const(98*r.Q)))
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
