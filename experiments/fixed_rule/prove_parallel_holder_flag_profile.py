"""Exact all-Address/all-front one-step proof of the restricted flag profile."""
import argparse,hashlib,json,time
from pathlib import Path
from gacsca.fixed_rule.word_bdd import BDD
from gacsca.fixed_rule.wordcode import Program
from gacsca.fixed_rule.word_prune import prune
from gacsca.fixed_rule import parallel_holder_rule as f


def prove_case(mode):
    # Interleave low bits of the 30-bit Address and 31-bit front (which includes Q).
    b=BDD(61);address=tuple(b.variable(2*i) for i in range(30))+(0,)*34
    front=tuple(b.variable(2*i+1) for i in range(30))+(b.variable(60),)+(0,)*33
    zero=b.const(0);one=b.const(1)
    def add(a,k):return b.add(a,b.const(k&((1<<64)-1)))
    def pos(a,d):return add(a,d)[:30]+(0,)*34
    def lt(a,d):return b.less(a,b.const(d))
    def equal(a,d):
        return b.arithmetic(4,a,b.const(d))[0]
    def select(condition,yes,no):return tuple(b.ite(condition,x,y) for x,y in zip(yes,no))
    forced=mode in ('forced','cutoff');entry=mode=='entry'
    age={'forced':96*f.Q+10,'cutoff':98*f.Q-1,'erase':98*f.Q+10,'entry':96*f.Q-1}[mode]
    guard=b.inv(lt(b.const(f.Q),0)) if False else b.inv(b.less(b.const(f.Q),front))
    if entry:guard=1
    def wf(a):return b.inv(lt(a,f.Q-5)) if forced else 0
    def flag(a):return 0 if entry else b.inv(b.less(a,front)) if forced else b.less(a,front)
    def sig(a):
        bits=[equal(a,f.Q-1-k) for k in range(5)];return tuple(bits)+(0,)*59
    words=[]
    for j in range(-7,8):
        a=pos(address,j);row={n:zero for n,_ in f.SCHEMA}
        row.update(address=a,age=b.const(age),f1=(flag(a),)+(0,)*63,signal=sig(a))
        for d in f.OFFSETS:row[f'w{d+2}_wf1']=(wf(pos(a,d)),)+(0,)*63
        words.extend(row[n] for n,_ in f.SCHEMA)
    desc=f.self_description();names=[*(n for n,_ in f.GEOMETRY),*(f'w{d+2}_{n}' for d in f.OFFSETS for n in ('wf1','wf2'))]
    # Select exactly the actual physical description's flags/geometry/Signal.
    program=prune(Program(desc.inputs,desc.operations,tuple(desc.outputs[f.COL[n]] for n in names)))
    actual=b.evaluate(program,tuple(words))
    if forced:
        shifted=select(lt(front,3),zero,add(front,-3));nextfront=select(b.less(b.const(f.Q-8),shifted),b.const(f.Q-8),shifted)
        nextflag=b.inv(b.less(address,nextfront))
    elif entry:nextflag=0
    else:
        nextfront=select(lt(front,2),zero,add(front,-2));nextflag=b.less(address,nextfront)
    expect=dict(address=address,age=b.const(age+1),f1=(nextflag,)+(0,)*63,f2=zero,signal=sig(address))
    for d in f.OFFSETS:
        on=b.inv(lt(pos(address,d),f.Q-5)) if mode in ('forced','entry') else 0
        expect[f'w{d+2}_wf1']=(on,)+(0,)*63;expect[f'w{d+2}_wf2']=zero
    for name,got in zip(names,actual):
        for bit,(a,c) in enumerate(zip(got,expect[name])):
            bad=b.and_(guard,b.xor(a,c))
            if bad:raise AssertionError((mode,name,bit,b.witness(bad)))
    result=dict(mode=mode,passed=True,independent_bits=61,all_addresses=f.Q,admissible_fronts=1 if entry else f.Q+1,nodes=len(b.nodes),checked_words=names,selected_operations=len(program.operations),descriptor_sha256=desc.digest())
    b.binary.cache_clear();return result


def prove():
    result=[prove_case(mode) for mode in ('entry','forced','cutoff','erase')]
    return dict(passed=True,cases=result,scope='exact selected full-rule flag/geometry/Signal outputs for every Address and front; controller coherence/mail-free condition checked separately',time_reduction='On canonical geometry, inconsistency and d3 are false. Flag updates have no Age dependence beyond Wf windows; these four clock regimes exhaust the profile.')


def execute(output):
    output=Path(output)
    if output.exists():raise FileExistsError('preserve evidence')
    start=time.monotonic();result=prove();result['seconds']=time.monotonic()-start
    files=[Path(__file__),Path('gacsca/fixed_rule/word_bdd.py'),Path('gacsca/fixed_rule/parallel_holder_flag_profile.py'),Path('gacsca/fixed_rule/parallel_holder_rule.py'),Path('gacsca/fixed_rule/parallel_holder_description.py')]
    result['source_sha256']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files};output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);a=p.parse_args();execute(a.output)
