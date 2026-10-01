"""Complete description of stream28_holder_rule, including every procedure/Wf copy."""
from .. import stream28_dual_holder_rule20 as r,stream28_dual_core20 as c,stream28_dual_core_word_description20
from ..wordcode_and import Builder,Program,LIT
from ..word_prune import prune
from . import clock_description


def build():
    b=Builder(15*r.FIELDS);rows={j:{n:(j+7)*r.FIELDS+i for i,(n,_) in enumerate(r.SCHEMA)} for j in r.NEIGHBORHOOD};own=rows[0]
    zero,one=b.const(0),b.const(1)
    def eq(x,value):return b.eq(x,b.const(value))
    def add_address(x,delta):return b.mask(b.add(x,b.const(delta)),(r.Q-1).bit_length())
    def embed(program,inputs):
        assert len(inputs)==program.inputs
        values=list(inputs)
        for op,a,d in program.operations:values.append(b.const(a) if op==LIT else b.op(op,values[a],values[d]))
        return tuple(values[w] for w in program.outputs)
    old=stream28_dual_core_word_description20.build()
    names=('address','age','f1','f2');maintenance=prune(Program(old.inputs,old.operations,tuple(old.outputs[c.COL[n]] for n in names)))
    geometry={}
    for offset in r.OFFSETS:
        data=[]
        for j in range(-5,6):
            row=rows[offset+j]
            for name,_ in c.SCHEMA:data.append(row[name] if name in ('address','age','f1','f2') else row['w2_'+name] if name in ('wf1','wf2') else zero)
        geometry[offset]=dict(zip(names,embed(maintenance,data)))
    def majority(values,width):
        if width==1:return b.count(values,3)
        a,d,e,f,g=values
        triple=b.band(b.band(a,d),e)
        pairs=b.bor(b.bor(b.band(a,d),b.band(a,e)),b.band(d,e))
        any3=b.bor(b.bor(a,d),e)
        return b.bor(b.bor(triple,b.band(pairs,b.bor(f,g))),b.band(any3,b.band(f,g)))
    corrected={j:{name:majority([rows[j+e][f's{2-e}_{name}'] for e in r.OFFSETS],width) for name,width in r.PROCEDURE} for j in range(-4,5)}
    procedure=clock_description.build(healthy_domain=True)
    out=dict(own);out.update(geometry[0])
    for offset in r.OFFSETS:
        data=[]
        for j in range(-2,3):
            for name,_ in c.SCHEMA:
                if j==2 and name=='data':value=corrected[offset+j][name]
                elif abs(j)>1:value=zero
                elif name in c.STATIC:value=own[f'p{offset+j+3}_{name}']
                elif name in corrected[0]:value=corrected[offset+j][name]
                elif name=='address':value=add_address(own['address'],offset+j)
                elif name=='age':value=own['age']
                else:value=zero
                data.append(value)
        result=embed(procedure,data)
        for name,_ in r.PROCEDURE:out[f's{offset+2}_{name}']=result[c.COL[name]]
    signal_votes={j:b.count([b.band(b.shr(rows[j+e]['signal'],b.const(2-e)),one) for e in r.OFFSETS],3) for j in range(-5,6)}
    signal=zero;capture=eq(out['age'],c.CAPTURE_AGE);data=b.band(corrected[0]['data'],one)
    for d in r.OFFSETS:
        at=b.any(*(eq(out['address'],target-d) for target in (3,r.Q-3)))
        bit=b.select(b.all(capture,at),data,signal_votes[d])
        for _ in range(d+2):bit=b.add(bit,bit)
        signal=b.bor(signal,bit)
    out['signal']=signal
    for d in r.OFFSETS:
        g=geometry[d];window=b.all(b.not_(b.lt(g['age'],b.const(r.WF_START))),b.lt(g['age'],b.const(r.WF_END)))
        out[f'w{d+2}_wf1']=b.all(window,b.any(*(b.all(eq(g['address'],a),signal_votes[d+r.Q-3-a]) for a in range(r.Q-5,r.Q))))
        out[f'w{d+2}_wf2']=b.all(window,b.not_(g['f1']),b.any(*(b.all(eq(g['address'],a),signal_votes[d+3-a]) for a in range(5))))
    clear=b.all(out['f1'],b.not_(b.eq(out['address'],own['address'])))
    for d in r.OFFSETS:
        for name,_ in r.PROCEDURE:
            key=f's{d+2}_{name}';out[key]=b.select(out['f1'] if name.startswith(('lp_','rp_')) else clear,zero,out[key])
        for name in ('wf1','wf2'):
            key=f'w{d+2}_{name}';out[key]=b.select(clear,zero,out[key])
    out['signal']=b.select(clear,zero,out['signal'])
    return prune(b.finish(tuple(out[name] for name,_ in r.SCHEMA)))
