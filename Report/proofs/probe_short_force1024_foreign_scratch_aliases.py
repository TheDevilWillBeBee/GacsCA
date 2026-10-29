#!/usr/bin/env python3
"""Conditional cache-erasure/phase-alias probe for second old foreign frames.

No native scratch reachability, complete third mask, or iid result is
claimed. A constant Boolean output is a universal identity on its stated
abstract fibre; a nonconstant normal form is not a failure witness.
"""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,Compiled
from check_g17_schedule import Terms
import proposed_sparse_short_force1024 as proposed
from check_short_force1024_protected_scratch import execute,dependencies


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    begin=time.monotonic();out=ROOT/'figs/robustness';p=proposed.parameters();candidate=proposed.load_artifact()
    listing_path=out/'SP29_program_listing.json';listing=json.loads(listing_path.read_text());start=p.E0+280*p.PL
    copies=(13,77,141,205,269)
    def readonly(terms,key):
        return 0 if key[2]=='addr' or key[2]=='h2' and key[3] in copies else terms.var(key)
    class Fresh(Net):
        def input(self,key):
            if isinstance(key,tuple) and len(key)==4 and key[0]=='x' and (key[2]=='addr' or key[2]=='h2' and key[3] in copies):return 0
            return super().input(key)
    net,_=proposed.full_net(p,Fresh)
    fresh={str(bit):(net.outputs['y','h2',bit] if net.outputs['y','h2',bit] in (0,1) else None) for bit in copies}
    terms=Terms();suffix=execute(p,candidate,listing,terms,readonly,start,p.U)
    deps=dependencies(terms,suffix['hold'][509]);seeds=[(name[1],name[2]) for name in deps if name[0]=='seed_scr']
    records=[]
    for cell,index in seeds:
        aliases=[r for r in listing if r[4]==(cell+512)%p.Q and r[6]==2 and r[9]==index
                 and p.T_wf-2<=p.E0+r[1]*p.PL+r[2]<p.T_wf+6144]
        ordinary=[r for r in listing if r[4]==cell and r[6]==2 and r[9]==index
                  and p.T_wf-2<=p.E0+r[1]*p.PL+r[2]<start]
        records.append(dict(cell=cell,index=index,opposite_phase=(cell+512)%p.Q,
            opposite_pulse_scratch_issues=[dict(sequence=r[0],input_issue_age=p.E0+r[1]*p.PL+r[2],
                op=r[5],source_a=r[7],source_b=r[8]) for r in aliases],
            ordinary_post_TF_scratch_issues=[dict(sequence=r[0],input_issue_age=p.E0+r[1]*p.PL+r[2]) for r in ordinary]))
    results=[]
    for mode in ('exact_prefix_cache','erased_prefix_cache','aliases_free_other_cache_erased','all_zero_cache'):
        algebra=Terms();prefix=execute(p,candidate,listing,algebra,readonly,p.E0,p.T_wf)
        cache={}
        for record in records:
            key=record['cell'],record['index'];value=prefix['scratch'][key]
            if mode=='all_zero_cache':value=0
            elif mode=='aliases_free_other_cache_erased' and record['opposite_pulse_scratch_issues']:
                value=algebra.var(('aliased_scratch',*key))
            elif mode in ('erased_prefix_cache','aliases_free_other_cache_erased'):
                value=algebra.op(0,value,algebra.var(('scratch_survival',*key)))
            cache[key]=value
        last=execute(p,candidate,listing,algebra,readonly,start,p.U,cache)
        target=last['hold'][509];live=dependencies(algebra,target)
        results.append(dict(mode=mode,output_constant=target if target in (0,1) else None,
            terms=len(algebra.terms),dependency_variables=live,physical_reachability_proved=False))
    receipt=dict(proposal='SP29',scope='Abstract GF0/rank13H2zero prefix-cache erasures and opposite-phase scratch alias scan; no physical erasure/alias/history theorem',
        Q=p.Q,U=p.U,T_wf=p.T_wf,start_age=start,fresh_GF0_rank13_H2zero_output_copies=fresh,
        fresh_netlist_sha256=Compiled(net).digest,arbitrary_suffix_target_constant=suffix['hold'][509] if suffix['hold'][509] in (0,1) else None,
        arbitrary_suffix_dependency_variables=deps,seed_count=len(seeds),scratch_alias_records=records,
        seed_slots_with_opposite_pulse_issues=sum(bool(r['opposite_pulse_scratch_issues']) for r in records),
        opposite_pulse_issue_count=sum(len(r['opposite_pulse_scratch_issues']) for r in records),
        seed_slots_with_ordinary_post_TF_issues=sum(bool(r['ordinary_post_TF_scratch_issues']) for r in records),cases=results,
        physically_surviving_scratch_or_retained_data_proved=False,complete_third_signal_or_pulse_proved=False,
        general_eroder_higher_map_or_positive_iid_rate_proved=False,global_reliability_established=False,
        active_G17_modified=False,rule_programme_or_constant_change=False,checker_sha256=digest(__file__),
        proposal_source_sha256=digest(proposed.__file__),execution_helper_sha256=digest(ROOT/'Report/proofs/check_short_force1024_protected_scratch.py'),
        algebra_source_sha256=digest(ROOT/'Report/proofs/check_g17_schedule.py'),listing_sha256=digest(listing_path),
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        receipt_dependencies_sha256={name:digest(out/name) for name in ('SP29_protected_scratch_certificate.json','SP29_second_right_boundary_certificate.json')},
        seconds=time.monotonic()-begin)
    (out/'SP29_foreign_scratch_alias_probe.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(fresh_copies=fresh,seed_count=len(seeds),alias_slots=receipt['seed_slots_with_opposite_pulse_issues'],
        alias_issues=receipt['opposite_pulse_issue_count'],ordinary_issues=receipt['seed_slots_with_ordinary_post_TF_issues'],
        cases=[dict(mode=row['mode'],constant=row['output_constant'],dependencies=len(row['dependency_variables'])) for row in results],
        seconds=receipt['seconds'],global_reliability_established=False)),flush=True)


if __name__=='__main__':main()
