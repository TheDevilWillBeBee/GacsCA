"""Exact full-raw-state proof of the ordinary holder cap for all 2^32 Ages."""
import argparse,hashlib,json,time
from pathlib import Path
from gacsca.fixed_rule.word_bdd import BDD
from gacsca.fixed_rule.wordcode import NAND,ADD,SHR,EQ,LT,LIT,MASK
from gacsca.fixed_rule import small_holder_rule as f,small_holder_projected as r,small_holder_boundary as cap


def validate(d):
    if d.inputs!=15*f.FIELDS or len(d.outputs)!=f.FIELDS:raise ValueError('complete radius-seven raw input/output contract required')
    for i,(op,a,b) in enumerate(d.operations):
        if op==LIT:
            if not isinstance(a,int) or not 0<=a<=MASK:raise ValueError('bad literal')
        elif op not in (NAND,ADD,SHR,EQ,LT) or any(not isinstance(v,int) or not 0<=v<d.inputs+i for v in (a,b)):raise ValueError('bad operation or forward wire')
    if any(not isinstance(v,int) or not 0<=v<d.wires for v in d.outputs):raise ValueError('bad output wire')


def prove(description=None):
    d=f.self_description() if description is None else description;validate(d);width=dict(f.SCHEMA)['age'];b=BDD(width)
    age=tuple(b.variable(i) for i in range(width))+(0,)*(64-width)
    def words(t):
        base=r.lift(cap.cell());values={n:b.const(getattr(base,n)) for n,_ in f.SCHEMA};values['age']=t
        head=0;pc=b.const(0)
        for clock,entry in cap.pulse_entries():
            hit=b.arithmetic(EQ,t,b.const(clock))[0];head=b.or_(head,hit)
            pc=tuple(b.ite(hit,a,c) for a,c in zip(b.const(entry),pc))
        values['s3_head']=(head,)+(0,)*63;values['s3_pc']=pc
        return tuple(values[n] for n,_ in f.SCHEMA)
    actual=b.evaluate(d,words(age)*15);next_age=b.add(age,b.const(1))[:width]+(0,)*(64-width)
    for (name,_),got,want in zip(f.SCHEMA,actual,words(next_age)):
        for bit,(a,c) in enumerate(zip(got,want)):
            if a!=c:raise AssertionError((name,bit,'Age witness',b.witness(b.xor(a,c))))
    return dict(passed=True,independent_bits=width,all_ages=f.U,complete_raw_words=f.FIELDS,operations=len(d.operations),descriptor_sha256=d.digest(),BDD_nodes=len(b.nodes),ordinary_cap='homogeneous Address Q-1, F1=F2=1, all other dynamics zero except Age and +1-backup reset/vote head/PC pulse',pulse_entries=cap.pulse_entries(),limitation='exact ordinary cap orbit with complete controller, not an organized or noise-robust colony; no deeper physical execution')


def execute(output):
    output=Path(output)
    if output.exists():raise FileExistsError('preserve evidence')
    start=time.monotonic();result=prove();result['seconds']=time.monotonic()-start
    files=[Path(__file__),Path('gacsca/fixed_rule/word_bdd.py'),Path('gacsca/fixed_rule/small_holder_boundary.py'),Path('gacsca/fixed_rule/small_holder_rule.py'),Path('gacsca/fixed_rule/small_holder_description.py'),Path('gacsca/fixed_rule/small_holder_program.py')]
    result['source_sha256']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files};output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);execute(p.parse_args().output)
