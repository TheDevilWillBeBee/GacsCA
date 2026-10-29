#!/usr/bin/env python3
"""Full-GR0 local restriction: one native Flag2 bit affects only itself.

GF/Age are canonical/common and all input Flag1/Workspace flags are zero.
Every simulation structure input and the external instruction are shared
free variables. These premises are not assumed to hold in arbitrary noisy
states or to follow from the abstract own-programme certificate alone.
"""
from pathlib import Path
import hashlib
import json
import sys
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'Report/proofs'))
from check_g17_schedule import Terms
import gray_scale_rule as proposed


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p = proposed.parameters()
    _, comp = proposed.cached(p)
    checked = 0
    records = []
    for reader in range(-5,6):
        terms = Terms()
        clock = [terms.var(('common_clock',bit)) for bit in range(p.m)]
        outputs = []
        for punctured in (False,True):
            node = [0,1]
            for name in comp.inputs:
                if name[0] == 'I':
                    value = terms.var(name)
                else:
                    _, offset, field, bit = name
                    if field == 'addr':
                        value = ((4096+reader+offset)%p.Q >> bit) & 1
                    elif field == 'age':
                        value = clock[bit]
                    elif field in ('f1','wf1','wf2'):
                        value = 0
                    elif field == 'f2':
                        value = int(punctured and reader+offset == 0)
                    else:
                        value = terms.var(('simulation',reader+offset,field,bit))
                node.append(value)
            for operation,a,b in comp.gates:
                node.append(terms.op(operation,node[a],node[b]))
            outputs.append({name:node[index] for name,index in comp.outputs.items()})
        different = [name for name in comp.outputs if outputs[0][name] != outputs[1][name]]
        wanted = [('y','f2',0)] if reader == 0 else []
        assert different == wanted, (reader,different)
        assert outputs[1]['y','f2',0] == int(reader == 0)
        checked += len(comp.outputs)-len(different)
        records.append(dict(reader=reader, changed_outputs=[list(name) for name in different],
                            symbolic_clock_bits=p.m, free_term_count=len(terms.terms)))
    result = dict(Q=p.Q,U=p.U,radius=5,width=proposed.width(p),
        candidate='GR0',checker_sha256=digest(__file__),proposal_sha256=digest(proposed.__file__),
        literal_module_sha256=digest(ROOT/'Report/proofs/gray_counterexamples/literal_maintenance.py'),
        netlist_sha256=comp.digest, full_output_and_lookup_equalities=checked,
        records=records, arbitrary_simulation_inputs_and_instruction=True,
        prescribed_input_workspace_flags_zero=True,
        full_rule_local_cofactor_proved=True, full_pristine_hierarchy_lift_proved=False,
        iid_unreliability_proved=False, intended_gray_refuted=False,
        scope='Exact full-rule local equality; invariant reachability and all-time Workspace-zero context remain separate.')
    (ROOT/'figs/gray_counterexamples/GR0_flag2_cofactor_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ('Q','U','full_output_and_lookup_equalities','full_rule_local_cofactor_proved','full_pristine_hierarchy_lift_proved')}))


if __name__ == '__main__':
    main()
