#!/usr/bin/env python3
"""Conditional first-suffix H1 rank13/H2 mailbox-tail identities.

No physical first-boundary or recovered-right lift is claimed by this
probe; the companion written bridge must justify its readonly premises.
"""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from check_g17_schedule import Terms
import proposed_sparse_short_force1024 as proposed
from check_short_force1024_protected_scratch import execute,dependencies


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    begin=time.monotonic();out=ROOT/'figs/robustness';p=proposed.parameters();candidate=proposed.load_artifact()
    listing_path=out/'SP29_program_listing.json';listing=json.loads(listing_path.read_text());start=p.E0+280*p.PL
    table=proposed.dependency_table(p);where={(r['field'],r['bit']):r['address'] for r in table}
    rank13=(13,77,141,205,269);tail_bits=[64*copy+rank for copy in range(5) for rank in range(54,64)]
    cases=[]
    for mode in ('first_four_H2_copies_mail_and_H1_rank13_zero','first_H2_tail_copies_and_mail_zero'):
        def readonly(terms,key):
            _,d,field,bit=key
            if mode=='first_four_H2_copies_mail_and_H1_rank13_zero':
                zero=field in ('mr','ml') or field=='h2' and bit in (13,77,205,269) or field=='h1' and bit in rank13
            else:zero=field in ('mr','ml') or field=='h2' and bit in tail_bits
            return 0 if zero else terms.var(key)
        terms=Terms();result=execute(p,candidate,listing,terms,readonly,start,p.U)
        field='h1' if mode.startswith('first_four') else 'h2';bits=rank13 if field=='h1' else tail_bits
        outputs=[]
        for bit in bits:
            target=result['hold'][where[field,bit]];dep=dependencies(terms,target)
            outputs.append(dict(field=field,bit=bit,phase=where[field,bit],constant=target if target in (0,1) else None,
                                dependency_variables=dep))
        cases.append(dict(mode=mode,late_instructions=result['instructions'],terms=len(terms.terms),outputs=outputs,
            all_earlier_work_other_readonly_inputs_and_I_free=True,physical_premises_proved=False))
    receipt=dict(proposal='SP29',scope='Abstract first-suffix selected H1/H2 zeros for recovered-right source study; no physical lift or full third pulse',
        Q=p.Q,U=p.U,T_wf=p.T_wf,start_age=start,cases=cases,
        raw_H1_rank13_copy_bits=list(rank13),raw_H2_tail_copy_bits=tail_bits,
        physical_first_boundary_sources_or_recovered_right_retained_data_proved=False,
        complete_third_signal_or_pulse_proved=False,general_eroder_higher_map_or_positive_iid_rate_proved=False,
        global_reliability_established=False,active_G17_modified=False,rule_programme_or_constant_change=False,
        checker_sha256=digest(__file__),proposal_source_sha256=digest(proposed.__file__),
        execution_helper_sha256=digest(ROOT/'Report/proofs/check_short_force1024_protected_scratch.py'),
        algebra_source_sha256=digest(ROOT/'Report/proofs/check_g17_schedule.py'),listing_sha256=digest(listing_path),
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        receipt_dependencies_sha256={name:digest(out/name) for name in ('SP29_crossing_history_probe.json',
            'SP29_second_right_boundary_certificate.json','SP29_emerging_foreign_source_certificate.json')},seconds=time.monotonic()-begin)
    (out/'SP29_recovered_right_source_probe.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(cases=[dict(mode=r['mode'],terms=r['terms'],constant_zero_outputs=sum(v['constant']==0 for v in r['outputs']),
        output_count=len(r['outputs']),nonconstant_bits=[v['bit'] for v in r['outputs'] if v['constant'] is None]) for r in cases],
        seconds=receipt['seconds'],global_reliability_established=False)),flush=True)


if __name__=='__main__':main()
