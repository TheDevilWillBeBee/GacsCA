"""Late-period non-mail separation and controller trapping identities.

These are conditional descriptor identities. Input AND output mail must vanish
along the trajectories to obtain complete-state separation. Shared raw Signals
need not vanish and may be incoherent. This file does not evolve physical states.
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


CONTROL = ('head', *c.CONTROL)
MAIL = tuple(name for name, _ in f.PROCEDURE if name.startswith(('lp_', 'rp_')))
INTERVALS = ((f.RESET_AGES[4]+1, f.ACTIVE_ENDS[4]-1),
             (f.ACTIVE_ENDS[4], f.U-2), (f.U-1, f.U-1))


def prepare(interval, *, fixed_rom=None, restrict_tail=True):
    table = rom() if fixed_rom is None else fixed_rom
    terms = ClockTerms(p.base_rom())
    zero = terms.const(0)
    age = terms.bounded('late_age', 31, *interval)
    owners = {}

    @lru_cache(None)
    def variable(name, width, owner=None):
        value = terms.variable(name, width)
        if owner is not None:
            owners[value] = owner
        return value

    @lru_cache(None)
    def primary(site, name, width):
        if name in MAIL:
            return zero
        if name in CONTROL and restrict_tail and site % f.Q >= len(p.base_rom()):
            return zero
        return variable(f'primary_{site}_{name}', width, site//f.Q)

    @lru_cache(None)
    def raw(site):
        values = []
        for name, width in f.SCHEMA:
            if name.startswith('p'):
                prefix, field = name.split('_', 1)
                value = terms.const(int(table[(site+int(prefix[1:])-3) % f.Q, c.STATIC.index(field)]))
            elif name == 'address':
                value = terms.const(site % f.Q)
            elif name == 'age':
                value = age
            elif name.startswith('s') and name != 'signal':
                prefix, field = name.split('_', 1)
                value = primary(site+int(prefix[1:])-2, field, width)
            elif name == 'f1':
                value = variable(f'physical_{site}_Flag1', 1, site//f.Q)
            elif name == 'signal':
                # Shared between the paired trajectories, not secretly zero.
                value = variable(f'shared_physical_{site}_Signal', width)
            else:
                value = zero  # Flag2 and Wf are explicit zero premises.
            values.append(value)
        return tuple(values)

    @lru_cache(None)
    def dependencies(word):
        if word in owners:
            return frozenset((owners[word],))
        node = terms.nodes[word]
        if node[0] in ('variable', 'const'):
            return frozenset()
        if node[0] == 'op':
            return dependencies(node[2]) | dependencies(node[3])
        if node[0] in ('not', 'modadd'):
            return dependencies(node[1])
        raise AssertionError(node)
    return terms, raw, dependencies, age


def cut(interval, *, description=None, restrict_tail=True):
    desc = f.self_description() if description is None else description
    t, raw, dependencies, age = prepare(interval, restrict_tail=restrict_tail)
    checked = skipped = 0
    for site in range(-11, 11):
        out = t.expression(desc, tuple(value for d in f.NEIGHBORHOOD for value in raw(site+d)))
        assert out[f.COL['address']] == t.const(site % f.Q)
        assert out[f.COL['age']] == t.modular_add(age, 1, 31)
        for index, (name, _) in enumerate(f.SCHEMA):
            if name.startswith('s') and name != 'signal' and name.split('_', 1)[1] in MAIL:
                skipped += 1
                continue
            if name == 'f2' or name.startswith('w'):
                assert out[index] == t.const(0), ('zero flag/forcing domain not preserved', site, name)
            if name == 'signal':
                assert not dependencies(out[index]), ('Signal is not shared', site)
            else:
                owner = site
                if name.startswith(('s', 'w')):
                    owner += int(name.split('_', 1)[0][1:])-2
                assert dependencies(out[index]) <= {owner//f.Q}, ('foreign mutable dependence', site, name, dependencies(out[index]))
            checked += 1
    assert checked+skipped == 22*f.FIELDS and skipped == 22*5*len(MAIL)
    return dict(old_age_interval=list(interval), nonmail_raw_outputs_checked=checked,
                conditional_zero_mail_outputs=skipped, arbitrary_Flag1=True,
                arbitrary_shared_raw_Signals=True, Flag2_Wf_zero_preserved=True,
                canonical_geometry_preserved=True)


def tail_edges(interval, *, fixed_rom=None):
    t, raw, _, _ = prepare(interval, fixed_rom=fixed_rom)
    sites = (len(p.base_rom()), f.Q-1)
    checked = 0
    for site in sites:
        out = t.expression(f.self_description(), tuple(value for d in f.NEIGHBORHOOD for value in raw(site+d)))
        for name in CONTROL:
            assert out[f.COL['s2_'+name]] == t.const(0), ('controller escaped into empty tail', site, name)
            checked += 1
    return dict(old_age_interval=list(interval), sites=list(sites), zero_controller_outputs=checked)


def no_head_birth():
    """Interior-tail case with arbitrary raw fields, absent heads/controllers/first markers."""
    t = ClockTerms(p.base_rom())
    inputs = []
    for site in f.NEIGHBORHOOD:
        for name, width in f.SCHEMA:
            controller = name.startswith('s') and name != 'signal' and name.split('_', 1)[1] in CONTROL
            first = name.startswith('p') and name.endswith('_first')
            inputs.append(t.const(0) if controller or first else t.variable(f'raw_{site}_{name}', width))
    out = t.expression(f.self_description(), tuple(inputs))
    checked = 0
    for slot in range(5):
        for name in CONTROL:
            assert out[f.COL[f's{slot}_{name}']] == t.const(0), ('spontaneous controller', slot, name)
            checked += 1
    return dict(zero_controller_outputs=checked, all_other_raw_fields_arbitrary=True,
                premise='Every input controller word and every first-marker bit zero.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    out = Path(parser.parse_args().output)
    if out.exists():
        raise FileExistsError(out)
    start = time.perf_counter()
    result = dict(passed=True, cut_cases=[cut(interval) for interval in INTERVALS],
                  tail_edge_cases=[tail_edges(interval) for interval in INTERVALS],
                  empty_interior=no_head_birth(),
                  complete_state_join_requires_zero_input_and_output_mail=True,
                  unrestricted_multihead_core_controllers=True,
                  descriptor_sha256=f.self_description().digest(),
                  source_sha256={str(path): sha(path) for path in (
                      Path(__file__), Path(f.__file__), Path(c.__file__), Path(p.__file__),
                      Path('gacsca/fixed_rule/retimed_holder_description.py'),
                      Path('experiments/fixed_rule/certify_small_holder_clock_mail_factorization.py'),
                      Path('experiments/fixed_rule/certify_small_holder_mail_factorization.py'))},
                  seconds=time.perf_counter()-start,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  scope='Late nonmail colony separation, Flag2/Wf zero preservation, '
                        'shared Signal evolution, and empty ordinary-tail controller '
                        'invariance. Tail premises are local at each cut. Complete '
                        'trajectory confinement still requires mail absence and entry '
                        'conditions to be verified; no arbitrary-noise theorem.')
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
