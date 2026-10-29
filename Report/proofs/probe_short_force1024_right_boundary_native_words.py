#!/usr/bin/env python3
"""Conditional right second-step native words and first-suffix H2 copies.

No damaged-history data repair or full third signal is asserted here.
Native source premises are J172's first-boundary enclosure. Newly used
H2 zeros are only abstract source premises until given a physical lift.
"""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,Compiled
from check_g17_schedule import Terms
import proposed_sparse_short_force1024 as proposed
from check_short_force1024_protected_scratch import execute,blocked


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def word(net,field,width):
    nodes=[net.outputs['y',field,bit] for bit in range(width)]
    return dict(constant=sum(node<<bit for bit,node in enumerate(nodes)) if all(node in (0,1) for node in nodes) else None,
                constant_bits={str(bit):node for bit,node in enumerate(nodes) if node in (0,1)},
                nonconstant_bits=[bit for bit,node in enumerate(nodes) if node not in (0,1)])


def main():
    begin=time.monotonic();out=ROOT/'figs/robustness';p=proposed.parameters();candidate=proposed.load_artifact()
    listing_path=out/'SP29_program_listing.json';listing=json.loads(listing_path.read_text())
    copies=(13,77,141,205,269)
    def first_readonly(terms,key):
        _,d,field,bit=key
        return 0 if field in ('mr','ml') or field=='h2' and bit in (13,77,205,269) else terms.var(key)
    terms=Terms();suffix=execute(p,candidate,listing,terms,first_readonly,p.E0+280*p.PL,p.U)
    suffix_copies=[]
    for bit in copies:
        phase=suffix['where']['h2',bit];node=suffix['hold'][phase]
        suffix_copies.append(dict(bit=bit,phase=phase,constant=node if node in (0,1) else None))
    table=proposed.dependency_table(p);phase_at={(row['field'],row['bit']):row['address'] for row in table}
    strips=((121*p.Q,121*p.Q+512),(135*p.Q+512,136*p.Q));records=[]
    for j in range(136,184):
        class Captured(Net):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,field,bit=key;col=j+d
                    if field in ('addr','age','f1','wf1'):
                        if blocked(strips,j,d,phase_at[field,bit],p.Q):return 0
                        assert col>=136,(j,key,col)
                        if field=='addr':return 0 if col<=143 else ((col%p.Q)>>bit)&1
                        if field=='f1':return int(col in (144,145,146))
                        if field=='age':return super().input(('upper_Age',col,bit)) if col<=143 else ((p.age_code(1)>>bit)&1)
                        if field=='wf1':return super().input(('upper_WF1',col,bit)) if col<=143 else 0
                    if field=='h2' and bit in copies:return 0
                return super().input(key)
        net,_=proposed.full_net(p,Captured)
        values={field:word(net,field,dict(candidate.schema)[field]) for field in ('addr','age','f1','wf1')}
        values['h2_copies']={str(bit):net.outputs['y','h2',bit] if net.outputs['y','h2',bit] in (0,1) else None for bit in copies}
        records.append(dict(colony=j,outputs=values,netlist_sha256=Compiled(net).digest))
    receipt=dict(proposal='SP29',scope='Conditional abstract first suffix-copy and second right native-word cofactors; no physical second boundary or third-signal theorem',
        Q=p.Q,U=p.U,first_suffix_late_instructions=suffix['instructions'],first_suffix_terms=len(terms.terms),
        first_suffix_five_rank13_H2_copy_outputs=suffix_copies,
        second_right_source_native_enclosure_from_J172=True,
        added_all_five_rank13_H2_inputs_zero_assumed=True,other_fields_and_I_free=True,
        records=records,physical_second_boundary_data_or_third_signal_proved=False,
        global_reliability_established=False,active_G17_modified=False,rule_programme_or_constant_change=False,
        checker_sha256=digest(__file__),proposal_source_sha256=digest(proposed.__file__),
        algebra_source_sha256=digest(ROOT/'Report/proofs/check_g17_schedule.py'),
        execution_helper_sha256=digest(ROOT/'Report/proofs/check_short_force1024_protected_scratch.py'),
        listing_sha256=digest(listing_path),proposed_candidate_sha256=candidate.digest(),
        receipt_dependencies_sha256={name:digest(out/name) for name in ('SP29_second_signal_enclosure_certificate.json','SP29_first_boundary_signal_data_certificate.json')},
        seconds=time.monotonic()-begin)
    (out/'SP29_right_boundary_native_word_probe.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(first_suffix_copies=suffix_copies,
        native_words=[dict(colony=row['colony'],**{field:row['outputs'][field]['constant'] for field in ('addr','age','f1','wf1')},h2=row['outputs']['h2_copies']) for row in records],
        seconds=receipt['seconds'],global_reliability_established=False)),flush=True)


if __name__=='__main__':main()
