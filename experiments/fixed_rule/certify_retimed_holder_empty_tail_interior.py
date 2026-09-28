"""No controller birth from three empty logical procedure records.

Only the target first marker is zero. Distant controllers and other first
markers remain arbitrary, including those inside the physical radius-seven
neighborhood. This supplies every interior site of an ordinary empty ROM tail.
"""
import argparse
from functools import lru_cache
import json
from pathlib import Path
import resource
import time
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_core as c
from gacsca.fixed_rule import retimed_holder_program as p
from experiments.fixed_rule.certify_small_holder_clock_mail_factorization import ClockTerms
from experiments.fixed_rule.audit_retimed_holder_prefix_embedding import sha

CONTROL = ('head', *c.CONTROL)


def certify(*, description=None, zero_first=True):
    t = ClockTerms(p.base_rom())
    zero = t.const(0)
    address = t.variable('canonical_address', 15)
    age = t.variable('common_legal_age', 31)
    desc = f.self_description() if description is None else description

    @lru_cache(None)
    def logical(site, name, width):
        if (name in CONTROL and -1 <= site <= 1) or (name == 'first' and site == 0 and zero_first):
            return zero
        return t.variable(f'logical_{site}_{name}', width)

    @lru_cache(None)
    def raw(site):
        row = []
        for name, width in f.SCHEMA:
            if name.startswith('p'):
                prefix, field = name.split('_', 1)
                value = logical(site+int(prefix[1:])-3, field, width)
            elif name.startswith('s') and name != 'signal':
                prefix, field = name.split('_', 1)
                value = logical(site+int(prefix[1:])-2, field, width)
            elif name == 'address':
                value = t.modular_add(address, site, 15)
            elif name == 'age':
                value = age
            else:
                value = t.variable(f'physical_{site}_{name}', width)
            row.append(value)
        return tuple(row)

    checked = 0
    for replica in f.OFFSETS:
        holder = -replica
        out = t.expression(desc, tuple(value for d in f.NEIGHBORHOOD for value in raw(holder+d)))
        for name in CONTROL:
            assert out[f.COL[f's{replica+2}_{name}']] == zero, ('controller birth', replica, name)
            checked += 1
    return dict(passed=True, complete_zero_controller_copies=checked, all_legal_ages=f.U,
                zero_logical_controller_sites=[-1, 0, 1], zero_first_marker_sites=[0],
                all_other_coherent_metadata_procedures_arbitrary=True,
                arbitrary_physical_flags_Wf_Signals=True,
                canonical_uniform_geometry_required=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    out = Path(parser.parse_args().output)
    if out.exists():
        raise FileExistsError(out)
    start = time.perf_counter()
    result = certify()
    result.update(descriptor_sha256=f.self_description().digest(),
                  source_sha256={str(path): sha(path) for path in (
                      Path(__file__), Path(f.__file__), Path(c.__file__), Path(p.__file__),
                      Path('experiments/fixed_rule/certify_small_holder_clock_mail_factorization.py'))},
                  seconds=time.perf_counter()-start,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  scope='Zero target controller image with only its three old logical '
                        'controller records zero and target first marker zero. No assumption '
                        'that all controllers or first markers in the raw stencil vanish.')
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
