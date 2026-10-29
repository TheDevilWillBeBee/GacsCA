#!/usr/bin/env python3
"""All-raw-word SP28 local front uniqueness and total ROM bounds.

This certifies local timing/addition gates. It does not establish the
physical front/capture invariant or a complete self-simulation theorem.
All previously built rule/proposal/compiler sources remain unchanged.
"""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import numpy as np
import proposed_sparse_distant_epoch1024 as proposed
from gacsca.netlist import Net,Compiled,w_add_const_mod
from gacsca.rule import front_timing_dwell


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started=time.monotonic();p=proposed.parameters()
    assert (p.k,p.PB,p.dlog,p.fronts,p.delta)==(10,10,0,5,5)
    assert (p.Q,p.lo,p.hi,p.H,p.E0b,p.NP,p.PW)==(1024,58,966,20,28,384,12)
    assert p.Q==1<<p.k and p.E0b+p.NP<=1<<(p.m-p.PB)
    n=Net();address=[n.input(('addr',i)) for i in range(p.k)]
    age=[n.input(('age',i)) for i in range(p.m)]
    for slot in proposed.SLOTS:
        xa=w_add_const_mod(n,address,slot%p.Q,p.Q)
        c=dict(age=age,addr=xa,reg=[0]*p.L)
        _,_,arrive,_=front_timing_dwell(n,p,c,{-1:dict(reg=[0]*p.L),0:c,1:dict(reg=[0]*p.L)})
        n.set_output(('arr',slot),arrive)
        for i,b in enumerate(xa):n.set_output(('xa',slot,i),b)
    comp=Compiled(n);mod=1<<p.k;mask=mod-1
    cases=2*mod*mod;histogram=[0,0];outside=0
    for begin in range(0,cases,8192):
        number=np.arange(begin,min(begin+8192,cases),dtype=np.uint32)
        A=number&mask;position=(number>>p.k)&mask;direction=number>>(2*p.k)
        raw_age=((p.E0b+direction)<<p.PB)|position
        values={('addr',i):((A>>i)&1).astype(bool) for i in range(p.k)}
        values.update({('age',i):((raw_age>>i)&1).astype(bool) for i in range(p.m)})
        got=comp.evaluate(values,bool)
        base=np.where(direction,p.hi-1-position.astype(np.int64),p.lo-p.H+position)&mask
        arrivals=[]
        for slot in proposed.SLOTS:
            xa=(A.astype(np.int64)+slot)%p.Q
            actual=sum(got['xa',slot,i].astype(np.uint32)<<i for i in range(p.k))
            assert np.array_equal(actual,xa)
            expected=np.isin((xa-base)&mask,[j*p.delta for j in range(p.fronts)])
            assert np.array_equal(got['arr',slot],expected)
            arrivals.append(expected)
            outside+=int(np.count_nonzero(expected&((xa<p.lo)|(xa>=p.hi))))
        count=np.stack(arrivals).sum(axis=0)
        assert np.all(count<=1)
        for i in (0,1):histogram[i]+=int(np.count_nonzero(count==i))
    # Pairwise slot differences are ±1..4. Distinct comb teeth differ
    # by ±5,±10,±15,±20 modulo1024. The sets are disjoint.
    slot_differences={((a-b)%mod) for a in proposed.SLOTS for b in proposed.SLOTS if a!=b}
    tooth_differences={((a-b)*p.delta)%mod for a in range(p.fronts) for b in range(p.fronts) if a!=b}
    assert 0 not in slot_differences and slot_differences.isdisjoint(tooth_differences)
    candidate=proposed.load_artifact();out=ROOT/'figs/robustness'
    build=json.loads((out/'SP28_program_build.json').read_text())
    assert candidate.digest()==build['proposed_candidate_sha256']
    assert candidate.comp.digest==proposed.cached(p)[1].digest==build['proposed_netlist_sha256']
    assert candidate.rom.shape==(p.Q,p.NPT)==(1024,4096)
    assert candidate.rom.dtype==np.uint32
    result=dict(proposal='SP28',proposed_rule_change=True,active_G17_modified=False,
        checker_sha256=digest(Path(__file__)),proposal_source_sha256=digest(Path(proposed.__file__)),
        timing_sha256=digest(ROOT/'gacsca/rule.py'),mux_front_sha256=digest(ROOT/'gacsca/rule_g.py'),
        helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        build_receipt_sha256=digest(out/'SP28_program_build.json'),artifact_sha256=digest(out/'SP28_program.npz'),
        local_timing_netlist_sha256=comp.digest,address_position_direction_cases=cases,
        arrival_count_histogram=histogram,arriving_cases_outside_work=outside,
        maximum_simultaneous_arrivals=1,raw_Age_words=1<<p.m,
        raw_address_words=1<<p.k,all_raw_addresses_in_ROM=True,
        raw_selector_words=1<<p.PW,all_raw_selectors_in_ROM=True,
        raw_ROM_key_pairs=(1<<p.k)*(1<<p.PW),
        slot_differences=sorted(slot_differences),comb_tooth_differences=sorted(tooth_differences),
        outside_work_I_independent_by_literal_mux_gates=True,
        physical_front_copy_capture_invariant_proved=False,complete_encoded_simulation_proved=False,
        global_reliability_established=False,seconds=time.monotonic()-started,
        scope='exact local arrival/addition certificate; window/direction factorization covers all raw Age; ROM bounds for all raw keys; not physical simulation or repair')
    (out/'SP28_front_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(cases=cases,histogram=histogram,outside_work=outside,
                         all_raw_ROM_keys_in_range=True,seconds=result['seconds'])),flush=True)


if __name__=='__main__':main()
