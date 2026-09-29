"""Exact all-Age descriptor proof of the ordinary zero-payload boundary orbit."""
import argparse,hashlib,json,time
from pathlib import Path
from dataclasses import replace
from gacsca.fixed_rule.word_bdd import BDD
from gacsca.fixed_rule import repair_b_rule as f,repair_b_projected as r,repair_b_initial as initial


def prove(description=None):
    d=f.self_description() if description is None else description
    width=dict(f.SCHEMA)['age'];assert f.U==1<<width
    b=BDD(width);age=tuple(b.variable(i) for i in range(width))+(0,)*(64-width)
    cap=r.lift(initial.terminal_data()[0]);word=tuple(age if name=='age' else b.const(getattr(cap,name)) for name,_ in f.SCHEMA)
    actual=b.evaluate(d,word*11)
    next_age=b.add(age,b.const(1))[:width]+(0,)*(64-width)
    expected=tuple(next_age if name=='age' else b.const(getattr(cap,name)) for name,_ in f.SCHEMA)
    for (name,_),got,want in zip(f.SCHEMA,actual,expected):
        for bit,(a,c) in enumerate(zip(got,want)):
            if a!=c:raise AssertionError((name,bit,'Age witness',b.witness(b.xor(a,c))))
    return dict(passed=True,all_ages=f.U,raw_words=f.FIELDS,descriptor_operations=len(d.operations),descriptor_sha256=d.digest(),BDD_nodes=len(b.nodes),physical_radius=5,boundary='homogeneous ordinary G cell with Address Q-1, Flag1=Flag2=1, all other fields zero except Age',limitation='exact noiseless boundary orbit; not an organized colony, a noise-robust cap, or deeper physical execution')


def execute(output):
    output=Path(output)
    if output.exists():raise FileExistsError('preserve evidence')
    start=time.monotonic();result=prove();result['seconds']=time.monotonic()-start
    files=[Path(__file__),Path('gacsca/fixed_rule/word_bdd.py'),Path('gacsca/fixed_rule/repair_b_rule.py'),Path('gacsca/fixed_rule/repair_b_description.py')]
    result['source_sha256']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files};output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True,type=Path);a=p.parse_args();execute(a.output)
