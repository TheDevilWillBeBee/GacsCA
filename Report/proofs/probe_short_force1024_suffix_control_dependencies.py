#!/usr/bin/env python3
"""Trace why the accepted late-zero lemma needs its mailbox premise.

These are universal/finite statements about an abstract suffix fibre.
No listed seed has assumed physical reachability after a native pulse.
Frozen suffix/proposal sources are reused without modification.
"""
from pathlib import Path
from types import FunctionType
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
import proposed_sparse_short_force1024 as proposed
import probe_short_force1024_late_suffix as prior
from check_g17_schedule import Terms


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(p,candidate,listing,spec):
    instances=[]
    class CofactorTerms(Terms):
        def __init__(self):super().__init__();instances.append(self)
        def var(self,name):
            if name[0]=='x':
                _,off,field,bit=name
                if field=='h2':return 0
                if spec.get('mail_ones') and field in ('mr','ml'):return 1
                if spec.get('native_Age_one') and field=='age':return (p.age_code(1)>>bit)&1
            if spec.get('scratch_zero') and name[0]=='seed_scr':return 0
            if spec.get('reg_zero') and name[0]=='seed_reg':return 0
            return super().var(name)
    namespace=dict(prior.__dict__,Terms=CofactorTerms)
    execute=FunctionType(prior.run.__code__,namespace,prior.run.__name__,prior.run.__defaults__)
    result=execute(p,candidate,listing,'h2_77_readonly_zero',p.E0+280*p.PL)
    terms=instances[0];target=result['selected_Hold_outputs']['h2:77']['term']
    pending=[target];live=set()
    while pending:
        term=pending.pop()
        if term in live:continue
        live.add(term);node=terms.terms[term]
        if node[0] in (0,1,2):pending.extend(node[1])
    names=[terms.terms[i][1] for i in sorted(live) if terms.terms[i][0]=='variable']
    result.update(premise=spec,all_h2_readonly_values_zero=True,
        target_dependency_variables=names,target_seed_dependencies=[n for n in names if n[0].startswith('seed_')],
        target_readonly_dependencies=[n for n in names if n[0]=='x'])
    witness=result['explicit_arbitrary_seed_h2_77_one_assignment']
    if witness is not None:
        live_names=set(names)
        witness['assignments']=[row for row in witness['assignments'] if tuple(row['name']) in live_names]
    return result


def main():
    begin=time.monotonic();out=ROOT/'figs/robustness';p=proposed.parameters()
    candidate=proposed.load_artifact();listing_path=out/'SP29_program_listing.json'
    listing=json.loads(listing_path.read_text())
    specs=[dict(name='H2zero_mail_free'),dict(name='H2zero_mail_one',mail_ones=True),
           dict(name='H2zero_mail_free_old_scratch_zero',scratch_zero=True),
           dict(name='H2zero_mail_free_native_Age_one',native_Age_one=True),
           dict(name='H2zero_mail_free_old_regs_and_scratch_zero',scratch_zero=True,reg_zero=True)]
    cases=[run(p,candidate,listing,spec) for spec in specs]
    receipt=dict(scope='Abstract page280 suffix dependency/cofactor probe only; physical prior-work/payload reachability and subsequent signal remain unproved',
        proposal='SP29',Q=p.Q,U=p.U,start_age=p.E0+280*p.PL,cases=cases,
        all_h2_readonly_zero_physical_premise_proved_by_this_probe=False,
        native_Age_one_alone_preserves_late_zero_proved=False,
        physical_seed_reachability_or_third_signal_proved=False,
        active_G17_modified=False,rule_programme_or_constant_change=False,global_reliability_established=False,
        checker_sha256=digest(__file__),proposal_source_sha256=digest(proposed.__file__),
        frozen_suffix_source_sha256=digest(prior.__file__),algebra_source_sha256=digest(ROOT/'Report/proofs/check_g17_schedule.py'),
        listing_sha256=digest(listing_path),proposed_candidate_sha256=candidate.digest(),seconds=time.monotonic()-begin)
    destination=out/'SP29_suffix_control_dependency_probe.json'
    destination.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(cases=[dict(premise=row['premise'],target=row['selected_Hold_outputs']['h2:77']['proved_constant'],
        dependencies=row['target_dependency_variables'],has_explicit_one_witness=row['explicit_arbitrary_seed_h2_77_one_assignment'] is not None)
        for row in cases],seconds=receipt['seconds'])),flush=True)


if __name__=='__main__':main()
