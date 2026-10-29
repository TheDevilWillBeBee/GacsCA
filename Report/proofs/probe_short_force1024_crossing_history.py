#!/usr/bin/env python3
"""Conditional suffix at the old true/foreign interface, before a new lift.

Native quiet-strip capture and shifted-prefix premises are explicit. This
probe alone proves neither their physical bridge nor a third whole pulse.
"""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from check_g17_schedule import Terms
import proposed_sparse_short_force1024 as proposed
from check_short_force1024_protected_scratch import execute,dependencies,blocked


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


class FreshPrefixTerms(Terms):
    def __init__(self):super().__init__();self.fresh_prefix=True
    def var(self,name):
        if self.fresh_prefix and name[0] in ('seed_reg','seed_scr'):return 0
        return super().var(name)


def main():
    begin=time.monotonic();out=ROOT/'figs/robustness';p=proposed.parameters();candidate=proposed.load_artifact()
    listing_path=out/'SP29_program_listing.json';listing=json.loads(listing_path.read_text());start=p.E0+280*p.PL
    selected=(13,77,141,205,269);native=('addr','age','f1','f2','wf1','wf2')
    def readonly(terms,key,mode):
        _,d,field,bit=key
        zero=field in ('mr','ml') or field=='h2' and bit in (13,77)
        if mode!='two_H2_copies_and_mail_zero' and field=='h2' and bit in (141,205,269) and d!=0:zero=True
        if mode in ('crossing_histories_and_native_zero','shifted_true120_prefix_cache_erased') and field in native:zero=True
        return 0 if zero else terms.var(('foreign',d,field,bit))
    cases=[]
    for mode in ('two_H2_copies_and_mail_zero','crossing_histories_zero','crossing_histories_and_native_zero'):
        terms=Terms();result=execute(p,candidate,listing,terms,lambda algebra,key:readonly(algebra,key,mode),start,p.U)
        target=result['hold'][509];dep=dependencies(terms,target)
        cases.append(dict(mode=mode,instructions=result['instructions'],terms=len(terms.terms),
            target_constant=target if target in (0,1) else None,dependency_variables=dep,
            all_other_work_and_readonly_inputs_free=True,physical_premises_proved=False))
    table=proposed.dependency_table(p);phase_at={(r['field'],r['bit']):r['address'] for r in table}
    live_offsets={(r['field'],r['bit']):r['offsets'] for r in table}
    strips=((121*p.Q,121*p.Q+512),(135*p.Q+512,136*p.Q))
    def normal120(terms,key):
        _,d,field,bit=key;col=120+d
        if d and d not in live_offsets[field,bit]:return terms.var(('normal',d,field,bit))
        if field in ('h1','h2'):
            assert col<=120 or blocked(strips,120,d,phase_at[field,bit],p.Q)
            return 0
        if field in ('addr','age','f1','wf1'):
            if blocked(strips,120,d,phase_at[field,bit],p.Q):return 0
            assert col<=120,(key,col)
            if field=='addr':return ((col%p.Q)>>bit)&1
            if field=='f1':return 0
            if col==120:return terms.var(('upper120_'+field,bit))
            return ((p.age_code(1)>>bit)&1) if field=='age' else 0
        return terms.var(('normal',d,field,bit))
    algebra=FreshPrefixTerms();prefix=execute(p,candidate,listing,algebra,normal120,p.E0,p.T_wf);algebra.fresh_prefix=False
    base=json.loads((out/'SP29_foreign_scratch_alias_probe.json').read_text())
    cache={};cache_records=[]
    for seed in base['scratch_alias_records']:
        cell,index=seed['cell'],seed['index'];old_phase=(cell+512)%p.Q
        value=prefix['scratch'].get((old_phase,index),0)
        cache[cell,index]=algebra.op(0,value,algebra.var(('shifted_scratch_survival',cell,index)))
        cache_records.append(dict(future_cell=cell,index=index,old_true_phase=old_phase,
            old_prefix_value_constant=value if value in (0,1) else None,
            written_during_prefix=(old_phase,index) in prefix['scratch']))
    mode='shifted_true120_prefix_cache_erased'
    suffix=execute(p,candidate,listing,algebra,lambda terms,key:readonly(terms,key,mode),start,p.U,cache)
    target=suffix['hold'][509];dep=dependencies(algebra,target)
    cases.append(dict(mode=mode,instructions=suffix['instructions'],terms=len(algebra.terms),
        target_constant=target if target in (0,1) else None,dependency_variables=dep,
        all_other_work_and_readonly_inputs_free=True,physical_premises_proved=False))
    receipt=dict(proposal='SP29',scope='Abstract emerging-foreign121 history/shifted-prefix suffix cofactors; no physical retained-bit120 theorem or full third pulse',
        Q=p.Q,U=p.U,T_wf=p.T_wf,start_age=start,cases=cases,
        first_two_rank13_H2_readonly_families_zero=[13,77],remaining_three_rank13_H2_nonzero_offset_histories_zero=[141,205,269],
        those_three_direct_Info_values_free=True,all_ten_mailbox_readonly_families_zero=True,
        optional_native_readonly_zero_fields=list(native),shifted_prefix_cache_records=cache_records,
        correct_initial_true120_pre_TF_prefix_assumed=True,initial_true_prefix_work_zero_assumed=True,
        physical_crossing_histories_or_shifted_cache_lift_proved=False,actual_retained_MF1021_120_zero_proved=False,
        complete_third_signal_or_pulse_proved=False,general_eroder_higher_map_or_positive_iid_rate_proved=False,
        global_reliability_established=False,active_G17_modified=False,rule_programme_or_constant_change=False,
        checker_sha256=digest(__file__),proposal_source_sha256=digest(proposed.__file__),
        execution_helper_sha256=digest(ROOT/'Report/proofs/check_short_force1024_protected_scratch.py'),
        algebra_source_sha256=digest(ROOT/'Report/proofs/check_g17_schedule.py'),listing_sha256=digest(listing_path),
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        receipt_dependencies_sha256={name:digest(out/name) for name in ('SP29_emerging_foreign_source_certificate.json',
            'SP29_foreign_cache_erasure_certificate.json','SP29_foreign_scratch_alias_probe.json')},seconds=time.monotonic()-begin)
    (out/'SP29_crossing_history_probe.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(cases=[dict(mode=row['mode'],constant=row['target_constant'],dependencies=len(row['dependency_variables']),terms=row['terms']) for row in cases],
        shifted_cache_constant_zero_slots=sum(row['old_prefix_value_constant']==0 for row in cache_records),
        shifted_cache_constant_one_slots=sum(row['old_prefix_value_constant']==1 for row in cache_records),
        shifted_cache_free_slots=sum(row['old_prefix_value_constant'] is None for row in cache_records),
        seconds=receipt['seconds'],global_reliability_established=False)),flush=True)


if __name__=='__main__':main()
