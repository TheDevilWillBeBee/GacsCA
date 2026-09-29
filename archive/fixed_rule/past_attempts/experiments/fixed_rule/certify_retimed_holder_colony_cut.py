"""Conditional one-step colony separation in the complete physical descriptor.

Raw copies are assigned to the logical site they represent. They are not
silently discarded at a physical colony edge. The certificate is a one-step
dependency statement, not a claim that its hypotheses hold for all noisy time.
"""
import argparse
from functools import lru_cache
import json
from pathlib import Path
import resource
import time

from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_core as c
from gacsca.fixed_rule import retimed_holder_program as p
from gacsca.fixed_rule.retimed_holder_literal_cone import rom
from experiments.fixed_rule.retimed_holder_symbolic_bits import BitDependencies
from experiments.fixed_rule.certify_small_holder_clock_mail_factorization import ClockTerms
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha


def certify(description=None,*,allow_mail=False,restrict_controllers=True):
    desc=f.self_description() if description is None else description
    assert desc.inputs==15*f.FIELDS and len(desc.outputs)==f.FIELDS
    terms=ClockTerms(p.base_rom());zero=terms.const(0);one=terms.const(1)
    age=terms.variable('common_legal_age',31)
    owners={}
    bit_terms=BitDependencies(terms,owners)
    @lru_cache(None)
    def primary(site,name,width):
        if name.startswith(('lp_','rp_')) and not allow_mail:return zero
        if name not in ('data',) and not name.startswith(('lp_','rp_')) and restrict_controllers and site%f.Q>=len(p.base_rom()):return zero
        variable=terms.variable(f'primary_{site}_{name}',width)
        owners[variable]=site//f.Q
        return variable
    @lru_cache(None)
    def raw(site):
        values=[]
        for name,width in f.SCHEMA:
            if name.startswith('p'):
                prefix,field=name.split('_',1)
                value=terms.const(int(rom()[(site+int(prefix[1:])-3)%f.Q,c.STATIC.index(field)]))
            elif name=='address':value=terms.const(site%f.Q)
            elif name=='age':value=age
            elif name.startswith('s') and name!='signal':
                prefix,field=name.split('_',1)
                value=primary(site+int(prefix[1:])-2,field,width)
            else:value=zero # Flags, Wf and Signals are explicit domain assumptions.
            values.append(value)
        return tuple(values)
    @lru_cache(None)
    def dependencies(word):
        if word in owners:return frozenset((owners[word],))
        node=terms.nodes[word]
        if node[0] in ('variable','const'):return frozenset()
        if node[0]=='op':return dependencies(node[2])|dependencies(node[3])
        if node[0] in ('not','modadd'):return dependencies(node[1])
        raise AssertionError(('unreviewed symbolic node',node))
    sites=tuple(range(-11,11));checked=0;controller=0;signal_bits=0
    for site in sites:
        out=terms.expression(desc,tuple(value for d in f.NEIGHBORHOOD for value in raw(site+d)))
        assert out[f.COL['address']]==terms.const(site%f.Q)
        assert out[f.COL['age']]==terms.modular_add(age,1,31)
        for i,(name,_) in enumerate(f.SCHEMA):
            if name=='signal':
                for d in f.OFFSETS:
                    _,bit_dependencies=bit_terms.bit(out[i],d+2)
                    expected_owner=(site+d)//f.Q
                    assert bit_dependencies<={expected_owner},('Signal crosses colony ownership',site,d,bit_dependencies)
                    signal_bits+=1
            else:
                owner=site
                if name.startswith(('s','w')):
                    owner+=int(name.split('_',1)[0][1:])-2
                assert dependencies(out[i])<={owner//f.Q},('raw output crosses colony ownership',site,name,dependencies(out[i]),owner//f.Q)
                if name.startswith('s') and name.split('_',1)[1] in ('head',*c.CONTROL):controller+=1
            checked+=1
    return dict(passed=True,physical_output_sites=list(sites),complete_raw_output_words=checked,
                raw_controller_outputs_checked=controller,Signal_output_bits_checked=signal_bits,
                all_legal_ages=f.U,ROM_rows=len(p.base_rom()),symbolic_terms=len(terms.nodes),
                assumptions=['canonical physical Address','common legal Age','fixed ROM',
                             'coherent copies of all procedure words','zero input mail',
                             'zero input flags, Wf and Signals','all controller words zero outside the ROM region'],
                ownership='Procedure and Wf slot k at site x belongs to logical site x+k-2; Signal bit k uses the same owner. Other raw fields belong to x.',
                conclusion='Each checked raw output depends only on mutable procedure inputs belonging to its logical owner colony. Geometry is preserved. Remaining sites are separated by the fixed radius and replica offsets.',
                limitation='Conditional one-step cut only. Mail may be generated inside a colony; forcing/capture may leave the input domain. No all-time invariant, arbitrary noisy cut, or full-Q physical embedding is asserted.')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    out=Path(parser.parse_args().output)
    if out.exists():raise FileExistsError(out)
    started=time.perf_counter();result=certify()
    sources=(Path(__file__),Path(f.__file__),Path(c.__file__),Path(p.__file__),
             Path('gacsca/fixed_rule/retimed_holder_description.py'),
             Path('experiments/fixed_rule/certify_small_holder_clock_mail_factorization.py'),
             Path('experiments/fixed_rule/certify_small_holder_mail_factorization.py'),
             Path('experiments/fixed_rule/retimed_holder_symbolic_bits.py'))
    result.update(descriptor_sha256=f.self_description().digest(),source_sha256={str(path):sha(path) for path in sources},
                  seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
