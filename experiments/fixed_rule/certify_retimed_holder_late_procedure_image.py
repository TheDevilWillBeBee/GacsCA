"""Complete nonmail procedure coherence for arbitrary multihead late inputs."""
import argparse
from functools import lru_cache
import json
from pathlib import Path
import resource
import time

from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_core as c
from gacsca.fixed_rule import retimed_holder_program as p
from experiments.fixed_rule.certify_small_holder_clock_mail_factorization import ClockTerms
from experiments.fixed_rule.certify_retimed_holder_late_confinement import INTERVALS, MAIL
from experiments.fixed_rule.audit_retimed_holder_prefix_embedding import sha


def certify(interval, *, description=None):
    t = ClockTerms(p.base_rom())
    zero = t.const(0)
    address = t.variable('canonical_address', 15)
    age = t.bounded('late_age', 31, *interval)
    desc = f.self_description() if description is None else description

    @lru_cache(None)
    def primary(site, name, width):
        return zero if name in MAIL else t.variable(f'logical_{site}_{name}', width)

    @lru_cache(None)
    def raw(site):
        values = []
        for name, width in f.SCHEMA:
            if name.startswith('p'):
                prefix, field = name.split('_', 1)
                value = primary(site+int(prefix[1:])-3, field, width)
            elif name == 'address':
                value = t.modular_add(address, site, 15)
            elif name == 'age':
                value = age
            elif name.startswith('s') and name != 'signal':
                prefix, field = name.split('_', 1)
                value = primary(site+int(prefix[1:])-2, field, width)
            elif name in ('signal', 'f1'):
                value = t.variable(f'physical_{site}_{name}', width)
            else:
                value = zero
            values.append(value)
        return tuple(values)

    @lru_cache(None)
    def output(site):
        return t.expression(desc, tuple(value for d in f.NEIGHBORHOOD for value in raw(site+d)))

    expected = output(0)
    names = tuple(name for name, _ in f.PROCEDURE if name not in MAIL)
    count = 0
    for replica in f.OFFSETS:
        holder = -replica
        out = output(holder)
        assert out[f.COL['address']] == raw(holder)[f.COL['address']]
        assert out[f.COL['age']] == t.modular_add(age, 1, 31)
        assert out[f.COL['f2']] == zero
        assert all(out[f.COL[f'w{k}_{name}']] == zero for k in range(5) for name in ('wf1', 'wf2'))
        for name in names:
            assert out[f.COL[f's{replica+2}_{name}']] == expected[f.COL['s2_'+name]], ('incoherent output', interval, replica, name)
            count += 1

    @lru_cache(None)
    def variables(word):
        node = t.nodes[word]
        if node[0] == 'variable':
            return frozenset((node[1],))
        if node[0] == 'const':
            return frozenset()
        if node[0] == 'op':
            return variables(node[2]) | variables(node[3])
        if node[0] in ('not', 'modadd'):
            return variables(node[1])
        raise AssertionError(node)
    signal_sources = variables(expected[f.COL['signal']])
    assert all(name.startswith('physical_') and name.endswith('_signal') for name in signal_sources), signal_sources
    return dict(passed=True, old_age_interval=list(interval), coherent_nonmail_output_words=count,
                arbitrary_all_logical_controller_words=True, arbitrary_coherent_metadata=True,
                arbitrary_physical_Flag1_and_Signals=True, shared_Signal_inputs_remain_shared=True,
                zero_input_mail_required=True, zero_output_mail_required_for_full_procedure_image=True,
                all_addresses=f.Q, symbolic_terms=len(t.nodes))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    out = Path(parser.parse_args().output)
    if out.exists():
        raise FileExistsError(out)
    start = time.perf_counter()
    result = dict(passed=True, cases=[certify(interval) for interval in INTERVALS],
                  descriptor_sha256=f.self_description().digest(),
                  source_sha256={str(path): sha(path) for path in (
                      Path(__file__), Path(f.__file__), Path(c.__file__), Path(p.__file__),
                      Path('experiments/fixed_rule/certify_retimed_holder_late_confinement.py'),
                      Path('experiments/fixed_rule/certify_small_holder_clock_mail_factorization.py'))},
                  seconds=time.perf_counter()-start,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  scope='Late descriptor nonmail image with arbitrary simultaneous controller '
                        'states, canonical geometry, coherent metadata/procedures, and zero '
                        'Flag2/Wf/input mail. Complete procedure coherence additionally '
                        'requires all output mail zero; no one-head premise is used.')
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
