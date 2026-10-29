"""Universal symbolic slot/index certificate plus separately sampled values."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import sys

import packed_window_slots as w

ROOT=Path(__file__).resolve().parents[4]
OLD=ROOT/'Report/proofs/gray_counterexamples/unregistered_gbd0'
sys.path.insert(0,str(OLD))
import packed_window as old


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    a=p.parse_args()
    cases=ports=0;used=set();end=None
    for q in range(5):
        for c in (-1,0,1):
            for phase in range(20):
                for stride in (1,5):
                    for count in range(21):
                        cases+=1
                        for i,group in enumerate(w.targets(q,c,phase,stride,count)):
                            chunk,bit=divmod(phase+stride*i,20)
                            u=w.SLOTS[q]+c-2+chunk
                            assert len(set((d,s) for d,s,_ in group))==5
                            for h,(d,slot,b) in enumerate(group):
                                assert d==u+w.SLOTS[h]
                                assert slot==w.INVERSE[h]
                                assert d+w.SLOTS[slot]==u
                                assert b==bit
                                assert -8<=d<=8 and 0<=slot<5
                                assert 20*chunk+b==phase+stride*i
                                ports+=1;used.add(d)
                                if d==8:end=dict(q=q,centre=c,phase=phase,
                                                stride=stride,count=count,output_bit=i)
    assert used==set(range(-7,9)) and end is not None
    for v in range(32):
        bits=[v>>i&1 for i in range(5)]
        assert w.majority_word(bits)==int(sum(bits)>=3)
    # Full raw values independent in all five slots: these measured cases
    # supplement, but do not replace, the preceding all-value identity.
    rng=random.Random(81921041)
    full_raw=coherent=0
    for _ in range(320):
        raw={d:tuple(rng.getrandbits(340) for s in range(5)) for d in range(-8,9)}
        args=(rng.randrange(5),rng.choice((-1,0,1)),rng.randrange(17),
              rng.randrange(20),rng.choice((1,5)),rng.randrange(21))
        assert w.read_window(raw,*args)==w.composed_window(raw,*args)
        full_raw+=1
        logical={d:rng.getrandbits(340) for d in range(-10,11)}
        raw=w.coherent_raw(logical)
        assert w.read_window(raw,*args)==w.coherent_reference(logical,*args)
        coherent+=1
    # Exact counterexample to using only slot0 at every old GBD0 input.
    ctrl=dict(q=0,centre=0,lane=0,phase=0,stride=1,count=1)
    raw={d:[0]*5 for d in range(-8,9)}
    for d,slot,bit in w.targets(0,0,0,1,1)[0][1:4]:
        raw[d][slot]|=1<<bit
    corrected=w.read_window(raw,**ctrl)
    projected=old.read_window({d:v[0] for d,v in raw.items()},**ctrl)
    assert corrected==1 and projected==0
    witness=dict(controls=ctrl,
                 replacements=[dict(physical=d,slot=s,value=v)
                               for d,slots in raw.items() for s,v in enumerate(slots) if v],
                 corrected=corrected,slot0_projection=projected,
                 error_history=False,Gray_counterexample=False)
    # Exact radius8 sensitivity with the true matching raw port.
    ctrl={k:v for k,v in end.items() if k!='output_bit'}
    i=end['output_bit'];group=w.targets(**ctrl)[i]
    singled=next(x for x in group if x[0]==8)
    others=[x for x in group if x!=singled]
    raw={d:[0]*5 for d in range(-8,9)}
    for d,s,b in others[:2]:raw[d][s]|=1<<b
    before=w.read_window(raw,lane=0,**ctrl)
    d,s,b=singled;raw[d][s]|=1<<b
    after=w.read_window(raw,lane=0,**ctrl)
    assert (before^after)&(1<<i)
    invalid=0
    # All unused patterns of this finite input-control encoding.
    raw={d:[(1<<340)-1]*5 for d in range(-8,9)}
    for name,values,fixed in [
        ('q',range(8),dict(q=0,centre=0,lane=0,phase=0,stride=1,count=1)),
        ('centre',range(-2,2),dict(q=0,centre=0,lane=0,phase=0,stride=1,count=1)),
        ('lane',range(32),dict(q=0,centre=0,lane=0,phase=0,stride=1,count=1)),
        ('phase',range(32),dict(q=0,centre=0,lane=0,phase=0,stride=1,count=1)),
        ('stride',range(8),dict(q=0,centre=0,lane=0,phase=0,stride=1,count=1)),
        ('count',range(32),dict(q=0,centre=0,lane=0,phase=0,stride=1,count=1))]:
        for v in values:
            ctrl=dict(fixed);ctrl[name]=v
            if not w.valid(**ctrl):
                assert w.read_window(raw,**ctrl)==0;invalid+=1
    proof=Path(__file__).with_name('GBD1_CORRECTED_PACKED_WINDOW_SOURCE_PORTS.md')
    r=dict(schema='GBD1-slot-1',passed=True,Q=w.Q,U=w.U,lambda_=24,c=104,
           universal_matching_slot_formula=True,
           inverse_slot=w.INVERSE,control_coordinate_cases=cases,
           physical_slot_bit_identities=ports,majority_truth_cases=32,
           exact_stencil=[-7,8],exact_radius=8,
           lower_source_port_refinement=True,
           controller_head_binding_proved=False,
           selected_independent_raw_comparisons=full_raw,
           selected_coherent_reference_comparisons=coherent,
           all_unused_control_pattern_checks=invalid,
           slot0_projection_failure=witness,
           radius8_cofactor=end,
           finite_circuit_gate_bound=old.circuit_upper_bound(),
           source_hashes={str(p.relative_to(ROOT)):sha(p) for p in
                         (Path(__file__),Path(w.__file__),proof)},
           full_rule=False,own_programme=False,actual_packing=False,
           runtime_bound=False,physical_period=False,noise_theorem=False,
           Gray_refutation=False,iid_failure=False,shorter_U=False)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r,indent=2))


if __name__=='__main__':main()
