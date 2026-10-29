"""Internal GBP1 compiler test: actual finite CPU, fitting prefix only.

This is not a full beta, period, or reliability certificate. The fitting
native/final-source subsection is executed at real tape coordinates. It
helps check compiler primitives while the full own emission overflows Q.
"""
import argparse, hashlib, json, random, time
from pathlib import Path
from dataclasses import replace
from binary_own_emitter import OwnEmitter
import binary_own_rule_v1 as b

def prefix():
    e=OwnEmitter();e.native_outputs_and_final_workspace();e.a.emit('HLT')
    beta,labels,rows=e.a.assemble();return beta,labels,rows

def tape(cells):
    encoded={j:b.encode_cell(c) for j,c in cells.items()}
    return tuple(sum(encoded[j][a-b.PRIMARY_START]<<i for i,j in enumerate(b.LANES))
       if b.PRIMARY_START<=a<b.PRIMARY_START+b.FRAME_BITS else 0 for a in range(b.Q))

def execute(cells,beta,limit=200000):
    data=tape(cells);p=b.Packet(p=1);address=b.PRIMARY_START;out={};ticks=0
    while ticks<limit:
        if p.move==1:address+=1
        elif p.move==2:address-=1
        if not 0<=address<b.Q:raise AssertionError(('head escaped',address,ticks))
        p,write=b.cpu(p,address,data[address],beta);ticks+=1
        if write is not None:out[address]=write
        if p.mode==b.ERROR:raise AssertionError(('error',address,ticks,p))
        if p.mode==b.HALT:return out,ticks,address
    raise AssertionError(('timeout',limit,p,address))

def random_cells(rng):
    return {j:b.Cell(**{f:rng.getrandbits(w) for f,w in b.NATIVE},
      **{f:tuple(rng.getrandbits(w) for _ in range(5)) for f,w in b.FIELDS}) for j in b.LANES}

def canonical(cells,age,gf=100):
    return {j:replace(c,addr=(gf+j)%b.Q,age=age,f1=0,f2=0,wf1=0,wf2=0) for j,c in cells.items()}

def run(count=20):
    start=time.monotonic();beta,labels,rows=prefix();rng=random.Random(721)
    cases=[]
    for i in range(count):cases.append(('raw_'+str(i),random_cells(rng)))
    for age in (b.U-1,0,b.DELIVERY-1,b.DELIVERY,96*b.Q-1,98*b.Q-1):
        for gf in (0,1,2,3,4,b.Q-5,b.Q-4,b.Q-3,b.Q-2,b.Q-1):
            cases.append((f'canonical_{age}_{gf}',canonical(random_cells(rng),age,gf)))
    traces=[]
    for name,cells in cases:
        out,ticks,last=execute(cells,beta)
        expected=b.total_rule(cells,beta);bit=0;words={}
        for field,width in b.NATIVE:
            value=sum(out.get(b.PRIMARY_START+bit+k,0)<<k for k in range(width))
            if value!=getattr(expected,field):
                raise AssertionError((name,field,value,getattr(expected,field),ticks,last))
            words[field]=value;bit+=width
        traces.append({'name':name,'ticks':ticks,'head_halt_address':last,'native':words})
    return {'scope':'FITTING native/final-source prefix only; full own beta still absent',
      'passed':True,'code_bits':sum(x[3] for x in rows),'instructions':len(rows),
      'cases':len(cases),'maximum_measured_ticks':max(x['ticks'] for x in traces),
      'traces':traces,'beta_sha256':hashlib.sha256(bytes(beta)).hexdigest(),
      'elapsed_seconds':time.monotonic()-start,'full_beta':False,'universal_proof':False,
      'period_proof':False,'noise_proof':False,'gray_counterexample':False}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--count',type=int,default=20);p.add_argument('--output',type=Path)
    a=p.parse_args();result=run(a.count)
    if a.output:a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='traces'},sort_keys=True))
