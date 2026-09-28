"""Full-descriptor certificate for arbitrary canonical flags and coherent Signals."""
import argparse,hashlib,json,time
from pathlib import Path
from gacsca.fixed_rule.word_bdd import BDD
from gacsca.fixed_rule.wordcode import Program
from gacsca.fixed_rule.word_prune import prune
from gacsca.fixed_rule import retimed_holder_rule as f


def prove_case(mode):
    width=f.Q.bit_length()-1;b=BDD(width+36)
    address=tuple(b.variable(i) for i in range(width))+(0,)*(64-width)
    flag1={i:b.variable(width+i+7) for i in range(-7,8)}
    flag2={i:b.variable(width+15+i+7) for i in range(-7,8)}
    signals={side:tuple(b.variable(width+30+3*side+i) for i in range(3)) for side in (0,1)}
    zero=b.const(0)
    def pos(d):return b.add(address,b.const(d&((1<<64)-1)))[:width]+(0,)*(64-width)
    def lt(a,v):return b.less(a,b.const(v))
    def eq(a,v):return b.arithmetic(4,a,b.const(v))[0]
    def sigbit(d,side):
        if d<0:return b.ite(lt(address,-d),signals[side][0],signals[side][1])
        if d>0:return b.ite(b.inv(lt(address,f.Q-d)),signals[side][2],signals[side][1])
        return signals[side][1]
    def signal(d):
        a=pos(d);bits=[]
        for k in range(5):bits.append(b.or_(b.and_(eq(a,5-k),sigbit(d,0)),b.and_(eq(a,f.Q-1-k),sigbit(d,1))))
        return tuple(bits)+(0,)*59
    forced=mode in ('forced','cutoff');next_forced=mode in ('entry','forced')
    age={'entry':f.WF_START-1,'forced':f.WF_START+10,'cutoff':f.WF_END-1,'erase':f.WF_END+10}[mode]
    def inside(d,j):
        a=pos(d)
        return b.inv(lt(a,-j)) if j<0 else lt(a,f.Q-j) if j>0 else 1
    def threshold(bits,k):
        counts=[1]+[0]*k
        for bit in bits:
            for j in range(k,0,-1):counts[j]=b.or_(counts[j],b.and_(counts[j-1],bit))
        return counts[k]
    def wf(d,kind):
        a=pos(d)
        if not forced:return 0
        if kind==1:return b.and_(b.inv(lt(a,f.Q-5)),sigbit(d,1))
        return b.and_(b.and_(lt(a,5),sigbit(d,0)),b.inv(flag1[d]))
    def new_f1(d):
        right=[b.and_(inside(d,j),flag1[d+j]) for j in range(1,6)]
        forcing=[b.and_(inside(d,j),wf(d+j,1)) for j in range(-5,6)]
        return b.or_(threshold(forcing,3),b.or_(threshold(right,3),b.and_(flag1[d],threshold(right,2))))
    nf=new_f1(0);left=[flag2[-j] for j in range(1,6)];local=[b.and_(inside(0,-j),flag2[-j]) for j in range(1,6)]
    force=threshold([b.and_(inside(0,j),wf(j,2)) for j in range(-5,6)],3)
    born=b.or_(force,b.or_(threshold(local,4),b.and_(nf,threshold(left,4))))
    erase=b.or_(b.and_(b.inv(nf),b.inv(threshold(local,2))),b.and_(nf,b.inv(threshold(left,1))))
    ng=b.or_(force,b.or_(b.and_(flag2[0],b.inv(erase)),b.and_(b.inv(flag2[0]),born)))
    words=[]
    for j in range(-7,8):
        row={n:zero for n,_ in f.SCHEMA}
        row.update(address=pos(j),age=b.const(age),f1=(flag1[j],)+(0,)*63,f2=(flag2[j],)+(0,)*63,signal=signal(j))
        row['w2_wf1']=(wf(j,1),)+(0,)*63;row['w2_wf2']=(wf(j,2),)+(0,)*63
        words.extend(row[n] for n,_ in f.SCHEMA)
    desc=f.self_description();names=[*(n for n,_ in f.GEOMETRY),*(f'w{d+2}_{n}' for d in f.OFFSETS for n in ('wf1','wf2'))]
    program=prune(Program(desc.inputs,desc.operations,tuple(desc.outputs[f.COL[n]] for n in names)))
    actual=b.evaluate(program,tuple(words))
    expect=dict(address=address,age=b.const(age+1),f1=(nf,)+(0,)*63,f2=(ng,)+(0,)*63,signal=signal(0))
    for d in f.OFFSETS:
        a=pos(d)
        one=b.and_(b.inv(lt(a,f.Q-5)),sigbit(d,1)) if next_forced else 0
        two=b.and_(b.and_(lt(a,5),sigbit(d,0)),b.inv(new_f1(d))) if next_forced else 0
        expect[f'w{d+2}_wf1']=(one,)+(0,)*63;expect[f'w{d+2}_wf2']=(two,)+(0,)*63
    for name,got in zip(names,actual):
        for bit,(x,y) in enumerate(zip(got,expect[name])):
            bad=b.xor(x,y)
            if bad:raise AssertionError((mode,name,bit,b.witness(bad)))
    result=dict(mode=mode,passed=True,independent_bits=width+36,all_addresses=f.Q,arbitrary_flag_bits=30,neighbor_signal_bits=6,checked_words=names,bdd_nodes=len(b.nodes),descriptor_sha256=desc.digest())
    b.binary.cache_clear();return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();cases=[prove_case(mode) for mode in ('entry','forced','cutoff','erase')]
    result=dict(passed=True,cases=cases,seconds=time.perf_counter()-start,source_sha256={str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in (Path(__file__),Path(f.__file__),Path('gacsca/fixed_rule/word_bdd.py'),Path('gacsca/fixed_rule/retimed_holder_description.py'))},scope='Selected complete physical descriptor outputs equal canonical arbitrary-flag recurrence, including every backup Wf and stationary Signal, over all Address/flag/neighbor-Signal assignments. Age has no remaining flag dependence except forcing boundaries on this suffix domain; input Wf is coherently derived, not arbitrary.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
