"""Relate the GPU coherent procedure DAG to complete raw F at every legal Age.

The GPU representation has canonical geometry and coherent procedure/static
copies. Physical flags/Wf are factored separately, not erased from a trajectory.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import sys
import time
from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_core as c
from gacsca.fixed_rule import compact16_holder_prefix_description as kernel
from experiments.fixed_rule import certify_compact16_holder_clock_mail_factorization as clock
from experiments.fixed_rule.certify_small_holder_head_invariant import BooleanAbstraction


def certify_case(phase, description=None):
    terms, original, _ = clock.prepare(phase)
    zero = terms.const(0)
    def raw(site):
        words = list(original(site))
        for name in ('f1', 'f2', *(f'w{k}_{n}' for k in range(5) for n in ('wf1', 'wf2'))):
            words[f.COL[name]] = zero
        return tuple(words)
    def field(site, name):
        prefix = 'p3_' if name in c.STATIC else 's2_' if name in dict(f.PROCEDURE) else 'w2_' if name.startswith('wf') else ''
        return raw(site)[f.COL[prefix+name]]
    full = terms.expression(f.self_description(), tuple(word for j in f.NEIGHBORHOOD for word in raw(j)))
    desc = kernel.build() if description is None else description
    result = terms.expression(desc, tuple(field(j, name) for j in range(-5, 6) for name, _ in c.SCHEMA))
    assert len(result) == c.FIELDS
    checked = []; bdd_nodes = 0; exact_fields = 0
    proof = None
    try:
        for (name, width), value in zip(c.SCHEMA, result):
            if name in ('f1', 'f2', 'wf1', 'wf2'):
                assert value == zero, ('kernel context placeholder', name)
                continue
            prefix = 'p3_' if name in c.STATIC else 's2_' if name in dict(f.PROCEDURE) else ''
            wanted = full[f.COL[prefix+name]]
            if value == wanted:
                exact_fields += 1
            else:
                proof = BooleanAbstraction(terms)
                for bit in range(64):
                    assert proof.bit(value, bit) == proof.bit(wanted, bit), ('coherent GPU reduction', phase, name, bit)
                bdd_nodes += len(proof.b.nodes)
                proof.close(); proof = None
            checked.append(name)
        return dict(passed=True, phase=phase, all_clock_ages=f.U, all_addresses=f.Q,
                    fields_checked=checked, complete_procedure_fields=len(f.PROCEDURE),
                    arbitrary_static_Data_controllers_mail_Signals=True,
                    BDD_nodes=bdd_nodes, exact_expression_fields=exact_fields, symbolic_terms=len(terms.nodes))
    finally:
        if proof is not None: proof.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    start = time.perf_counter()
    cases = [certify_case(phase) for phase in (None, *range(8))]
    sources = {Path(__file__).resolve()}
    for module in tuple(sys.modules.values()):
        filename = getattr(module, '__file__', None)
        if filename and '/fixed_rule/' in str(Path(filename).resolve()):
            sources.add(Path(filename).resolve())
    result = dict(passed=True, cases=cases, descriptor_sha256=f.self_description().digest(),
                  kernel_description_sha256=kernel.build().digest(),
                  source_sha256={str(path.relative_to(Path.cwd())): hashlib.sha256(path.read_bytes()).hexdigest()
                                 for path in sorted(sources)},
                  seconds=time.perf_counter()-start,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  scope='Complete procedure, geometry, Signal and static primary outputs for coherent '
                        'canonical zero-flag/Wf neighborhoods at every normalized Age, with zero or one head. '
                        'General physical flags/Wf require the existing context factorization and separate '
                        'flag recurrence; nonzero-flag intervals must have no mail. No GPU backend or noise theorem.')
    with args.output.open('x') as stream:
        stream.write(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(passed=True, cases=len(cases), seconds=result['seconds'])), flush=True)


if __name__ == '__main__':
    main()
