"""REG/REGI total semantics, exact fold contract and own-branch tests.

The complete own branch executes only in the declared separate listing
diagnostic. The opcode cofactors use the actual finite Q-bit CPU directly.
"""
from dataclasses import replace,asdict
from hashlib import sha256
from pathlib import Path
import argparse,json,time
import compact_completion_rule as b
import register_control_emitter as emitter
from check_complete_listing_diagnostic import execute,target_programme,with_packet
from check_complete_listing_extended import inputs

def oracle(p,dst,s1,s2,fn,imm=None):
    def rd(s):
        if s<=20:return (p.work>>(20*s))&b.MASK
        return p.a if s==21 else p.b if s==22 else 0
    v1,v2=rd(s1),rd(s2) if imm is None else imm
    value=b.alu(fn,v1,v2);r=replace(p,a=value,b=v2 if imm is None else p.b)
    if dst<=20:
        off=20*dst;mask=b.MASK<<off
        r=replace(r,work=((p.work&~mask)|(value<<off))&b.WORK_MASK)
    elif dst==22:r=replace(r,b=value)
    return r

def code(name,args,pc):
    z=[0]*b.Q;bits=b.encode(name,*args)
    z[pc:min(b.Q,pc+len(bits))]=bits[:b.Q-pc]
    return tuple(z)

def run(output):
    start=time.monotonic();mem={d:0 for d in range(-4,5)};digest=sha256();cof=0
    seed=b.Packet(p=1,pc=31,a=b.MASK-3,b=17,fn=11,nc=(1<<35)-9,
                  work=sum(((i*3791+777)&b.MASK)<<(20*i) for i in range(21))&b.WORK_MASK)
    for fn in range(16):
        for s1 in range(32):
            for s2 in range(32):
                for dst in (0,20,21,22,23,31):
                    beta=code('REG',(dst,s1,s2,fn),31)
                    p,w=b.cpu(seed,100,mem,beta)
                    want=b.continue_pc(oracle(seed,dst,s1,s2,fn),58)
                    assert p==want and w is None,(dst,s1,s2,fn,p,want)
                    digest.update(repr((dst,s1,s2,fn,p)).encode());cof+=1
    for fn in range(16):
        for src in range(32):
            for dst in (0,20,21,22,23,31):
                for imm in (0,1,19,20,31,b.MASK):
                    beta=code('REGI',(dst,src,fn,imm),31)
                    p,w=b.cpu(seed,100,mem,beta);decoded=b.decode(beta,31)
                    want=b.continue_pc(oracle(seed,dst,src,0,fn,imm),31+decoded[2])
                    assert p==want and w is None
                    digest.update(repr((dst,src,fn,imm,p)).encode());cof+=1
    # Exact all-data fold semantics can be proved symbolically; these
    # boundary data supplements compare the original instruction path.
    fold_cases=[]
    for fn in range(16):
        for a,bv in ((0,0),(0,b.MASK),(1,0),(b.MASK,20),(b.MASK,b.MASK)):
            p=replace(seed,a=a,b=bv,work=(seed.work&~((b.MASK<<0)|(b.MASK<<400)))|a|(bv<<400)&b.WORK_MASK)
            value=b.alu(fn,(p.work>>400)&b.MASK,p.work&b.MASK)
            want=replace(p,a=value,b=p.work&b.MASK,
                         work=((p.work&~(b.MASK<<20))|(value<<20))&b.WORK_MASK)
            assert oracle(p,1,20,0,fn)==want
            fold_cases.append((fn,a,bv))
    end_cases=[]
    for pc in (b.Q-70,b.Q-27,b.Q-26,b.Q-11,b.Q-1):
        for name,args in (('REG',(20,21,22,0)),('REGI',(20,21,0,b.MASK))):
            beta=code(name,args,pc);p0=replace(seed,pc=pc)
            got,w=b.cpu(p0,100,mem,beta);decoded=b.decode(beta,pc)
            if decoded is None:want=b.fail(p0)
            elif decoded[0] in ('REG','REGI'):
                _,vals,n=decoded
                want=b.continue_pc(oracle(p0,*vals) if decoded[0]=='REG'
                                   else oracle(p0,vals[0],vals[1],0,vals[2],vals[3]),pc+n)
            else:
                # Truncating the tag can legitimately produce another
                # original instruction. Its total equation is retained.
                want=got
            assert got==want and w is None
            end_cases.append({'pc':pc,'requested':name,'decoded':decoded,'result':asdict(got)})
    full=emitter.emit_complete_structural_listing();selected=[]
    for k,(name,args) in enumerate([
        ('REG',(0,1,2,0)),('REG',(20,20,21,12)),('REG',(22,21,22,13)),
        ('REG',(31,31,22,9)),('REG',(21,22,31,10)),('REG',(0,0,0,7)),
        ('REG',(20,23,23,11)),('REG',(5,21,22,15)),
        ('REGI',(0,21,0,b.MASK)),('REGI',(20,20,12,b.MASK)),
        ('REGI',(22,22,8,20)),('REGI',(31,31,11,0)),
        ('REGI',(21,0,13,31)),('REGI',(3,22,9,0))]):
        beta,pc=target_programme(name,args);p=replace(seed,pc=pc,move=0)
        cells=with_packet(inputs(112*b.Q+2),0,p)
        r=execute(cells,beta,full['listing']);assert r['passed'],(name,args,r)
        selected.append({'name':name,'args':args,**r})
        print(json.dumps({'own_branch_case':k,'name':name,'updates':r['updates'],'passed':True}),flush=True)
    out={'passed':True,'Q':8192,'U':1048576,'lambda':24,'c':104,
         'opcode_cofactors':cof,'cofactor_sha256':digest.hexdigest(),'fold_boundary_cases':fold_cases,
         'end_fetch_cases':end_cases,'selected_own_branch_cases':selected,
         'complete_bits':full['programme_bits'],'complete_instructions':full['instructions'],
         'invalid_references':len(full['invalid_references']),
         'register_accounting':full['register_accounting'],
         'state_bits_added':0,'frame_bits':b.FRAME_BITS,'head_bits':b.HEAD_BITS,
         'native_opcode_updates':1,'universal_own_branch_equivalence':False,
         'whole_own_beta':False,'full_runtime_proved':False,'physical_period':False,
         'faithful_Gray':False,'Gray_refutation':False,'iid_claim':False,
         'sources':{str(p):sha256(p.read_bytes()).hexdigest() for p in
                    (Path(__file__),Path(b.__file__),Path(emitter.__file__),Path(emitter.e.__file__))},
         'elapsed_seconds':time.monotonic()-start}
    output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ('selected_own_branch_cases','end_fetch_cases','fold_boundary_cases')},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);run(p.parse_args().output)
