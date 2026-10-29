"""Selected complete-emitter WORDOUT branches on full raw upper inputs.

The rejectedQ listing is tested only in the declared separate-code
diagnostic. Every raw input/output bit is pinned; no universal composite
own-emitter or physical-period claim is inferred from this campaign.
"""
from dataclasses import replace
from hashlib import sha256
from pathlib import Path
import argparse,json,time
import compact_completion_rule as b
import complete_branch_emitter as e
from check_complete_listing_diagnostic import execute,with_packet,target_programme
from check_complete_listing_extended import inputs


def selected():
    base=inputs(112*b.Q+2)
    for width,wide,start in ((1,0,100),(20,0,100),(20,1,100),(1,1,8191),
                              (20,1,8096),(20,1,8097),(21,0,100),
                              (0,0,100|(20<<13)),(0,1,100|(13<<13)),
                              (0,1,8191|(1<<13)),(0,0,100|(1<<18)),
                              (0,1,100|(21<<13))):
        beta,pc=target_programme('PUTWORD',(width,wide))
        p=b.Packet(p=1,pc=pc,a=b.MASK-3,b=start,work=(1<<407)-1,nc=(1<<35)-1,
                   fn=15,ret=13,index=100,buf=3,lane=31,kind=3)
        yield 'PUTWORD_'+str((width,wide,start)),with_packet(base,0,p),beta
    for kind,index,start in ((0,0,100),(0,19,100),(1,0,100),(1,19,100),
                             (1,19,8096),(1,19,8097),(1,20,100),(3,0,100),
                             (0,0,99),(1,1,101)):
        p=b.Packet(p=1,mode=b.WORDOUT,pc=31,ret=45,start=start,index=index,
                   b=b.MASK-2,a=777,kind=kind,work=(1<<407)-1,nc=(1<<35)-1,
                   buf=3,lane=31,fn=15)
        yield 'pending_'+str((kind,index,start)),with_packet(base,0,p),(0,)*b.Q


def run(output):
    t0=time.monotonic();r=e.emit_complete_structural_listing();cases=[]
    for name,cells,beta in selected():
        v=execute(cells,beta,r['listing']);cases.append({'name':name,**v})
        print(json.dumps({'name':name,'passed':v['passed'],'updates':v.get('updates'),
                          'wrong_raw_bits':v.get('wrong_raw_bits',[])[:10]}),flush=True)
        if not v['passed']:break
    out={'passed':all(x['passed'] for x in cases),'Q':b.Q,'U':b.U,'lambda':24,'c':104,
         'scope':'selected full raw branches; separate finite listing diagnostic',
         'cases':cases,'programme_bits':r['programme_bits'],
         'out_of_Q_references':len(r['invalid_references']),
         'sources':{str(p):sha256(p.read_bytes()).hexdigest() for p in
                    (Path(__file__),Path(e.__file__),Path(b.__file__))},
         'universal_emitter_equivalence':False,'whole_own_beta':False,
         'physical_period':False,'gray_refutation':False,'iid_failure':False,
         'elapsed_seconds':time.monotonic()-t0}
    output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='cases'},indent=2))
    return out['passed']


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    raise SystemExit(0 if run(p.parse_args().output) else 1)
