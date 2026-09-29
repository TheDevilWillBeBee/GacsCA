"""Complete-descriptor geometry independence with uniform early clock and Wf0."""
import argparse
import json
from pathlib import Path
import time
import resource
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_program as p
from experiments.fixed_rule.certify_small_holder_clock_mail_factorization import ClockTerms
from experiments.fixed_rule.audit_retimed_holder_prefix_embedding import sha


def certify(description=None):
    desc = f.self_description() if description is None else description
    t = ClockTerms(p.base_rom())
    age = t.bounded('uniform_early_age', 32, 0, 32767)
    inputs = []
    for copy in (0, 1):
        raw = []
        for site in f.NEIGHBORHOOD:
            for name, width in f.SCHEMA:
                if name == 'age':
                    value = age
                elif name.startswith('w'):
                    value = t.const(0)
                elif name in ('address','f1','f2'):
                    value = t.variable(f'geometry_{site}_{name}', width)
                else:
                    value = t.variable(f'copy_{copy}_{site}_{name}', width)
                raw.append(value)
        inputs.append(tuple(raw))
    outputs = [t.expression(desc, raw) for raw in inputs]
    for name in ('address','age','f1','f2'):
        assert outputs[0][f.COL[name]] == outputs[1][f.COL[name]], ('geometry depends on other state',name)
    for out in outputs:
        assert out[f.COL['age']] == t.modular_add(age,1,31), 'uniform clock not preserved'
        for k in range(5):
            for flag in ('wf1','wf2'):
                assert out[f.COL[f'w{k}_{flag}']] == t.const(0), 'nonzero Wf output'
    return dict(passed=True, old_age_interval=[0,32767], geometry_outputs_independent=4,
                zero_Wf_outputs=10, arbitrary_independent_Addresses_and_flags=True,
                arbitrary_all_other_raw_fields=True, uniform_clock_preserved=True,
                uniform_clock_and_zero_input_Wf_required=True, symbolic_terms=len(t.nodes))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    out=Path(parser.parse_args().output)
    if out.exists(): raise FileExistsError(out)
    started=time.perf_counter();result=certify()
    result.update(descriptor_sha256=f.self_description().digest(),
                  source_sha256={str(x):sha(x) for x in (Path(__file__),Path(f.__file__),Path('gacsca/fixed_rule/retimed_holder_description.py'),Path('experiments/fixed_rule/certify_small_holder_clock_mail_factorization.py'))},
                  seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  scope='Independence of the complete physical geometry outputs from all '
                        'other raw fields under uniform early clock and zero input Wf; '
                        'zero Wf and uniform clock are preserved. Not a whole-state repair theorem.')
    with out.open('x') as stream: stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__': main()
