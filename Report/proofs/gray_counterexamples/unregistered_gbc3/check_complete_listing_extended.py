"""Further selected full-raw tests of the rejected separate-listing diagnostic.

No originalQ-bit own programme/physical period/noise theorem is asserted.
Every actual upper record is preserved in each receipt, including all
553 raw Head bits, native fields and17 History lanes/fiveholders.
"""
from dataclasses import replace
from pathlib import Path
from hashlib import sha256
import argparse,json,time
import compact_completion_rule as b
import complete_branch_emitter as e
from check_complete_listing_diagnostic import execute,with_packet,target_programme
from check_early_stage_emission import case_cells


def inputs(phi,addr=100):
    return {j:replace(c,addr=(addr+j)%b.Q,head=(0,)*5)
            for j,c in case_cells(phi).items()}


def selected():
    tests=[]
    for kind,lane in ((0,0),(0,24),(0,8),(0,9),(1,0),(1,26),(1,6),(1,7),
                      (2,0),(2,1),(3,31)):
        p=b.Packet(p=1,mode=b.IO,start=100,ret=13,kind=kind,lane=lane,
                   a=b.MASK,b=734,nc=(1<<35)-1)
        tests.append(('IO_'+str((kind,lane)),with_packet(inputs(112*b.Q+2),0,p),(0,)*b.Q))
    for kind in range(4):
        for aligned_lane in (0,4 if kind==1 else 6 if kind==2 else 8):
            p=b.Packet(p=1,mode=b.SPAN,start=100,index=1,ret=13,kind=kind,
                       lane=aligned_lane,a=2,b=b.MASK//3)
            tests.append(('SPAN_'+str((kind,aligned_lane)),with_packet(inputs(112*b.Q+2),0,p),(0,)*b.Q))
        p=b.Packet(p=1,mode=b.SPAN,start=100,index=0,ret=13,kind=kind,
                   lane=0,a=1,b=b.MASK//3)
        tests.append(('SPAN_last_'+str(kind),with_packet(inputs(112*b.Q+2),0,p),(0,)*b.Q))
    for kind,buf,lane in ((0,0,0),(1,0,6),(1,2,4),(1,3,31),
                          (0,1,17),(3,1,1),(1,2,5)):
        p=b.Packet(p=1,mode=b.STREAM,start=100,index=0,ret=13,kind=kind,
                   buf=buf,lane=lane,a=1,b=b.MASK)
        tests.append(('STREAM_'+str((kind,buf,lane)),with_packet(inputs(112*b.Q+2),0,p),(0,)*b.Q))
    for mode,move in ((0,3),(2,0),(3,0),(6,0),(7,0)):
        p=b.Packet(p=1,mode=mode,move=move,pc=b.Q-1,a=b.MASK,b=b.MASK)
        tests.append(('static_'+str((mode,move)),with_packet(inputs(112*b.Q+2),0,p),(0,)*b.Q))
    c=with_packet(inputs(112*b.Q+2),0,b.Packet(p=1,pc=0))
    c=with_packet(c,-1,b.Packet(p=1,move=1,mode=b.HALT,a=333))
    tests.append(('collision_self_left',c,(0,)*b.Q))
    for gf in (0,1,2,3,4,b.Q-5,b.Q-4,b.Q-3,b.Q-2,b.Q-1):
        tests.append(('final_source_'+str(gf),inputs(96*b.Q+4,gf),(0,)*b.Q))
    for gf in (b.COLLECTOR-2,b.COLLECTOR-1,b.COLLECTOR,
               b.COLLECTOR+1,b.COLLECTOR+2):
        c=inputs(b.EVALUATE,gf)
        for logical in range(-2,3):
            p=b.Packet(work=(1<<407)-1 if logical%2 else (1<<396)-1)
            c=with_packet(c,logical,p)
        tests.append(('native_seed_'+str(gf),c,(0,)*b.Q))
    # All five copied logical heads execute a legal instruction at the
    # same row. This is a prepared separate-code runtime diagnostic,
    # never an actual compiled-Q beta or intact hierarchy/noise history.
    beta,pc=target_programme('PUSH',(20,))
    c=inputs(112*b.Q+2)
    for logical in range(-2,3):
        c=with_packet(c,logical,b.Packet(p=1,pc=pc,a=b.MASK,
                       work=(1<<407)-1,ret=7,index=123))
    tests.append(('five_simultaneous_PUSH20',c,beta))
    return tests


def run(output):
    t0=time.monotonic();r=e.emit_complete_structural_listing();cases=[]
    for name,cells,beta in selected():
        v=execute(cells,beta,r['listing'])
        cases.append({'name':name,**v})
        print(json.dumps({'case':name,'passed':v['passed'],'updates':v.get('updates'),
                          'wrong_raw_bits':v.get('wrong_raw_bits',[])[:12]}),flush=True)
        if not v['passed']:break
    out={'passed':all(c['passed'] for c in cases),'scope':'selected separate-code diagnostics',
         'Q':8192,'U':1048576,'lambda':24,'c':104,
         'programme_bits':r['programme_bits'],'instructions':r['instructions'],
         'out_of_Q_references':len(r['invalid_references']),
         'cases':cases,'sources':{str(p):sha256(p.read_bytes()).hexdigest() for p in
                    (Path(__file__),Path(e.__file__),Path(b.__file__))},
         'universal_semantics_proved':False,'universal_deadline_proved':False,
         'whole_own_beta':False,'physical_period':False,'gray_refutation':False,
         'iid_failure':False,'elapsed_seconds':time.monotonic()-t0}
    output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='cases'},indent=2))
    return out['passed']


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();raise SystemExit(0 if run(a.output) else 1)
