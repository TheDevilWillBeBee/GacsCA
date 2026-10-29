"""Conditional source/store bootstrap for a new dense16Q SP30 history.

This uses the unchanged frozen factor and full-net cofactors. The driver
does not itself prove the physical mail/store or infinite-line lifts.
Until a written composition discharges those premises, its pulse rows
are conditional evidence, not an actual-rule counterexample.
"""
from pathlib import Path
import hashlib,json,subprocess,sys,time
import numpy as np

ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'Report/proofs'))
from gacsca.netlist import Net,Compiled
import proposed_sparse_signal_reservation1024 as proposed
from check_signal_reservation1024_second_signal import blocked

OUT=ROOT/'figs/robustness';FIELDS=('addr','age','f1','wf1')

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def bits(p,field,value):
    width={'addr':p.k,'age':p.m,'f1':1,'wf1':1}[field]
    return [(value>>b)&1 for b in range(width)]

def canonical(p,j,period):
    return {f:bits(p,f,{'addr':j%p.Q,'age':p.age_code(period),'f1':0,'wf1':0}[f]) for f in FIELDS}

def unknown(p):return {f:[None]*len(bits(p,f,0)) for f in FIELDS}

def fixed_word(v):
    return sum(b<<i for i,b in enumerate(v)) if all(b in (0,1) for b in v) else None

def signal_and_outputs(p,period,L,R,model):
    phases={(r['field'],r['bit']):r['address'] for r in proposed.dependency_table(p)}
    strips=(((L-1)*p.Q,L*p.Q-512),(R*p.Q-512,R*p.Q))
    records={};native={}
    # Far-right canonical closure; no route can see a noncanonical source.
    stop=max(R,model['right_canonical_from'])+38
    receivers=[*range(L-44,L-1),*range(R,stop)]
    def value(j,f,b):
        if period==0 or j<=model['left_canonical_through'] or j>=model['right_canonical_from']:
            return canonical(p,j,period)[f][b]
        return model['records'].get(j,unknown(p))[f][b]
    for j in receivers:
        class Captured(Net):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,f,b=key;col=j+d
                    if f in FIELDS:
                        if blocked(strips,j,d,phases[f,b],p.Q):return 0
                        v=value(col,f,b)
                        if v is not None:return v
                        return super().input(('upper',col,f,b))
                    if period==0 and f in ('f2','wf2','packet_valid','service_valid','backward_pressure'):
                        return 0
                return super().input(key)
        n,_=proposed.full_net(p,Captured)
        result={f:[n.outputs['y',f,b] if n.outputs['y',f,b] in (0,1) else None
                   for b in range(len(bits(p,f,0)))] for f in FIELDS}
        native[j]=result
        flag=result['f1'][0]
        records[j]=dict(colony=j,Flag1=flag,native_words={f:fixed_word(result[f]) for f in FIELDS},
            native_bit_domains=result,netlist_sha256=Compiled(n).digest)
    # The distant homogeneous prefixes/suffixes are supplied by a
    # conditional canonical cofactor, not an assumed sampled trajectory.
    for j in (L-44,stop-1):
        assert native[j]==canonical(p,j,period+1),(period,j,native[j])
    return records,native

def condition(cols):
    return '('+' || '.join(f'col=={j}' for j in sorted(cols))+')' if cols else '0'

def wrapper(period,L,R,signals,dest):
    source=(OUT/'unregistered_translation_force2048/generated.c').read_text()
    ones={j for j,r in signals.items() if r['Flag1']==1}
    free={j for j,r in signals.items() if r['Flag1'] is None}
    seedlo=min({L-1,L-4,*ones,*free})
    seedhi=max({R,*[j+1 for j in ones|free]})
    initial='        info[x]=residue==509?(128<=col && col<=133):\n'\
        '            residue!=1021?0:(col<72 || col>=152 || col==123)?2:\n'\
        '            ((124<=col && col<=126)||(134<=col && col<=151));'
    changes={
        '#include "../SP29_third_pulse_domains_factor_generated.c"':
            f'#include "{OUT}/SP29_third_pulse_domains_factor_generated.c"',
        'initial_a=128*Q-512,initial_b=134*Q,initial_lo=127*Q':
            f'initial_a={L}*Q-512,initial_b={R}*Q,initial_lo={L-1}*Q',
        'lo=72*Q-margin,hi=152*Q+margin':f'lo={seedlo}*Q-margin,hi={seedhi}*Q+margin',
        'duration=2048;info_mode=100':f'duration=2048;info_mode={200+period}',
        '/tmp/SP30_translation_class_force2048_final.bin':f'/tmp/SP30_16Q_bootstrap_p{period}_final.bin',
        initial:f'        info[x]=residue==509?({L}<=col && col<{R}):\n'
            f'            residue!=1021?0:{condition(free)}?2:{condition(ones)};'}
    for a,b in changes.items():assert source.count(a)==1,a;source=source.replace(a,b)
    path=dest/'generated.c';path.write_text(source)
    return path,(seedlo*pQ,seedhi*pQ) if (pQ:=1024) else None,sorted(ones),sorted(free)

def pulse(period,L,R,signals,dest):
    started=time.monotonic();dest.mkdir(exist_ok=True)
    source,seed,ones,free=wrapper(period,L,R,signals,dest)
    exe=Path(f'/tmp/SP30_16Q_bootstrap_p{period}')
    built=subprocess.run(['cc','-O3','-std=c11','-Wall','-Wextra','-Werror','-Wno-parentheses',
        str(source),'-o',str(exe)],capture_output=True,text=True)
    (dest/'compile.log').write_text(built.stdout+built.stderr)
    assert built.returncode==0,built.stderr
    log=dest/'trace.jsonl'
    with log.open('w') as stream:run=subprocess.run([str(exe),'0'],stdout=stream,stderr=subprocess.PIPE,text=True)
    (dest/'stderr.log').write_text(run.stderr)
    rows=[json.loads(line) for line in log.read_text().splitlines()]
    if run.returncode!=0:
        receipt=dict(period=period,initial_L_R=[L,R],exit_code=run.returncode,
            witness=rows[-1] if rows else None,finite_domain_complete=False,
            actual_rule_history_proved=False,global_reliability_established=False)
        (dest/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print(json.dumps(receipt),flush=True);return None
    summary=rows.pop();assert summary['certificate_complete'] and len(rows)==6145
    raw=Path(f'/tmp/SP30_16Q_bootstrap_p{period}_final.bin').read_bytes();N=262144
    assert len(raw)==11*N
    state=np.frombuffer(raw,np.uint8,8*N).reshape(8,N).copy()
    code=np.frombuffer(raw,np.uint16,N,8*N).copy()
    info=np.frombuffer(raw,np.uint8,N,10*N).copy()
    asset=dest/'endpoint.npz';np.savez_compressed(asset,native=state,code=code,Info=info)
    final=rows[-1];a,b=final['left'],final['right_exclusive'];x=np.arange(N)
    assert (a+512)%1024==b%1024==0
    nextL,nextR=(a+512)//1024,b//1024
    assert np.array_equal(state[0],(a<=x)&(x<b))
    assert np.array_equal(state[1],((a-512<=x)&(x<a))|((b-512<=x)&(x<b)))
    assert not state[2:].any() and not code.any()
    assert nextL<nextR and nextL<=L and nextR<=R-1
    hull=[min(r['left'] for r in rows),max(r['right_exclusive'] for r in rows)]
    receipt=dict(period=period,initial_L_R=[L,R],endpoint_L_R=[nextL,nextR],
        initial_wrong_GF_sites=(R-L)*1024+512,endpoint_wrong_GF_sites=b-a,all_row_GF_hull=hull,
        native_quiet_template=True,MF509_one_colonies=list(range(L,R)),
        MF1021_one_colonies=ones,MF1021_free_colonies=free,seed_interval=seed,
        finite_domain_complete=True,summary=summary,source_sha256=sha(source),
        factor_sha256=sha(OUT/'SP29_third_pulse_domains_factor_generated.c'),
        executable_sha256=sha(exe),log_sha256=sha(log),asset_sha256=sha(asset),
        physical_source_store_and_Z_lift_proved=False,actual_rule_history_proved=False,
        global_reliability_established=False,elapsed_seconds=time.monotonic()-started)
    (dest/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ('period','initial_L_R','endpoint_L_R',
        'endpoint_wrong_GF_sites','all_row_GF_hull','MF1021_free_colonies','elapsed_seconds')}),flush=True)
    return receipt

def next_model(p,period,L,R,result,native):
    nextL,nextR=result['endpoint_L_R']
    assert result['all_row_GF_hull'][0]>=L*p.Q-7616
    assert result['all_row_GF_hull'][1]<=R*p.Q
    assert nextL==L-6
    records={}
    # Whole late frames strictly outside the hull supply all four words.
    for j,out in native.items():
        if j>=R+1:records[j]=out
    # Early normal GF/F1 holds at edgeR have their20-site reserve;
    # entire late Age/WF words are deliberately left unknown there.
    records[R]=unknown(p)
    for f in ('addr','f1'):records[R][f]=native[R][f]
    # Recovered columns have no eligible new GF/F1 destination kind.
    for j in range(nextR,R):
        records[j]=unknown(p)
        for f in ('addr','f1'):records[j][f]=bits(p,f,0)
    # Protected left edge has the449-site GF/F1 reserve.
    records[L-8]=unknown(p)
    for f in ('addr','f1'):records[L-8][f]=native[L-8][f]
    right=max(records)+1
    while right-1 in records and records[right-1]==canonical(p,right-1,period+1):
        records.pop(right-1);right-=1
    left=L-9
    for j in [v for v in records if v<=left]:records.pop(j)
    zero_to=nextR-1
    while zero_to+1<right and fixed_word(records.get(zero_to+1,unknown(p))['addr'])==0:zero_to+=1
    return dict(left_canonical_through=left,right_canonical_from=right,records=records,
        right_zero_GF_prefix=[nextR,zero_to],upper_clock=period+1)

def main(periods=7):
    started=time.monotonic();p=proposed.parameters();assert (p.Q,p.U)==(1024,475136)
    campaign=OUT/'unregistered_16Q_source_bootstrap';campaign.mkdir(exist_ok=True)
    L,R=128,143
    model=dict(left_canonical_through=127,right_canonical_from=144,records={})
    receipts=[]
    for period in range(periods):
        dest=campaign/f'p{period}';dest.mkdir(exist_ok=True)
        signals,native=signal_and_outputs(p,period,L,R,model)
        (dest/'source_model.json').write_text(json.dumps(model,indent=2)+'\n')
        (dest/'cofactors.json').write_text(json.dumps(list(signals.values()),indent=2)+'\n')
        print(json.dumps(dict(period=period,stage='cofactors',L_R=[L,R],
            ones=[j for j,r in signals.items() if r['Flag1']==1],
            free=[j for j,r in signals.items() if r['Flag1'] is None])),flush=True)
        result=pulse(period,L,R,signals,dest)
        if result is None:break
        model=next_model(p,period,L,R,result,native)
        (dest/'next_source_model.json').write_text(json.dumps(model,indent=2)+'\n')
        print(json.dumps(dict(period=period,stage='next_source',
            right_zero_GF_prefix=model['right_zero_GF_prefix'],
            left_canonical_through=model['left_canonical_through'],
            right_canonical_from=model['right_canonical_from'])),flush=True)
        receipts.append(result);L,R=result['endpoint_L_R']
    result=dict(name='New16Q row conditional SP30 source/store bootstrap',
        Q=p.Q,U=p.U,T_wf=p.T_wf,initial_L_R=[128,143],
        completed_periods=len(receipts),pulse_receipts=receipts,
        checker_sha256=sha(__file__),candidate_sha256=proposed.load_artifact().digest(),
        source_dependencies_sha256={name:sha(ROOT/name) for name in (
            'Report/proofs/proposed_sparse_signal_reservation1024.py',
            'Report/proofs/check_signal_reservation1024_second_signal.py',
            'gacsca/netlist.py')},
        actual_original_error_classification_proved=False,
        physical_variable_width_protocol_and_store_lifts_proved=False,
        actual_rule_history_or_global_reliability_proved=False,
        active_rule_or_frozen_SP30_changed=False,elapsed_seconds=time.monotonic()-started)
    (campaign/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('completed_periods',
        'actual_rule_history_or_global_reliability_proved','elapsed_seconds')}),flush=True)

if __name__=='__main__':main(int(sys.argv[1]) if len(sys.argv)>1 else 7)
