"""Replay all selected full-raw families for the exact shared GBC5 listing."""
from dataclasses import asdict
from pathlib import Path
from hashlib import sha256
import json,argparse,time
import scratch_free_reader_emitter as e
b=e.b
import check_complete_listing_extended as x
import check_wordout_listing as w
from check_complete_listing_diagnostic import execute,target_programme,with_packet
from check_early_stage_emission import case_cells


def cases():
    for phi in (0,b.COLLECT,b.COLLECT+1,b.EVALUATE-1,b.EVALUATE,b.EVALUATE+1,b.DELIVERY,96*b.Q,96*b.Q+1,98*b.Q-1,98*b.Q,112*b.Q,112*b.Q+1,120*b.Q):
        yield 'stage_'+str(phi),x.inputs(phi),(0,)*b.Q
    yield from x.selected()
    yield from w.selected()
    for bank in (0,1):
        for target in (0,77,b.Q-1,b.Q,b.MASK):
            p=b.Packet(p=1,pc=31,work=target<<(360+20*bank),a=777,b=999)
            beta,pc=target_programme('RETURN',(bank,))
            yield 'RETURN_'+str((bank,target)),with_packet(x.inputs(112*b.Q+2),0,p),beta
        for target in (0,77,b.Q-1):
            beta,pc=target_programme('CALL',(target,bank))
            p=b.Packet(p=1,pc=pc,work=(1<<407)-1,a=777,b=999)
            yield 'CALL_'+str((bank,target)),with_packet(x.inputs(112*b.Q+2),0,p),beta


def run(output):
    t0=time.monotonic();r=e.emit_complete_structural_listing();rows=[]
    for name,c,beta in cases():
        v=execute(c,beta,r['listing']);rows.append({'name':name,**v})
        print(json.dumps({'name':name,'passed':v['passed'],'updates':v.get('updates'),'wrong_raw_bits':v.get('wrong_raw_bits',[])[:12]}),flush=True)
        if not v['passed']:break
    out={'passed':all(z['passed'] for z in rows),'scope':'selected separate-code complete GBC5 shared-control diagnostic','Q':8192,'U':1048576,'lambda':24,'c':104,'cases':rows,'listing_bits':r['programme_bits'],'instructions':r['instructions'],'invalid_references':len(r['invalid_references']),'sources':{str(p):sha256(p.read_bytes()).hexdigest() for p in (Path(__file__),Path(e.__file__),Path(b.__file__))},'universal_complete_emitter_equivalence':False,'whole_own_beta':False,'physical_period':False,'gray_refutation':False,'iid_failure':False,'elapsed_seconds':time.monotonic()-t0}
    output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='cases'},indent=2));return out['passed']


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);raise SystemExit(0 if run(p.parse_args().output) else 1)
