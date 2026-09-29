"""Structural complete-descriptor cut plus exhaustive majority-gate proof.

Every raw procedure input reaches every output only through an identified
five-replica majority gate. With identical nonprocedure inputs and unchanged
corrected words, complete F outputs agree. Projection then gives the same G.
"""
import argparse
import itertools
import json
from pathlib import Path
import resource
import time

from gacsca.fixed_rule import retimed_holder_rule as f
from gacsca.fixed_rule.wordcode import Builder,Program,NAND,ADD,EQ,LIT,MASK
from experiments.fixed_rule.audit_small_holder_position_events import sha


def majority(b, leaves, width, *, broken=False):
    if width == 1:
        return b.count(leaves,2 if broken else 3)
    a,d,e,x,y = leaves
    triple = b.band(b.band(a,d),e)
    pairs = b.bor(b.bor(b.band(a,d),b.band(a,e)),b.band(d,e))
    any3 = b.bor(b.bor(a,d),e)
    return b.bor(b.bor(triple,b.band(pairs,b.bor(x,y))),b.band(any3,b.band(x,y)))


class Structure:
    def __init__(self):
        self.ids = {}

    def intern(self, node):
        if node not in self.ids:
            self.ids[node] = len(self.ids)
        return self.ids[node]

    def wires(self, program):
        values = [self.intern(('input',i)) for i in range(program.inputs)]
        for opcode,a,b in program.operations:
            if opcode == LIT:
                key = ('literal',a)
            else:
                a,b = values[a],values[b]
                if opcode in (NAND,ADD,EQ):
                    a,b = sorted((a,b))
                key = (opcode,a,b)
            values.append(self.intern(key))
        return values


def gates():
    rows = []
    for width in (1,64):
        b = Builder(5); program = b.finish((majority(b,tuple(range(5)),width),))
        if width == 64:
            assert all(op in (NAND,LIT) for op,_,_ in program.operations),'word gate is not bit-local'
        one = 1 if width == 1 else MASK
        for mask in range(32):
            got = program.evaluate(tuple(one if mask>>i&1 else 0 for i in range(5)))[0]
            assert got == (one if mask.bit_count()>=3 else 0),(width,mask)
        minority = 0
        for damaged in itertools.combinations(range(5),2):
            for healthy,x,y in itertools.product((0,one),repeat=3):
                inputs = [healthy]*5
                inputs[damaged[0]],inputs[damaged[1]] = x,y
                assert program.evaluate(inputs)[0] == healthy
                minority += 1
        rows.append(dict(width=width,all_boolean_assignments=32,minority_assignments=minority,
                         bit_local=width==64,passed=True))
    return rows


def cut(*, broken=False):
    desc = f.self_description(); structure = Structure(); actual = structure.wires(desc)
    by_node = {}
    for wire,node in enumerate(actual):
        by_node.setdefault(node,[]).append(wire)
    roots = {}; groups = []
    for primary in range(-4,5):
        for name,width in f.PROCEDURE:
            leaves = tuple((primary+d+7)*f.FIELDS+f.COL[f's{2-d}_{name}'] for d in f.OFFSETS)
            b = Builder(desc.inputs); program = b.finish((majority(b,leaves,width,broken=broken),))
            nodes = structure.wires(program); found = by_node.get(nodes[program.outputs[0]],())
            for wire in found:
                roots[wire] = (primary,name,width)
            if found:
                groups.append(dict(primary=primary,field=name,width=width,input_wires=leaves,root_wires=list(found)))
    # Reject the deliberately wrong Boolean-majority identification, rather
    # than trusting an inventory of gate names or a rewritten source function.
    stack = list(desc.outputs); seen = set(); used = set(); raw = set()
    procedure_names = {f's{k}_{name}' for k in range(5) for name,_ in f.PROCEDURE}
    while stack:
        wire = stack.pop()
        if wire in seen:
            continue
        seen.add(wire)
        if wire in roots:
            used.add(wire); continue
        if wire<desc.inputs:
            if f.SCHEMA[wire%f.FIELDS][0] in procedure_names:
                raw.add(wire)
            continue
        opcode,a,b = desc.operations[wire-desc.inputs]
        if opcode != LIT:
            stack.extend((a,b))
    assert not raw,('unprotected raw procedure dependency',sorted(raw)[:12])
    assert used and len(desc.outputs) == f.FIELDS
    return dict(passed=True,complete_raw_outputs=f.FIELDS,identified_majority_groups=len(groups),
                reached_cut_roots=len(used),remaining_raw_procedure_inputs=0,groups=groups,
                traversed_wires=len(seen),interned_structural_nodes=len(structure.ids))


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--output',required=True); args = parser.parse_args()
    out = Path(args.output)
    if out.exists():
        raise FileExistsError('preserve evidence')
    start = time.perf_counter(); gate_checks = gates(); complete = cut()
    try:
        cut(broken=True)
    except AssertionError as error:
        rejected = str(error)
    else:
        raise AssertionError('wrong Boolean threshold escaped the structural cut')
    files = [Path(__file__),Path(f.__file__),Path('gacsca/fixed_rule/retimed_holder_description.py'),Path('gacsca/fixed_rule/wordcode.py')]
    result = dict(passed=True,gate_checks=gate_checks,complete_descriptor_cut=complete,
                  wrong_threshold_mutation_rejected=rejected,descriptor_sha256=f.self_description().digest(),
                  source_sha256={str(path):sha(path) for path in files},seconds=time.perf_counter()-start,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  theorem='If two raw neighborhoods have identical nonprocedure fields and equal five-replica corrected values for every reached logical procedure input, their complete F outputs agree. In particular, changing at most two copies per initially coherent logical procedure field preserves the next complete F output. Fixed projection/lift yields identical G outputs too.',
                  limitation='One-step procedure-replica correction only. Geometry, Signal and Wf defects are not covered; three bad copies can persist. No general noise threshold or hierarchical amplification theorem.')
    out.write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps({k:v for k,v in result.items() if k!='complete_descriptor_cut'},indent=2),flush=True)


if __name__ == '__main__':
    main()
