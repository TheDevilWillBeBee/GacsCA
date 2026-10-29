#!/usr/bin/env python3
"""Literal counterexample to the unmodified scheduler's XOR set folding.

Evaluates two saved abstract listings on one explicit raw neighborhood.
It does not run a physically invalid compiled rule or alter jobsched.py.
The separate universal verifier proves the replacement program's outputs.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import numpy as np
from gacsca import jobsched
import proposed_sparse_liveness448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def literal_listing(candidate,listing,values):
    p,comp = candidate.p,candidate.comp
    nodes = [False,True]+[bool(values[key]) for key in comp.inputs]
    for operation,a,b in comp.gates:
        nodes.append(nodes[a] and nodes[b] if operation == 0 else
                     nodes[a] or nodes[b] if operation == 1 else nodes[a] != nodes[b])
    names = proposed.source_names(p)
    profile = {(row['field'],row['bit']):row for row in proposed.dependency_table(p)}
    at = {}
    live = set(comp.outputs.values())
    for _,a,b in comp.gates:
        live.update((a,b))
    for key in comp.inputs:
        if key[0] != 'x' or comp.index[key] not in live:
            continue
        _,offset,field,bit = key
        row = profile[field,bit]
        name = ('info',0) if offset == 0 else ('ln',row['offsets'].index(offset))
        at[row['address'],names.index(name)] = bool(values[key])
    regs = [[None]*p.L for _ in range(p.fronts)]
    scratch,hold = {},{}
    matched = False
    wrong_writes = []
    for seq,page,tick,front,cell,operation,kind,a,b,dest,note in listing:
        if not matched and page > p.MP:
            matched = True
            regs = [[None]*p.L for _ in range(p.fronts)]
            for bit in range(p.IW):
                regs[0][p.k+bit] = bool(values.get(('I',bit),False))

        def read(code):
            field,index = names[code]
            if field == 'reg':
                assert regs[front][index] is not None
                return regs[front][index]
            if field == 'const':
                return bool(index)
            if field == 'scr':
                return scratch[cell,index]
            return at[cell,code]

        x,y = read(a),read(b)
        value = x and y if operation == 0 else x or y if operation == 1 else x != y if operation == 2 else x and not y
        node = note[-1]
        if isinstance(node,int) and node < len(nodes) and value != nodes[node]:
            wrong_writes.append(dict(sequence=seq,node=node,page=page,cell=cell,front=front,note=note,
                                     expected=int(nodes[node]),actual=int(value)))
        if kind == 0:
            regs[front][dest] = value
        elif kind == 1:
            hold[cell] = value
        elif kind == 2:
            scratch[cell,dest] = value
    reference = np.array([nodes[comp.outputs['y',field,bit]] for field,bit in candidate.rows],dtype=bool)
    actual = np.array([hold[row['address']] for row in proposed.dependency_table(p)],dtype=bool)
    return reference,actual,wrong_writes


def main():
    out = ROOT/'figs/robustness'
    candidate = proposed.load_artifact()
    p,comp = candidate.p,candidate.comp
    neighborhood = np.zeros((candidate.W,25),dtype=bool)
    for offset in range(-5,1):
        state = neighborhood[:,offset+12:offset+13]
        candidate.set_field(state,'addr',8+offset)
        candidate.set_field(state,'age',1-offset)
    values = {key:bool(neighborhood[candidate.row[key[2],key[3]],key[1]+12]) if key[0] == 'x' else False for key in comp.inputs}
    failed_path = out/'SP5_initial_schedule_failure_listing.json'
    valid_path = out/'SP5_program_listing.json'
    reference,bad,bad_writes = literal_listing(candidate,json.loads(failed_path.read_text()),values)
    reference2,valid,valid_writes = literal_listing(candidate,json.loads(valid_path.read_text()),values)
    assert np.array_equal(reference,reference2) and np.array_equal(reference,valid)
    assert not valid_writes
    assert not np.array_equal(reference,bad)
    reference_fields = {field:int(candidate.field(reference[:,None],field)[0]) for field in ('addr','age','f1','f2')}
    failed_fields = {field:int(candidate.field(bad[:,None],field)[0]) for field in reference_fields}
    assert reference_fields['age'] == 2 and failed_fields['age'] != 2
    with proposed.compiler_input_map():
        dag = jobsched.Dag(p,comp,proposed.layout(p))
    repeated = {str(node):list(leaves) for node,(op,leaves) in dag.nary.items() if op == jobsched.M_XOR and len(set(leaves)) < len(leaves)}
    assert repeated
    first = bad_writes[0]
    assert str(first['node']) in repeated
    asset = out/'SP5_xor_scheduler_witness.npz'
    np.savez_compressed(asset,neighborhood=neighborhood,reference=reference,failed=bad,verified=valid)
    result = dict(proposal='SP5',proposed_rule_change=True,active_G17_modified=False,
                  proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=comp.digest,
                  proposal_source_sha256=digest(Path(proposed.__file__)),checker_sha256=digest(Path(__file__)),
                  jobscheduler_sha256=digest(ROOT/'gacsca/jobsched.py'),
                  isolated_scheduler_helper_sha256=digest(ROOT/'Report/proofs/xor_multiplicity_scheduler.py'),
                  failed_build_receipt_sha256=digest(out/'SP5_initial_schedule_failure.json'),
                  failed_listing_sha256=digest(failed_path),verified_listing_sha256=digest(valid_path),
                  verified_schedule_receipt_sha256=digest(out/'SP5_symbolic_schedule.json'),
                  input_asset_sha256=digest(asset),central_Address=8,central_Age=1,
                  left_Address_words=[3,4,5,6,7],left_Age_words=[6,5,4,3,2],
                  all_right_raw_words_zero=True,other_raw_fields_zero=True,external_instruction_word=0,
                  expected_output_fields=reference_fields,failed_output_fields=failed_fields,
                  first_wrong_scheduled_value=first,repeated_XOR_leaf_nodes=repeated,
                  failed_physical_Hold_bits=[candidate.rows[index] for index in np.flatnonzero(reference != bad)],
                  failed_intermediate_write_count=len(bad_writes),verified_intermediate_write_count=0,
                  statement='literal Boolean counterexample to the original scheduled output on a valid-address neighborhood; binary-tree workaround verified for this witness and universal outputs separately',
                  active_scheduler_source_modified=False,global_reliability_established=False)
    (out/'xor_multiplicity_scheduler_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(reference=reference_fields,failed=failed_fields,
                          failed_output_bits=len(result['failed_physical_Hold_bits']),first_wrong_node=first['node'])),flush=True)


if __name__ == '__main__':
    main()
