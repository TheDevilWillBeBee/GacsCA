"""Quantified full-descriptor geometry identity under arbitrary flags and Wf."""
import json
from pathlib import Path
import time
from gacsca.fixed_rule import compact16_holder_rule as f
from gacsca.fixed_rule.wordcode import MASK
from experiments.fixed_rule.prove_compact16_holder_two_site_geometry import geometry,BoundedBDD
from experiments.fixed_rule.run_compact16_holder_streamed_depth2 import sha


def prove(*,broken=False):
    program,support=geometry(f.self_description());aw=f.Q.bit_length()-1;tw=f.U.bit_length()-1
    fields=('f1','f2','w2_wf1','w2_wf2');labels=[('address',i) for i in range(aw)]+[('age',i) for i in range(tw)]+[(j,name) for name in fields for j in range(-5,6)]
    b=BoundedBDD(len(labels));v={label:b.variable(i) for i,label in enumerate(labels)};zero=b.const(0)
    address=tuple(v['address',i] for i in range(aw))+(0,)*(64-aw);age=tuple(v['age',i] for i in range(tw))+(0,)*(64-tw)
    inputs=[]
    for j in f.NEIGHBORHOOD:
        row={name:zero for name,_ in f.SCHEMA};row['address']=b.add(address,b.const(j&MASK))[:aw]+(0,)*(64-aw);row['age']=age
        if -5<=j<=5:
            for name in fields:row[name]=(v[j,name],)+(0,)*63
        inputs.extend(row[name] for name,_ in f.SCHEMA)
    def any_(xs):
        result=0
        for x in xs:result=b.or_(result,x)
        return result
    def count(xs,k):
        dp=[1]+[0]*k
        for x in xs:
            for i in range(k,0,-1):dp[i]=b.or_(dp[i],b.and_(x,dp[i-1]))
        return dp[k]
    inside={j:b.inv(b.less(address,b.const(-j))) if j<0 else b.less(address,b.const(f.Q-j)) for j in range(-5,6)}
    right=[b.and_(inside[j],v[j,'f1']) for j in range(1,6)]
    wf1=count([b.and_(inside[j],v[j,'w2_wf1']) for j in range(-5,6)],3)
    wf2=count([b.and_(inside[j],v[j,'w2_wf2']) for j in range(-5,6)],3)
    first=any_((wf1,count(right,2 if broken else 3),b.and_(v[0,'f1'],count(right,2))))
    left=[b.and_(inside[j],v[j,'f2']) for j in range(-5,0)];left_raw=[v[j,'f2'] for j in range(-5,0)]
    on=any_((count(left,4),b.and_(first,count(left_raw,4)),wf2))
    erase=b.or_(b.and_(b.inv(first),b.inv(count(left,2))),b.and_(first,b.inv(any_(left_raw))))
    second=b.ite(v[0,'f2'],b.or_(wf2,b.inv(erase)),on)
    wanted=(address,b.add(age,b.const(1))[:tw]+(0,)*(64-tw),(first,)+(0,)*63,(second,)+(0,)*63)
    try:
        actual=b.evaluate(program,tuple(inputs))
        for name,got,expected in zip(('address','age','f1','f2'),actual,wanted):
            for bit,(x,y) in enumerate(zip(got,expected)):
                if x!=y:raise AssertionError(dict(output=name,bit=bit,witness=b.witness(b.xor(x,y))))
        return dict(independent_bits=len(labels),BDD_nodes=len(b.nodes),operations=len(program.operations),checked_outputs=['address','age','f1','f2'],support=support)
    finally:b.binary.cache_clear()


def main():
    output=Path('figs/fixed_rule/compact16_holder_canonical_geometry_v1.json')
    if output.exists():raise FileExistsError(output)
    t=time.perf_counter();proof=prove()
    try:prove(broken=True)
    except AssertionError as error:mutation=str(error)
    else:raise AssertionError('wrong flag threshold escaped')
    result=dict(passed=True,**proof,descriptor_sha256=f.self_description().digest(),all_addresses=f.Q,all_ages=f.U,
                independently_arbitrary_primary_flags_and_Wf=44,unused_raw_fields_unrestricted=True,wrong_threshold_rejected=mutation,
                seconds=time.perf_counter()-t,source_sha256={str(Path(__file__)):sha(__file__)},
                theorem='Canonical Address and uniform legal Age are invariant under complete G for arbitrary typed remaining fields. Exact simplified Flag1/Flag2 equations equal the full descriptor for every such neighborhood.',
                limitation='Geometry factor only; procedure, Signal and Wf factorization also requires the documented algebra and backend parity checks.')
    with output.open('x') as out:out.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


if __name__=='__main__':main()
