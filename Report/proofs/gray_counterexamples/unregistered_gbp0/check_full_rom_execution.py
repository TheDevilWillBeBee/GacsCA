"""Actual prepared whole-emission tests for the EXPLICIT nine-Q ROM rule.

The finite CPU uses exactly the emitted immutable bits, with real physical
operand travel. No total-rule evaluator is an opcode. This is development
validation, not a universal proof or a canonical period theorem.
"""
import argparse, hashlib, json, random, time
from pathlib import Path
from dataclasses import replace, asdict
from binary_own_emitter_full_rom_v2 import FullEmitter
import binary_own_rule_rom_v2 as b

def compile_program():
    a=FullEmitter().complete();beta,labels,rows=a.assemble()
    assert all(x in (0,1) for x in beta)
    return beta,labels,rows

def tape(cells):
    words={j:b.encode_cell(c) for j,c in cells.items()}
    return tuple(sum(words[j][a-b.PRIMARY_START]<<i for i,j in enumerate(b.LANES))
      if b.PRIMARY_START<=a<b.PRIMARY_START+b.FRAME_BITS else 0 for a in range(b.Q))

def run(cells,beta,limit=300000):
    data=tape(cells);p=b.Packet(p=1);address=b.PRIMARY_START
    out={};ticks=0;deadline=None;whole_stage=None;writes=0
    control=hashlib.sha256();lo=address;hi=address
    while ticks<limit:
        if p.move==1:address+=1
        elif p.move==2:address-=1
        if not 0<=address<b.Q:raise AssertionError(('escape',ticks,address,asdict(p)))
        control.update(address.to_bytes(2,'little')+p.pc.to_bytes(3,'little')+
                       bytes((p.mode,p.kind,p.index,p.move)))
        lo=min(lo,address);hi=max(hi,address)
        p,write=b.cpu(p,address,data[address],beta);ticks+=1
        if write is not None:out[address]=write;writes+=1
        if ticks==8*b.Q-2:deadline=dict(out)
        if ticks==16*b.Q-2:whole_stage=dict(out)
        if p.mode==b.ERROR:raise AssertionError(('Error',ticks,address,asdict(p)))
        if p.mode==b.HALT:return out,ticks,address,deadline,writes,whole_stage,control.hexdigest(),(lo,hi)
    raise AssertionError(('timeout',ticks,address,asdict(p)))

def canonical(age=123,gf=100):
    return {j:b.Cell(addr=(gf+j)%b.Q,age=age) for j in b.LANES}

def coherent(cells,heads):
    return {x:replace(c,head=tuple(b.pack(heads.get(x+s,b.ZERO)) for s in b.SLOTS)) for x,c in cells.items()}

def cases(beta,rows,which='smoke'):
    yield 'zero',canonical()
    allones=b.Packet(p=1,mode=b.HALT,regs=(b.MASK,)*b.REGISTERS,work=(1<<b.WORK_BITS)-1)
    yield 'halt_heads',coherent(canonical(),{j:allones for j in range(-10,11)})
    if which=='smoke':return
    yield 'birth',canonical(112*b.Q,b.PRIMARY_START)
    yield 'collect',canonical(b.COLLECT-1,b.PRIMARY_START+17)
    yield 'move_collect',coherent(canonical(b.COLLECT+8,b.COLLECTOR),{j:allones for j in range(-10,11)})
    first={}
    for pc,name,args,size in rows:
        if name in b.OP_NAMES and name not in first:first[name]=pc
    for name,pc in first.items():
        h=b.Packet(p=1,pc=pc,regs=(0,b.PRIMARY_START,0,0,0,0,0,0,0,0,0),work=(1<<407)-1)
        yield 'run_'+name,coherent(canonical(112*b.Q+1,b.PRIMARY_START),{0:h})
    for kind in range(4):
        h=b.Packet(p=1,mode=b.IO,kind=kind,start=b.PRIMARY_START,index=0,
           width=37 if kind==b.LDB else 20,dst=0,ret=0,regs=(b.MASK,)*b.REGISTERS,work=0)
        yield 'io_'+str(kind),coherent(canonical(112*b.Q+1,b.PRIMARY_START),{0:h})

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--cases',choices=('smoke','all'),default='smoke')
    ap.add_argument('--output',type=Path);ap.add_argument('--failure',type=Path);args=ap.parse_args()
    start=time.monotonic();beta,labels,rows=compile_program();traces=[]
    for name,cells in cases(beta,rows,args.cases):
        expected=b.encode_cell(b.total_rule(cells,beta))
        try:
            out,ticks,address,deadline,writes,whole_stage,control_sha,bounds=run(cells,beta)
            missing=[b.PRIMARY_START+i for i in range(b.FRAME_BITS) if b.PRIMARY_START+i not in out]
            wrong=[i for i,bit in enumerate(expected) if out.get(b.PRIMARY_START+i,0)!=bit]
            assert not missing and not wrong,('mismatch',name,missing[:20],wrong[:20])
        except Exception as exc:
            failure={'name':name,'exception':repr(exc),'cells':{str(j):asdict(c) for j,c in cells.items()},
                'beta_sha256':hashlib.sha256(bytes(beta)).hexdigest(),'code_bits':sum(r[3] for r in rows),
                'time_seconds':time.monotonic()-start,'own_beta_Q_fit':False,'universal_equivalence':False}
            if 'out' in locals():failure.update({'wrong_all':wrong,'missing_all':missing,'outputs':out,'ticks':ticks})
            if args.failure:args.failure.write_text(json.dumps(failure,indent=2)+'\n')
            raise
        deadline_wrong=[] if deadline is None else [i for i,v in enumerate(expected) if deadline.get(b.PRIMARY_START+i,0)!=v]
        stage_wrong=[] if whole_stage is None else [i for i,v in enumerate(expected) if whole_stage.get(b.PRIMARY_START+i,0)!=v]
        trace={'name':name,'ticks':ticks,'head_halt_address':address,'writes':writes,'deadline':8*b.Q-2,
          'deadline_wrong_bits':deadline_wrong,'whole_fifth_stage_wrong_bits':stage_wrong,
          'control_trace_sha256':control_sha,'physical_head_bounds':bounds,'full_outputs_equal':True}
        if name=='halt_heads':
            trace.update({'intact_recursive_initialization':False,
              'source_cells':{str(j):asdict(c) for j,c in cells.items()},
              'expected_raw_record':''.join(map(str,expected)),
              'deadline_raw_record':''.join(str(deadline.get(b.PRIMARY_START+i,0)) for i in range(b.FRAME_BITS)),
              'whole_fifth_stage_raw_record':''.join(str(whole_stage.get(b.PRIMARY_START+i,0)) for i in range(b.FRAME_BITS))})
        traces.append(trace)
        print(json.dumps({k:v for k,v in trace.items() if k in ('name','ticks','head_halt_address','writes','deadline','full_outputs_equal','physical_head_bounds')}|
            {'deadline_wrong_bit_count':len(deadline_wrong),'whole_fifth_stage_wrong_bit_count':len(stage_wrong)}),flush=True)
    result={'passed':True,'scope':'selected prepared actual full-code executions; explicitly9Q-ROM rule',
      'Q':b.Q,'U':b.U,'lambda':b.LAMBDA,'c':b.ERROR_SEPARATION,'K':b.FRAME_BITS,'2K':2*b.FRAME_BITS,
      'code_bits':sum(r[3] for r in rows),'ROM_bits':b.CODE_BITS,'PC_bits':b.PC_BITS,
      'beta_sha256':hashlib.sha256(bytes(beta)).hexdigest(),'traces':traces,
      'elapsed_seconds':time.monotonic()-start,'Q_beta_fit':False,'universal_equivalence':False,
      'physical_period':False,'noise_proof':False,'gray_counterexample':False}
    if args.output:args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='traces'}),flush=True)

if __name__=='__main__':main()
