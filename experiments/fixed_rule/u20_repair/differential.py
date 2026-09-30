"""All-421-word parity checks for the private corrected U20 description."""
import argparse
from collections import Counter
from dataclasses import replace
import hashlib
import json
import random
import time

from gacsca.fixed_rule import spatial_epoch8 as spatial
from gacsca.fixed_rule import stream28_dual_core20 as core
from gacsca.fixed_rule import stream28_dual_holder_rule20 as holder
from gacsca.fixed_rule import stream28_dual_pass20 as physical
from gacsca.fixed_rule import stream28_dual_pass_optimized20 as old
from gacsca.fixed_rule.u20_repair import description, native


SCHEMA = holder.SCHEMA + tuple((f'spatial_{i}', width) for i, width in
                                enumerate(__import__('gacsca.fixed_rule.spatial_codec8',
                                                    fromlist=['WIDTHS']).WIDTHS))
AGES = sorted({0, 1, 2392, *(age + delta for age in
                    (*core.RESET_AGES, *core.ACTIVE_ENDS, *core.VOTE_AGES,
                     core.CAPTURE_AGE, physical.EARLY_CAPTURE_AGE,
                     physical.EARLY_RUN_START, physical.EARLY_RUN_STOP)
                    for delta in (-1, 0, 1) if 0 <= age + delta < core.U)})
KINDS = (core.MEM, core.SEND, core.LOOP, core.LOAD, core.META,
         core.LIT, core.HALT, core.IF_THIRD, core.BRANCH_THIRD,
         core.PACK3, *core.ALU_KINDS)


def _cell(rng, age, opcode):
    values = {name: rng.getrandbits(width) for name, width in holder.SCHEMA}
    values['age'] = age
    values['address'] = rng.randrange(core.Q)
    values['p3_kind'] = opcode
    values['p3_index'] = values['s2_pc']
    # A random typed state includes controller/mail fields in all five copies.
    h = holder.Cell(**values)
    s = spatial.Cell(address=rng.randrange(spatial.Q),
                     age=rng.randrange(spatial.PERIOD),
                     kind=rng.choice((spatial.SOURCE, spatial.GATE,
                                      spatial.OUTPUT)),
                     source_value=rng.getrandbits(64),
                     arg0=rng.getrandbits(64), arg1=rng.getrandbits(64),
                     ready=rng.randrange(4), result=rng.getrandbits(64),
                     done=rng.randrange(2), collision=rng.randrange(2))
    return physical.Cell(h, s)


def random_neighborhood(seed, age, opcode):
    rng = random.Random(seed)
    return tuple(_cell(rng, age, opcode) for _ in physical.NEIGHBORHOOD)


def coherent_neighborhood(age, opcode, offset, seed):
    rng = random.Random(seed)
    rows = []
    for j in physical.NEIGHBORHOOD:
        c = _cell(rng, age, opcode)
        h = replace(c.holder, address=(3000+j)%core.Q,
                    age=age, f1=0, f2=0,
                    **{f'w{i}_wf{k}': 0 for i in range(5)
                       for k in (1,2)})
        rows.append(replace(c, holder=h))
    # Force a STREAM source at the center. This is also a typed raw test of
    # every sign/magnitude of route count; exact launch branches are supplied
    # separately by layout route cases.
    center = rows[7]
    h = replace(center.holder,
                p3_kind=core.MEM,
                p3_b=(1 << (offset+7)) | (1 << core.STREAM_FIELD_SHIFT),
                s2_data=rng.getrandbits(64))
    rows[7] = replace(center, holder=h)
    return tuple(rows)


def words(neighborhood):
    return tuple(word for c in neighborhood for word in physical.encode_cell(c))


def compare(neighborhood, label, *, check_old=False):
    raw = words(neighborhood)
    expected = physical.encode_cell(physical.local_step(neighborhood))
    coded = description.build().evaluate(raw)
    compiled = native.evaluate(raw)
    if len(expected) != len(coded) or len(expected) != len(compiled):
        raise AssertionError(('dropped raw outputs', label, len(expected),
                              len(coded), len(compiled)))
    for field, (a, b, c) in enumerate(zip(expected, coded, compiled)):
        if a != b or a != c:
            raise AssertionError(dict(label=label, field=field,
                                      name=SCHEMA[field][0], literal=a,
                                      wordcode=b, native=c,
                                      input_sha256=hashlib.sha256(
                                          bytes(__import__('array').array('Q',raw))).hexdigest()))
    if check_old:
        return [i for i, (a,b) in enumerate(zip(expected,old.build().evaluate(raw)))
                if a != b]
    return []


def run(seed=20260929, random_cases=80):
    start = time.monotonic()
    program = description.build()
    if (program.inputs, len(program.outputs), program.digest()) != (
            15*physical.FIELDS, physical.FIELDS,
            '232fa6b96f3e2887975337ff52564e54d3a2f7fc59cbf59580e2adf8e1429f88'):
        raise AssertionError('corrected program identity changed')
    coverage = Counter()
    cases = 0
    for i in range(random_cases):
        age = AGES[i % len(AGES)] if i < len(AGES) else random.Random(seed+i).randrange(core.U)
        opcode = KINDS[i % len(KINDS)]
        compare(random_neighborhood(seed+i, age, opcode),
                f'random:{i}:age={age}:opcode={opcode}')
        coverage[f'opcode_{opcode}'] += 1
        coverage[f'age_{age}'] += 1
        cases += 1
    for offset in range(-7,8):
        if offset == 0: continue
        compare(coherent_neighborhood(2392,core.MEM,offset,seed+offset),
                f'coherent_route_{offset}')
        coverage[f'route_offset_{offset}'] += 1
        cases += 1
    # Raw trajectory samples use F repeatedly on a short closed ring.
    ring = list(random_neighborhood(seed+999,0,core.MEM))
    for tick in range(3):
        for site in (0,7,14):
            hood = tuple(ring[(site+j)%len(ring)] for j in physical.NEIGHBORHOOD)
            compare(hood, f'trajectory_t{tick}_site{site}')
            cases += 1
        ring = [physical.local_step(tuple(ring[(site+j)%len(ring)]
                          for j in physical.NEIGHBORHOOD))
                for site in range(len(ring))]
    _, c_digest, target = native.library()
    return dict(cases=cases, outputs_checked=cases*physical.FIELDS,
                opcodes={str(k):coverage[f'opcode_{k}'] for k in KINDS},
                route_offsets={str(k):coverage[f'route_offset_{k}']
                               for k in range(-7,8) if k},
                age_classes=len([k for k in coverage if k.startswith('age_')]),
                wordcode_sha256=program.digest(),native_source_sha256=c_digest,
                native_library=target,duration_seconds=round(time.monotonic()-start,3))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--random-cases',type=int,default=80)
    parser.add_argument('--seed',type=int,default=20260929)
    parser.add_argument('--output')
    args = parser.parse_args()
    receipt = run(args.seed,args.random_cases)
    rendered = json.dumps(receipt,indent=2,sort_keys=True)+'\n'
    if args.output:
        from pathlib import Path
        target=Path(args.output)
        if target.exists():raise FileExistsError(target)
        target.write_text(rendered)
    print(rendered)
