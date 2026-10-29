#!/usr/bin/env python3
"""Read-only GPU output checks plus complete selected C state replays.

All-row border/endpoint checks are exact; this exploration does not
supply the physical source proof, global repair or iid theorem.
"""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib,json,struct,subprocess,time
import numpy as np
ROOT=Path(__file__).resolve().parents[3];S=Path(__file__).resolve().parent
D=ROOT/'figs/robustness/unregistered_sp31_third_gpu'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
GLOBALS='''
static FILE *reference;
static void dump(const State *s,const Info *m,int t){
    _Static_assert(sizeof(Segment)==12,"segment binary format");
    uint32_t header[3]={(uint32_t)t,(uint32_t)s->n,(uint32_t)m->n};
    if(fwrite(header,sizeof(uint32_t),3,reference)!=3 ||
       fwrite(s->seg,sizeof(Segment),s->n,reference)!=(size_t)s->n ||
       fwrite(m->x,sizeof(int),m->n,reference)!=(size_t)m->n){fprintf(stderr,"dump failed\\n");exit(7);}
}
'''
TAIL='''
int main(int argc,char **argv){
    if(argc!=4)return 1;reference=fopen(argv[3],"wb");if(!reference)return 1;
    int result=sp31_third_pilot_main(3,argv);if(fclose(reference))return 8;return result;
}
'''
def generated_reference():
    source=(S/'sp31_third_enclosure_cases.c').read_text()
    source=source.replace('#include "../sp31_two_flag2_sources.c"','#include "'+str(S.parent/'sp31_two_flag2_sources.c')+'"')
    source=source.replace('int main(int argc,char **argv){',GLOBALS+'\nint sp31_third_pilot_main(int argc,char **argv){')
    old='uint64_t events=0;report(&a,&m,0,events);';assert source.count(old)==1
    source=source.replace(old,old+'dump(&a,&m,0);')
    old='a=next;m=newm;report(&a,&m,t+1,events);';assert source.count(old)==1
    return source.replace(old,old+'dump(&a,&m,t+1);')+TAIL

def load(d):
    meta=json.loads((d/'metadata.json').read_text());assert meta['passed']
    assert (meta['NX'],meta['LO'],meta['HI'],meta['fields'],meta['border_width'])==(114688,81920,196608,9,64)
    masks=np.fromfile(d/'masks.bin',dtype='<i4');assert len(masks)==meta['cases']
    metrics=np.memmap(d/'metrics.bin',dtype='<u4',mode='r',shape=(len(masks),meta['ticks']+1,9))
    assert not np.any(metrics[:,:,8]) and not np.any(np.fromfile(d/'endpoint_bad.bin',dtype='<u4'))
    nc=np.fromfile(d/'native_transition_counts.bin',dtype='<u4').reshape(meta['ticks']+1,4)
    ic=np.fromfile(d/'Info_counts.bin',dtype='<u4').reshape(meta['ticks']+1,4)
    tr=np.memmap(d/'native_transitions.bin',dtype='<i4',mode='r',shape=(meta['ticks']+1,4,512,2))
    ip=np.memmap(d/'Info_coordinates.bin',dtype='<i4',mode='r',shape=(meta['ticks']+1,4,64))
    indices=np.fromfile(d/'selected_case_indices.bin',dtype='<i4')
    assert np.max(nc)<=512 and np.max(ic)<=64
    return meta,masks,metrics,nc,ic,tr,ip,indices

def compare_reference(pilot,reference,selected):
    meta,masks,metrics,nc,ic,tr,ip,indices=pilot;c=int(indices[selected]);mask=int(masks[c]);count=0
    lines=[json.loads(s) for s in (D/'reference'/f'mask{mask}_trace.jsonl').read_text().splitlines()[:-1]]
    old=ROOT/'figs/robustness/unregistered_sp31_third_pulse_pilot'/f'mask{mask}_trace.jsonl'
    assert (D/'reference'/f'mask{mask}_trace.jsonl').read_bytes()==old.read_bytes()
    with reference.open('rb') as fh:
        for row in range(6145):
            rr,ns,ni=struct.unpack('<3I',fh.read(12));assert rr==row
            segments=np.frombuffer(fh.read(ns*12),dtype='<i4').reshape(ns,3).tolist()
            info=np.frombuffer(fh.read(ni*4),dtype='<i4').tolist()
            pairs=sorted(tr[row,selected,:int(nc[row,selected])].tolist())
            assert all(pairs[i][0]<pairs[i+1][0] for i in range(len(pairs)-1))
            assert pairs and pairs[-1][1]==0
            got=[[a,pairs[j+1][0],v] for j,(a,v) in enumerate(pairs[:-1]) if v]
            assert got==segments,(mask,row,'whole native state')
            gotinfo=sorted(ip[row,selected,:int(ic[row,selected])].tolist())
            assert gotinfo==info,(mask,row,'whole voted special Info')
            v=lines[row];expected=[v['GF_sites'],0 if not v['GF_sites'] else meta['HI']-v['GF_left'],v['GF_right_exclusive'],v['Flag1_sites'],v['WF1_sites'],v['Flag2_sites'],v['WF2_sites'],v['Info_ones'],0]
            assert metrics[c,row].tolist()==expected,(mask,row,'all row metrics')
            count+=1
        assert not fh.read(1)
    return dict(mask=mask,all_rows=6145,whole_native_and_voted_Info_states_equal=True,
        exact_frozen_pilot_trace_unchanged=True,reference_state_sha256=sha(reference),reference_trace_sha256=sha(D/'reference'/f'mask{mask}_trace.jsonl'))

def main():
    start=time.monotonic();pilot=load(D/'pilot');assert pilot[1].tolist()==[0,2047,2048,4095] and pilot[0]['ticks']==6144
    ref=D/'reference';ref.mkdir(exist_ok=True);source=ref/'sp31_third_reference.c';source.write_text(generated_reference());binary=ref/'third_reference'
    p=subprocess.run(['gcc','-O3','-std=c11','-Wall','-Wextra',str(source),'-o',str(binary)],capture_output=True,text=True)
    (ref/'build.log').write_text(p.stdout+p.stderr);assert p.returncode==0
    def run(mask):
        trace=ref/f'mask{mask}_trace.jsonl';state=ref/f'mask{mask}_state.bin'
        with trace.open('w') as fh:p=subprocess.run([str(binary),str(mask),'6144',str(state)],stdout=fh,stderr=subprocess.PIPE,text=True)
        (ref/f'mask{mask}_stderr.log').write_text(p.stderr);assert p.returncode==0
    with ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(run,(0,2047,2048,4095)))
    comparisons=[compare_reference(pilot,ref/f'mask{mask}_state.bin',i) for i,mask in enumerate((0,2047,2048,4095))]
    all_path=D/'all4096';allresult=None
    if (all_path/'metadata.json').exists():
        allrun=load(all_path);meta,masks,metrics,nc,ic,tr,ip,indices=allrun
        assert masks.tolist()==list(range(4096)) and meta['ticks']==6144
        assert np.all(metrics[:,0,0]==7680) and np.all(metrics[:,-1,0]==3584)
        assert np.all(metrics[:,-1,1]==meta['HI']-152064) and np.all(metrics[:,-1,2]==155648)
        assert np.all(metrics[:,-1,3]==1024) and not np.any(metrics[:,-1,4:7])
        assert np.all(np.max(metrics[:,:,1],axis=1)==meta['HI']-144896)
        assert np.all(np.max(metrics[:,:,2],axis=1)==155648)
        for i,c in enumerate(indices):
            assert int(masks[c])==int(pilot[1][i]) and np.array_equal(metrics[c],pilot[2][i])
            assert np.array_equal(nc[:,i],pilot[3][:,i]) and np.array_equal(ic[:,i],pilot[4][:,i])
            for row in range(6145):
                assert sorted(tr[row,i,:int(nc[row,i])].tolist())==sorted(pilot[5][row,i,:int(nc[row,i])].tolist())
                assert sorted(ip[row,i,:int(ic[row,i])].tolist())==sorted(pilot[6][row,i,:int(ic[row,i])].tolist())
        allresult=dict(masks=4096,all_row_records=4096*6145,every_boundary_guard_zero=True,
            every_endpoint_whole_native_template=[149,152],every_GF_hull=[144896,155648],
            every_GF_width_change=-4096,selected_pilot_whole_states_reproduced=True,
            physical_reachability_of_individual_assignments_proved=False)
    assets={str(p.relative_to(ROOT)):sha(p) for p in sorted(D.rglob('*')) if p.is_file() and p.name!='exploration_receipt.json'}
    result=dict(proposal='SP31',scope='Exploratory exact integer native/Info evaluation; physical source proof is J238; no general repair/iid theorem',
        checker_sha256=sha(__file__),CUDA_source_sha256=sha(S/'sp31_third_dense.cu'),
        frozen_factor_sha256=sha(S.parent/'sp31_two_flag2_sources.c'),frozen_third_wrapper_sha256=sha(S/'sp31_third_enclosure_cases.c'),
        source_certificate_sha256=sha(ROOT/'figs/robustness/SP31_third_source_enclosure_certificate.json'),
        pilot_whole_state_replays=comparisons,all4096_execution=allresult,assets_sha256=assets,
        no_new_rule_or_constant_change=True,active_G17_modified=False,global_reliability_established=False,seconds=time.monotonic()-start)
    (D/'exploration_receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,selected_whole_state_rows=4*6145,all4096_execution=allresult,seconds=result['seconds'])),flush=True)
if __name__=='__main__':main()
