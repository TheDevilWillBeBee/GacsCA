#!/usr/bin/env python3
"""UNREGISTERED conditional native-map diagnostic, not a physical lift proof.

Assumes paddingInfo4000/4192=0, upper Head.p=0 and the same derived capture
shift at each lower period. These continuing physical premises are not yet
certified. Native flag words are normalized to their low bit; actual own
beta input-normalization equivalence remains to be proved separately.
"""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
import gray_token_gather_v7 as k


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def label(g):return int(0<=g<17)


def clean(g,n):return dict(addr=g%k.Q,age=n,f1=0,f2=0,wf1=0,wf2=0)


def raw_record(row,g,j):
    source=g+j;fields=[row[source][n] for n in k.NATIVE_NAMES]
    shift=((j>0)-(j<0))*(label(source)-label(g))
    if shift==1:fields=fields[1:]+[0]  # Head.p0 premise.
    elif shift==-1:fields=[0]+fields[:-1]  # padding0 premise.
    raw=dict(zip(k.NATIVE_NAMES,fields))
    projected={name:value&(k.Q-1 if name=='addr' else k.SMALL_MASK if name=='age' else 1)
        for name,value in raw.items()}
    return raw,projected,shift


def main():
    started=time.monotonic();directory=ROOT/'figs/gray_counterexamples'
    lo=-128;hi=145;row={g:clean(g,0) for g in range(lo,hi)}
    stages=[];first=None;flag2=[]
    for n in range(16):
        output={}
        for g in range(lo+5,hi-5):
            inputs={j:raw_record(row,g,j)[1] for j in range(-5,6)}
            output[g]=k.predecessor.scalar_native(inputs)
        # Dependencies cannot reach the exterior truncation: damaged native
        # support moves at most5 per map step, and static routing jumps have
        # support only within five colonies of0/17.
        outside=[g for g,c in output.items() if c!=clean(g,n+1)]
        assert not outside or min(outside)>lo+10 and max(outside)<hi-10
        for g in range(lo,lo+5):output[g]=clean(g,n+1)
        for g in range(hi-5,hi):output[g]=clean(g,n+1)
        if first is None:
            bad=[g for g,c in output.items() if c['age']!=n+1]
            if bad:
                g=bad[0];first=dict(output_epoch=n+1,g=g,output=output[g],
                    inputs={str(j):dict(raw=raw_record(row,g,j)[0],projected=raw_record(row,g,j)[1],
                        capture_shift=raw_record(row,g,j)[2]) for j in range(-5,6)})
        flag2.append([g for g in range(0,17) if output[g]['f2']])
        stages.append(dict(epoch=n+1,native=[output[g] for g in range(-6,23)],
            right_edge_Ages=[output[g]['age'] for g in (13,14,15,16)],
            maximum_Age=max(c['age'] for c in output.values()),
            all_Address_canonical=all(c['addr']==g%k.Q for g,c in output.items()),
            differing_native_columns=outside))
        row=output
    r=dict(name='conditional continuing distorted-bank native map probe',Q=k.Q,U=k.U,
        lambda_original=24,c_original=104,epochs=16,checker_sha256=digest(__file__),
        source_sha256=digest(k.__file__),native_source_sha256=digest(k.predecessor.__file__),
        first_noncommon_Age=first,Flag2_columns_inside_per_epoch=flag2,stages=stages,
        padding_and_head_zero_continuing_physical_premises=True,
        beta_raw_flag_word_normalization_equivalence_assumed=True,
        actual_full_GMW7_stroboscopic_map_proved=False,
        Gray_or_iid_refuted=False,active_rule_modified=False,
        elapsed_seconds=time.monotonic()-started)
    path=directory/'GMW7_conditional_clock_upper_native_probe.json'
    path.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(dict(first_noncommon_Age=first,right_edge_Ages=[s['right_edge_Ages'] for s in stages],
        Flag2_columns_inside=flag2,receipt_sha256=digest(path),
        actual_full_GMW7_stroboscopic_map_proved=False)))


if __name__=='__main__':main()
