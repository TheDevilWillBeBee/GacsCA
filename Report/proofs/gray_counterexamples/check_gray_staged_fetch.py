#!/usr/bin/env python3
"""Exact GR1 match-courier sublemma, with coherent native/front controls.

This proves neither physical E0 robustness nor a complete period/frame lift.
The all-raw outside-key irrelevance argument is stated explicitly in the
receipt; the exact netlist route checks certify its elementary constituents.
"""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
import numpy as np
from gacsca import rule_g
from gacsca.netlist import Net,const_word,w_eq
import gray_staged_rule as proposed


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    start=time.monotonic(); out=ROOT/'figs/gray_counterexamples'
    candidate=proposed.load_artifact(); p=candidate.p
    assert p.MP%2==1 and p.PL==p.hi-p.lo+p.H==512
    assert not np.any(candidate.rom[:p.lo]) and not np.any(candidate.rom[p.hi:])
    equality_count=0; cases=0; route_checks=0
    path=[p.hi-1-t for t in range(p.PL)]
    assert len(set(path))==p.PL and path[-1]==p.lo-p.H
    for tick,center0 in enumerate(path):
        age=p.E0+p.MP*p.PL+tick
        for front in range(p.fronts):
            center=center0+front*p.delta
            previous=center if tick==0 else center+1
            assert 2<=center and center+2<p.Q
            for holder in rule_g.SLOTS:
                # One coherent register vector at the previous comb front.
                # Other logical-cell registers remain independent free bits.
                n=Net(); R=[n.input(('R',b)) for b in range(p.L)]
                I=[n.input(('I',b)) for b in range(p.IW)]
                local_cache={}
                def lv(x,f,b=0):
                    absolute=center+holder+x
                    if f=='reg' and absolute==previous: return R[b]
                    key=absolute,f,b
                    if key not in local_cache:
                        local_cache[key]=n.input(('other',)+key)
                    return local_cache[key]
                actual=rule_g._five_front(n,p,I,lv,const_word(age,p.m),
                                         const_word((center+holder)%p.Q,p.k))
                match=w_eq(n,R[:p.k],const_word(center,p.k)) if p.lo<=center<p.hi else 0
                expected=[n.MUX(match,I[b-p.k],R[b])
                          if p.k<=b<p.k+p.IW else R[b] for b in range(p.L)]
                assert actual['reg']==expected,(tick,front,holder,'register route')
                for field in ('pend','pkind','pval'):
                    assert not any(actual[field]),(tick,front,holder,field)
                assert [n.outputs['laddr',b] for b in range(p.k)]==const_word(center,p.k)
                assert [n.outputs['psel',b] for b in range(p.PW)]==R[p.k:p.k+p.PW]
                assert n.outputs['arrive',0]==1
                equality_count+=p.L+sum(len(actual[f]) for f in ('pend','pkind','pval'))+p.k+p.PW+1
                route_checks+=1; cases+=1
        if tick%128==0: print(json.dumps(dict(match_tick=tick,checked=cases)),flush=True)
    # This is the complete finite geometry, not a sampled key campaign.
    # Before its unique hit the selector is unchanged; after the hit the
    # address key is unchanged and the path never revisits it. Consequently
    # overwriting the overlapping selector/I buffer cannot change a later hit.
    work_key_checks=0; zero_key_checks=0
    for key in range(p.Q):
        hits=[tick for tick,center in enumerate(path) if center==key and p.lo<=center<p.hi]
        if p.lo<=key<p.hi:
            assert hits==[p.hi-1-key]
            work_key_checks+=1
        else:
            assert not hits
            assert not np.any(candidate.rom[key])
            zero_key_checks+=1
    result=dict(Q=p.Q,U=p.U,width=candidate.W,candidate='GR1',
        candidate_sha256=candidate.digest(),netlist_sha256=candidate.comp.digest,
        checker_sha256=digest(__file__),proposal_sha256=digest(proposed.__file__),
        inherited_front_sha256=digest(ROOT/'gacsca/rule_g.py'),
        inherited_timing_sha256=digest(ROOT/'gacsca/rule.py'),
        build_receipt_sha256=digest(out/'GR1_program_build.json'),
        asset_sha256=digest(out/'GR1_program.npz'),
        exact_symbolic_front_cases=cases,exact_output_and_lookup_equalities=equality_count,
        arbitrary_register_bits_per_case=p.L,arbitrary_instruction_bits_per_case=p.IW,
        coherent_copy_holder_routes=route_checks,match_path=path,
        work_keys_with_unique_hit=work_key_checks,zero_row_keys_without_hit=zero_key_checks,
        match_start=p.hi-1,match_end=p.lo-p.H,next_forward_start=p.lo-p.H,
        correct_work_key_fetch_proved_conditionally=True,
        outside_work_key_instruction_irrelevance_proved=True,
        outside_key_proof='For every raw input, at most one of the five logical slots arrives: their Addresses span four sites, while comb centers are five apart. If no slot arrives, every front output is zero. If one arrives, output laddr is its selected Address. When laddr is outside [lo,hi), all instruction kind gates and matched are zero, so registers only carry and pending outputs are zero, independently of I. Every other GR1 output and lookup output is independent of I. All outside ROM rows are zero. Thus an unfetched instruction for an outside key cannot affect the computed upper output.',
        work_key_proof='With coherent copies and canonical holder geometry/common computed clock throughout MP, the exact checks give the same register update and lookup on all five holders. Front0 visits every work key exactly once, using the unchanged key selector before that hit, and replaces its complete I buffer with ROM(key,selector). Its address key is never overwritten and it is not revisited. The next forward page starts at the same final center and carries that buffer.',
        hypotheses=['coherent five physical copies of each compared compact-front register before the match page',
            'canonical holder Address and common correct computed Age throughout the noiseless match page',
            'external physical lookup supplies the pinned ROM instruction selected by laddr/psel',
            'the preceding abstract programme has populated front0 with its proved lookup key'],
        not_proved=['preceding physical frame and Gather refinement',
            'native controls/copy coherence under E0 or real1 errors',
            'physical Hold/scratch write forwarding over the full period',
            'continuing encoded-period closure',
            'literal computed-SimBit Workspace refinement'],
        measured_only=False,full_physical_E0_lift_proved=False,
        physical_self_simulation_proved=False,gray_verbatim_simulation=False,
        global_reliability_established=False,elapsed_seconds=time.monotonic()-start)
    (out/'GR1_fetch_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('exact_symbolic_front_cases',
        'exact_output_and_lookup_equalities','work_keys_with_unique_hit','zero_row_keys_without_hit',
        'correct_work_key_fetch_proved_conditionally','outside_work_key_instruction_irrelevance_proved',
        'elapsed_seconds')}),flush=True)


if __name__=='__main__': main()
