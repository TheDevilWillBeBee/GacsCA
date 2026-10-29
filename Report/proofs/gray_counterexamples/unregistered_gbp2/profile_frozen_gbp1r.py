"""Instruction/travel profile of frozen GBP1R, not a new rule or proof.

Annotation wrappers are confined to a new subclass. The emitted bits must
equal the frozen beta. Profiles guide the next smaller interpreter design.
"""
import argparse
from collections import Counter,defaultdict
from dataclasses import replace
import functools,hashlib,json,sys,time
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(BASE/'unregistered_gbp0'))
from binary_own_emitter_full_rom_v2 import FullEmitter
import binary_own_rule_rom_v2 as b
from check_full_rom_execution import canonical,coherent,tape

class AnnotatedEmitter(FullEmitter):
    pass

for name in {n for cls in FullEmitter.__mro__ for n,v in cls.__dict__.items()
             if callable(v) and not n.startswith('__')}:
    original=getattr(FullEmitter,name)
    def wrap(fn,n):
        @functools.wraps(fn)
        def call(self,*args,**kwargs):
            self.call_stack.append(n)
            try:return fn(self,*args,**kwargs)
            finally:self.call_stack.pop()
        return call
    setattr(AnnotatedEmitter,name,wrap(original,name))

def profile():
    start=time.monotonic();emitter=AnnotatedEmitter();emitter.call_stack=[];tags=[]
    original=emitter.a.emit
    important={'native_outputs_and_final_workspace','info_field','next_field',
      'mail_field','history_field','courier_field','head_field','packet_output',
      'helpers','io_body','run_body'}
    def emit(*args):
        tags.append(next((n for n in reversed(emitter.call_stack) if n in important),'setup/wipe/loop'))
        return original(*args)
    emitter.a.emit=emit
    asm=emitter.complete();beta,labels,rows=asm.assemble()
    assert hashlib.sha256(bytes(beta)).hexdigest()=='ac681db3e466cabb3bca8c01a0c1d68b8ac23668e4a4ad8e81db7fc65c5e9418'
    instructions=[row for row in rows if row[1]!='DATA20'];assert len(instructions)==len(tags)
    owners={pc:tag for (pc,_,_,_),tag in zip(instructions,tags)}
    helper_starts=sorted((p,n) for n,p in labels.items() if n.startswith('helper_'))
    # These shared physical helpers are separate actual code intervals.
    helper_names={'helper_reg_read','helper_work_read','helper_metadata_load','helper_mem_read'}
    helper_starts=[(p,n) for p,n in helper_starts if n in helper_names]
    for i,(lo,name) in enumerate(helper_starts):
        hi=helper_starts[i+1][0] if i+1<len(helper_starts) else labels['data_slots']
        for pc in owners:
            if lo<=pc<hi:owners[pc]=name
    ones=b.Packet(p=1,mode=b.HALT,regs=(b.MASK,)*b.REGISTERS,work=(1<<b.WORK_BITS)-1)
    cells=coherent(canonical(),{j:ones for j in range(-10,11)});mem=tape(cells)
    p=b.Packet(p=1);address=b.PRIMARY_START;counts=defaultdict(Counter);opcounts=Counter();ticks=0;io_owner=None
    writes=0;moves=0
    while ticks<300000:
        if p.move==1:address+=1;moves+=1
        elif p.move==2:address-=1;moves+=1
        if p.mode==b.RUN:
            owner=owners[p.pc];kind='RUN';op=b.decode(b.code_word(beta,p.pc)|(b.code_word(beta,p.pc+20)<<20))[0]
            opcounts[op]+=1
        elif p.mode==b.IO:
            owner=io_owner;kind='IO_consume' if address==b.io_target(p) else 'IO_travel'
        else:raise AssertionError(('unexpected mode',ticks,p.mode))
        counts[owner][kind]+=1;oldmode=p.mode
        p,write=b.cpu(p,address,mem[address],beta);ticks+=1
        if oldmode==b.RUN and p.mode==b.IO:io_owner=owner
        if write is not None:writes+=1
        if p.mode==b.HALT:break
        assert p.mode!=b.ERROR
    assert ticks==147051 and sum(sum(c.values()) for c in counts.values())==ticks
    return {'passed':True,'scope':'actual frozen GBP1R HALT-input cost profile only; no new rule',
      'Q':b.Q,'U':b.U,'c':b.ERROR_SEPARATION,'lambda':b.LAMBDA,
      'beta_sha256':hashlib.sha256(bytes(beta)).hexdigest(),'ticks':ticks,'moves':moves,'writes':writes,
      'counts_by_emitted_section':{n:dict(c) for n,c in sorted(counts.items())},
      'run_instruction_counts':dict(opcounts),'elapsed_seconds':time.monotonic()-start,
      'new_beta_fit':False,'universal_time_proof':False,'new_rule':False,'gray_counterexample':False}

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--output',type=Path,required=True);options=a.parse_args()
    result=profile();options.output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,sort_keys=True))
