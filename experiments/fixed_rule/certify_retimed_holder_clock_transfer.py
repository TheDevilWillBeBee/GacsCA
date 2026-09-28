"""Canonical clock-signature transfer between two globally fixed candidates.

Every non-Age raw output is compared at matching clock signatures, with arbitrary
other raw fields. New Age is checked explicitly modulo U. This transfers local
rule lemmas only; new-ROM instruction paths and complete execution remain separate.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time

from gacsca.fixed_rule import retimed_holder_rule as new,retimed_holder_core as nc,retimed_holder_program as p
from gacsca.fixed_rule import small_holder_rule as old,small_holder_core as oc
from experiments.fixed_rule.certify_small_holder_clock_mail_factorization import ClockTerms
from experiments.fixed_rule.audit_small_holder_position_events import sha


def signature(c,age):
    next_age=(age+1)%c.U
    return (c.active(age),c.RESET_AGES[2]<=age<c.ACTIVE_ENDS[2],
            tuple(age==x for x in c.RESET_AGES),tuple(age==x for x in c.VOTE_AGES),
            next_age==c.CAPTURE_AGE,c.WF_START<=next_age<c.WF_END,age==c.U-1)


def intervals(c):
    points={0,c.U}
    for value in (*c.RESET_AGES,*c.VOTE_AGES,c.CAPTURE_AGE-1,c.U-1):points.update((value,value+1))
    points.update((*c.ACTIVE_ENDS,c.WF_START-1,c.WF_END-1))
    points=sorted(x for x in points if 0<=x<=c.U)
    return tuple((lo,hi-1) for lo,hi in zip(points,points[1:]) if lo<hi)


def prove_interval(interval,reference_age,description=None):
    t=ClockTerms(p.base_rom());A=t.variable('base_address',15)
    age=t.bounded('new_age',32,*interval);old_age=t.const(reference_age)
    common={site:tuple(t.modular_add(A,site,15) if name=='address' else age if name=='age'
                       else t.variable(f'raw_{site}_{name}',width) for name,width in new.SCHEMA)
            for site in new.NEIGHBORHOOD}
    incoming=tuple(word for site in new.NEIGHBORHOOD for word in common[site])
    previous=tuple(old_age if name=='age' else word for site in old.NEIGHBORHOOD
                   for (name,_),word in zip(old.SCHEMA,common[site]))
    after=t.expression(new.self_description() if description is None else description,incoming)
    before=t.expression(old.self_description(),previous)
    assert after[new.COL['age']]==t.modular_add(age,1,(new.U-1).bit_length()),('wrong new clock wrap',interval)
    assert after[new.COL['address']]==A
    for (name,_),a,b in zip(new.SCHEMA,after,before):
        if name!='age':assert a==b,('non-Age clock transfer',interval,reference_age,name)
    return dict(new_age_interval=interval,reference_age=reference_age,non_Age_words=153,
                exact_new_clock=True,arbitrary_other_raw_fields=True,symbolic_terms=len(t.nodes))


def certify(description=None):
    assert new.SCHEMA==old.SCHEMA and new.NEIGHBORHOOD==old.NEIGHBORHOOD
    representatives={}
    for lo,hi in intervals(oc):
        assert signature(oc,lo)==signature(oc,hi)
        representatives.setdefault(signature(oc,lo),lo)
    rows=[]
    for lo,hi in intervals(nc):
        key=signature(nc,lo);assert key==signature(nc,hi) and key in representatives
        rows.append(prove_interval((lo,hi),representatives[key],description))
    assert sum(hi-lo+1 for lo,hi in intervals(nc))==new.U
    return dict(passed=True,intervals=rows,legal_new_ages=new.U,
                compared_non_Age_output_words=153*len(rows),all_Ages_covered_without_sampling=True,
                unchanged_alphabet_bits=new.WIDTH,unchanged_neighborhood=new.NEIGHBORHOOD,
                domain='Canonical Address and uniform legal new Age; arbitrary remaining raw fields. Equivalent old phase may use different numeric Age.',
                limitation='Local clock-signature transfer plus modulo-U wrap, not new-ROM path recertification or a completed physical period.')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();result=certify()
    result.update(physical_descriptor_sha256=new.self_description().digest(),reference_descriptor_sha256=old.self_description().digest(),
                  source_sha256={str(path):sha(path) for path in (Path(__file__),Path('experiments/fixed_rule/certify_small_holder_clock_mail_factorization.py'),
                    *sorted(Path('gacsca/fixed_rule').glob('retimed_holder*.py')))},
                  seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
