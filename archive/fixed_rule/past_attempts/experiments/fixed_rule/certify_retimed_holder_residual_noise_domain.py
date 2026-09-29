"""Residual Data separation with arbitrary clocks and incoherent Data copies.

Canonical physical Address and its hard-wired ROM remain premises. All other
raw words, including every 32-bit clock and each of the selected Data replicas,
are independent symbolic variables. This is a descriptor identity, not a noise
threshold or a replacement transition implementation.
"""
import argparse
from functools import lru_cache
import json
from pathlib import Path
import resource
import time
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_core as c
from gacsca.fixed_rule import retimed_holder_program as p
from gacsca.fixed_rule.retimed_holder_literal_cone import rom
from experiments.fixed_rule.certify_small_holder_clock_mail_factorization import ClockTerms
from experiments.fixed_rule.audit_retimed_holder_prefix_embedding import sha


def majority(t, values):
    a, b, c_, d, e = values
    triple = t.band(t.band(a, b), c_)
    pairs = t.bor(t.bor(t.band(a, b), t.band(a, c_)), t.band(b, c_))
    any3 = t.bor(t.bor(a, b), c_)
    return t.bor(t.bor(triple, t.band(pairs, t.bor(d, e))), t.band(any3, t.band(d, e)))


def certify(targets=(30960, 30961, 30962), description=None):
    targets = tuple(sorted(set(targets)))
    if not targets or len(targets) > 8 or any(type(a) is not int or not 16 <= a < f.Q-16 for a in targets) or targets[-1]-targets[0] > 32:
        raise ValueError('bounded interior Data support required')
    desc = f.self_description() if description is None else description
    assert desc.inputs == 15*f.FIELDS and len(desc.outputs) == f.FIELDS
    t = ClockTerms(p.base_rom())
    values = {(a, e): t.variable(f'residual_{a}_holder_{e}', 64) for a in targets for e in f.OFFSETS}
    expected = {a: majority(t, [values[a, e] for e in f.OFFSETS]) for a in targets}
    affected = set(values.values())

    @lru_cache(None)
    def depends(word):
        if word in affected:
            return True
        node = t.nodes[word]
        if node[0] in ('variable', 'const'):
            return False
        if node[0] == 'op':
            return depends(node[2]) or depends(node[3])
        if node[0] in ('not', 'modadd'):
            return depends(node[1])
        raise AssertionError(('unreviewed symbolic node', node))

    data_fields = {f's{k}_data': k-2 for k in range(5)}

    @lru_cache(None)
    def raw(site):
        row = []
        for name, width in f.SCHEMA:
            if name.startswith('p'):
                prefix, field = name.split('_', 1)
                offset = int(prefix[1:])-3
                value = t.const(int(rom()[(site+offset) % f.Q, c.STATIC.index(field)]))
            elif name == 'address':
                value = t.const(site % f.Q)
            elif name in data_fields and site+data_fields[name] in targets:
                value = values[site+data_fields[name], -data_fields[name]]
            else:
                value = t.variable(f'raw_{site}_{name}', width)
            row.append(value)
        return tuple(row)

    outputs = sorted({a+d for a in targets for d in range(-9, 10)})
    corrected = independent = 0
    for site in outputs:
        out = t.expression(desc, tuple(value for d in f.NEIGHBORHOOD for value in raw(site+d)))
        assert out[f.COL['address']] == t.const(site % f.Q), 'canonical Address not preserved'
        for index, (name, _) in enumerate(f.SCHEMA):
            target = site+data_fields[name] if name in data_fields else None
            if target in targets:
                assert out[index] == expected[target], ('selected Data not majority-corrected', site, name)
                corrected += 1
            else:
                assert not depends(out[index]), ('residual Data affects another output', site, name)
                independent += 1
    assert corrected == 5*len(targets)
    return dict(passed=True, selected_addresses=list(targets), causal_output_sites=outputs,
                complete_raw_outputs=len(outputs)*f.FIELDS,
                corrected_Data_copies=corrected, independent_raw_outputs=independent,
                independent_clock_bits_per_physical_site=32,
                arbitrary_other_raw_fields=True, initial_Data_coherence_required=False,
                canonical_Address_preserved=True, symbolic_terms=len(t.nodes),
                relation='All selected Data copies become their bitwise majority; every other '
                         'raw output is independent of all selected input Data copies. '
                         'Canonical Address is preserved with arbitrary independent clocks '
                         'and all other raw words. Fixed G ROM therefore remains canonical.',
                limitation='Canonical Address and hard-wired ROM remain essential premises. '
                           'This gives separation of residual Data, not correction of arbitrary '
                           'clock/controller faults or an ongoing full-state noise theorem.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    out = Path(parser.parse_args().output)
    if out.exists():
        raise FileExistsError(out)
    started = time.perf_counter()
    result = certify()
    sources = (Path(__file__), Path(f.__file__), Path(c.__file__), Path(p.__file__),
               Path('gacsca/fixed_rule/retimed_holder_description.py'),
               Path('experiments/fixed_rule/certify_small_holder_clock_mail_factorization.py'),
               Path('experiments/fixed_rule/certify_small_holder_mail_factorization.py'))
    result.update(descriptor_sha256=f.self_description().digest(),
                  source_sha256={str(path): sha(path) for path in sources},
                  seconds=time.perf_counter()-started,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    with out.open('x') as stream:
        stream.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
