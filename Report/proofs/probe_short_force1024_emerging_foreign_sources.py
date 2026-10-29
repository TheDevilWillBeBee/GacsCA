#!/usr/bin/env python3
"""Abstract source identities for the newly emerging second-period frames.

The receipt contains Boolean identities, not a physical source bridge or
complete third-signal theorem. Every earlier workspace seed remains free.
"""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,Compiled
from check_g17_schedule import Terms
import proposed_sparse_short_force1024 as proposed
from check_short_force1024_protected_scratch import execute


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    begin=time.monotonic();out=ROOT/'figs/robustness';p=proposed.parameters();candidate=proposed.load_artifact()
    listing_path=out/'SP29_program_listing.json';listing=json.loads(listing_path.read_text())
    fields=[(field,bit) for field,width in candidate.schema for bit in range(width)]
    at_phase={int(candidate.layout[i]):key for i,key in enumerate(fields)}
    where={key:int(candidate.layout[i]) for i,key in enumerate(fields)}
    copies=(13,77,141,205,269);cases=[]
    for mode in ('true_history_and_mail_zero','foreign_initial_shifted_private_zero','foreign_info_hold_mail_zero'):
        def readonly(terms,key):
            _,d,field,bit=key
            if mode=='true_history_and_mail_zero':zero=field in ('h1','h2','mr','ml')
            elif mode=='foreign_info_hold_mail_zero':zero=field in ('info','hold','mr','ml')
            else:
                physical=at_phase.get((where[field,bit]+512)%p.Q)
                zero=physical is None or physical[0] not in ('addr','info')
            return 0 if zero else terms.var(key)
        terms=Terms();suffix=execute(p,candidate,listing,terms,readonly,p.E0+280*p.PL,p.U)
        outputs={}
        for field,bits in [('h1',range(dict(candidate.schema)['h1'])),
                           ('h2',range(dict(candidate.schema)['h2'])),
                           ('mr',range(5)),('ml',range(5))]:
            values={str(bit):(suffix['hold'][where[field,bit]] if suffix['hold'][where[field,bit]] in (0,1) else None) for bit in bits}
            outputs[field]=dict(constant_bits={bit:value for bit,value in values.items() if value is not None},
                                nonconstant_bits=[int(bit) for bit,value in values.items() if value is None])
        cases.append(dict(mode=mode,late_instructions=suffix['instructions'],terms=len(terms.terms),outputs=outputs))
    class ZeroGF(Net):
        def input(self,key):
            if isinstance(key,tuple) and len(key)==4 and key[0]=='x' and key[2]=='addr':return 0
            return super().input(key)
    net,_=proposed.full_net(p,ZeroGF)
    ghost={}
    for field in ('h1','h2','mr','ml'):
        values={str(bit):(node if node in (0,1) else None) for bit in range(dict(candidate.schema)[field])
                for node in [net.outputs['y',field,bit]]}
        ghost[field]=dict(constant_bits={bit:value for bit,value in values.items() if value is not None},
                          nonconstant_bits=[int(bit) for bit,value in values.items() if value is None])
    receipt=dict(proposal='SP29',scope='Abstract first-boundary source and GF0 fresh-programme cofactors only; physical source bridge unproved by this probe',
        Q=p.Q,U=p.U,start_age=p.E0+280*p.PL,cases=cases,fresh_GF_zero_all_other_inputs_free_outputs=ghost,
        fresh_GF_zero_cofactor_netlist_sha256=Compiled(net).digest,
        physical_emerging_foreign_readonly_sources_zero_proved=False,complete_third_signal_or_pulse_proved=False,
        general_eroder_higher_map_or_positive_iid_rate_proved=False,global_reliability_established=False,
        active_G17_modified=False,rule_programme_or_constant_change=False,
        checker_sha256=digest(__file__),proposal_source_sha256=digest(proposed.__file__),
        execution_helper_sha256=digest(ROOT/'Report/proofs/check_short_force1024_protected_scratch.py'),
        algebra_source_sha256=digest(ROOT/'Report/proofs/check_g17_schedule.py'),listing_sha256=digest(listing_path),
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        receipt_dependencies_sha256={name:digest(out/name) for name in ('SP29_second_right_boundary_certificate.json','SP29_protected_scratch_certificate.json')},
        seconds=time.monotonic()-begin)
    (out/'SP29_emerging_foreign_source_probe.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(cases=[dict(mode=row['mode'],terms=row['terms'],
        constants={field:len(value['constant_bits']) for field,value in row['outputs'].items()},
        rank13={field:{str(bit):row['outputs'][field]['constant_bits'].get(str(bit)) for bit in copies} for field in ('h1','h2')}) for row in cases],
        fresh_GF0_constants={field:len(value['constant_bits']) for field,value in ghost.items()},
        seconds=receipt['seconds'],global_reliability_established=False)),flush=True)


if __name__=='__main__':main()
