"""Complete early descriptor identities for joining geometry to procedure state."""
import argparse
import json
from pathlib import Path
import resource
import time
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_program as p
from gacsca.fixed_rule.wordcode import EQ
from experiments.fixed_rule.certify_small_holder_clock_mail_factorization import ClockTerms
from experiments.fixed_rule.audit_retimed_holder_prefix_embedding import sha


def certify_effects(description=None):
    desc=f.self_description() if description is None else description
    t=ClockTerms(p.base_rom());zero=t.const(0)
    age=t.bounded('early_age',32,128,16988);address=t.variable('own_address',15)
    inputs=[]
    for damaged in (False,True):
        raw=[]
        for site in f.NEIGHBORHOOD:
            for name,width in f.SCHEMA:
                if name=='age': value=age
                elif name=='address':
                    value=address if site==0 else t.variable(f'geometry_{site}_address',15) if damaged else t.modular_add(address,site,15)
                elif name in ('f1','f2'): value=t.variable(f'geometry_{site}_{name}',1) if damaged else zero
                elif name.startswith('w'): value=zero
                else:value=t.variable(f'shared_{site}_{name}',width)
                raw.append(value)
        inputs.append(tuple(raw))
    healthy,actual=(t.expression(desc,raw) for raw in inputs)
    clear=t.all(actual[f.COL['f1']],t.not_(t.op(EQ,actual[f.COL['address']],address)))
    for d in f.OFFSETS:
        for name,_ in f.PROCEDURE:
            key=f's{d+2}_{name}'
            predicate=actual[f.COL['f1']] if name.startswith(('lp_','rp_')) else clear
            assert actual[f.COL[key]]==t.select(predicate,zero,healthy[f.COL[key]]),('unaccounted geometry effect',key)
    assert actual[f.COL['signal']]==t.select(clear,zero,healthy[f.COL['signal']]), 'unaccounted Signal effect'
    for out in (healthy,actual):
        assert out[f.COL['age']]==t.modular_add(age,1,31)
        for k in range(5):
            for name in ('wf1','wf2'):assert out[f.COL[f'w{k}_{name}']]==zero
    return dict(passed=True,old_age_interval=[128,16988],complete_procedure_outputs=5*len(f.PROCEDURE),
                same_own_Address_and_raw_metadata_required=True,
                arbitrary_shared_raw_procedures_and_Signals=True,
                arbitrary_neighbor_Addresses_and_flags=True,
                nonmail_difference_only_via_Flag1_Address_change_clearing=True,
                mail_difference_only_via_Flag1_clearing=True,
                Signal_difference_only_via_Flag1_Address_change_clearing=True,
                output_Wf_zero=True,symbolic_terms=len(t.nodes))


def certify_zero(description=None):
    desc=f.self_description() if description is None else description
    t=ClockTerms(p.base_rom());zero=t.const(0);age=t.bounded('early_age',32,128,16988)
    raw=[]
    for site in f.NEIGHBORHOOD:
        for name,width in f.SCHEMA:
            if name=='age':value=age
            elif name.startswith(('s0_','s1_','s2_','s3_','s4_','w')) or name=='signal':value=zero
            else:value=t.variable(f'raw_{site}_{name}',width)
            raw.append(value)
    output=t.expression(desc,tuple(raw));checked=0
    for name,_ in f.SCHEMA:
        if name.startswith(('s0_','s1_','s2_','s3_','s4_','w')) or name=='signal':
            assert output[f.COL[name]]==zero,('zero procedure domain not preserved',name)
            checked+=1
    return dict(passed=True,old_age_interval=[128,16988],zero_procedure_Signal_Wf_outputs=checked,
                arbitrary_raw_Addresses_flags_and_metadata=True,entire_raw_neighborhood_procedures_zero_required=True,
                symbolic_terms=len(t.nodes))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    out=Path(parser.parse_args().output)
    if out.exists():raise FileExistsError(out)
    started=time.perf_counter()
    result=dict(passed=True,effects=certify_effects(),zero_domain=certify_zero(),
                descriptor_sha256=f.self_description().digest(),
                source_sha256={str(x):sha(x) for x in (Path(__file__),Path(f.__file__),Path('gacsca/fixed_rule/retimed_holder_description.py'),Path('experiments/fixed_rule/certify_small_holder_clock_mail_factorization.py'))},
                seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                scope='Local full-descriptor identities only. Joining them over time requires '
                      'a checked shared-procedure entry, healthy zero-mail behavior, and zero '
                      'procedure neighborhoods wherever own Address changes or is incorrect.')
    with out.open('x') as stream:stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
