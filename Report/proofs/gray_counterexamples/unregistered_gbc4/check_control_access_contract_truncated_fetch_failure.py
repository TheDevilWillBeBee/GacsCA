"""Generic CALL/RETURN cofactors and issued shared Head-read component.

The component beta fitsQ and runs the actual generic CPU (no diagnostic
table). It is not an own beta for the complete GBC4 rule. Coherent real
lower controls and captured input bank are explicit execution premises.
"""
from dataclasses import asdict,replace
from hashlib import sha256
from pathlib import Path
import argparse,json,time
import compact_completion_rule as b
import complete_branch_emitter as e
from check_early_stage_emission import case_cells


def code_at(name,args,pc):
    code=[0]*b.Q;bits=b.encode(name,*args)
    code[pc:min(b.Q,pc+len(bits))]=bits[:b.Q-pc]
    return tuple(code)


def helper_beta(q,centre,offset,width):
    a=e.Assembler();a.literal(q);a.put(e.QCOL)
    a.literal(centre&15);a.emit('SETFN')
    a.literal(offset+(width<<10));a.emit('SWAP')
    a.call('shared_head_read',380);a.get(e.RAW);a.emit('HLT')
    e.shared_head_read_helper(a)
    bits,listing,size=a.finish();return bits,listing,size


def run(output):
    t0=time.monotonic();mem={d:0 for d in range(-4,5)};counts={'call':0,'return':0,'issued_helper':0}
    seed=b.Packet(p=1,pc=0,move=2,a=777,b=999,fn=13,buf=3,lane=31,
                  work=(1<<407)-7,nc=(1<<35)-9)
    digest=sha256()
    for pc in (0,31,b.Q-26,b.Q-25,b.Q-24,b.Q-1):
        for bank in (0,1):
            for target in (0,77,b.Q-1):
                beta=code_at('CALL',(target,bank),pc);p=replace(seed,pc=pc)
                got,write=b.cpu(p,100,mem,beta);decoded=b.decode(beta,pc)
                assert decoded[0]=='CALL';actualtarget,actualbank=decoded[1]
                if pc+25>=b.Q:want=b.fail(p)
                else:
                    off=360+20*actualbank;mask=b.MASK<<off
                    want=b.continue_pc(replace(p,work=((p.work&~mask)|((pc+25)<<off))&b.WORK_MASK),actualtarget)
                assert got==want and write is None,(pc,bank,target,asdict(got),asdict(want))
                digest.update(repr((p,decoded,got)).encode());counts['call']+=1
    for pc in (0,31,b.Q-11,b.Q-1):
        for bank in (0,1):
            for target in (0,77,b.Q-1,b.Q,b.MASK):
                beta=code_at('RETURN',(bank,),pc);decoded=b.decode(beta,pc)
                assert decoded[0]=='RETURN';actualbank=decoded[1][0]
                off=360+20*actualbank;mask=b.MASK<<off
                p=replace(seed,pc=pc,work=(seed.work&~mask)|(target<<off))
                got,write=b.cpu(p,100,mem,beta)
                want=b.continue_pc(p,target)
                assert got==want and write is None,(pc,bank,target,got,want)
                digest.update(repr((p,decoded,got)).encode());counts['return']+=1
    cells=case_cells(112*b.Q+2);enc={j:b.encode_cell(c) for j,c in cells.items()}
    def tape(a):
        if not b.PRIMARY_START<=a<b.PRIMARY_START+b.FRAME_BITS:return 0
        return sum(enc[j][a-b.PRIMARY_START]<<lane for lane,j in enumerate(b.LANES))
    rows=[]
    for centre in (-1,0,1):
        for q in range(5):
            for offset,width in ((0,6),(19,13),(91,20),(400,20),(546,7)):
                beta,listing,size=helper_beta(q,centre,offset,width)
                p=replace(seed,move=0);position=b.PRIMARY_START;trace=sha256()
                for tick in range(1,20000):
                    position+=1 if p.move==1 else -1 if p.move==2 else 0
                    assert 0<=position<b.Q
                    p,bit=b.cpu(p,position,{d:tape(position+d) for d in range(-4,5)},beta)
                    assert bit is None and p.mode!=b.ERROR,(centre,q,offset,width,tick,asdict(p))
                    trace.update(repr((tick,position,p)).encode())
                    if p.mode==b.HALT:break
                else:raise AssertionError('issued helper did not terminate')
                wanted=(b.voted(cells,centre+b.SLOTS[q],'head')>>offset)&((1<<width)-1)
                assert p.a==wanted and (p.work>>80)&b.MASK==wanted
                changed=((1<<20)-1)<<80|((1<<20)-1)<<100|((1<<20)-1)<<380
                assert p.work&~changed==seed.work&~changed
                assert p.nc==seed.nc and p.fn==centre&15
                rows.append({'q':q,'centre':centre,'offset':offset,'width':width,
                             'component_bits':size,'component_sha256':sha256(bytes(beta)).hexdigest(),
                             'updates':tick,'result':wanted,'trace_sha256':trace.hexdigest()})
                counts['issued_helper']+=1
    out={'passed':True,'Q':8192,'U':1048576,'lambda':24,'c':104,
         'scope':'generic control cofactors and issued non-own Head-access component',
         'counts':counts,'raw_control_sha256':digest.hexdigest(),'helper_cases':rows,
         'actual_input_cells':{str(j):asdict(c) for j,c in cells.items()},
         'sources':{str(p):sha256(p.read_bytes()).hexdigest() for p in
                    (Path(__file__),Path(b.__file__),Path(e.__file__))},
         'whole_own_beta':False,'physical_period':False,'gray_refutation':False,
         'iid_failure':False,'elapsed_seconds':time.monotonic()-t0}
    output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k not in ('helper_cases','actual_input_cells')},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    run(p.parse_args().output)
