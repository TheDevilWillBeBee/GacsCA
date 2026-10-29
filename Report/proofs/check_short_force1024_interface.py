#!/usr/bin/env python3
"""Exact SP29 graph/layout identity with the retained two-Q family member."""
from dataclasses import asdict
from pathlib import Path
import hashlib
import json
import sys

import numpy as np

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca.netlist import Compiled
import proposed_sparse_short_force1024 as proposed
import proposed_sparse_distant_epoch1024 as baseline
import proposed_sparse_short_epoch_duration as family


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    p=proposed.parameters();old=baseline.parameters()
    assert asdict(p)==asdict(old)
    assert p.fam() is proposed
    actual=Compiled(proposed.full_net(p)[0])
    retained=Compiled(family.full_net(old,2048)[0])
    assert actual.inputs==retained.inputs
    assert actual.gates==retained.gates
    assert actual.outputs==retained.outputs
    assert actual.digest==retained.digest
    _,cached=proposed.cached(p)
    assert cached.inputs==actual.inputs and cached.gates==actual.gates and cached.outputs==actual.outputs
    assert proposed.schema(p)==baseline.schema(old)
    assert proposed.width(p)==baseline.width(old)==842
    assert np.array_equal(proposed.layout(p),baseline.layout(old))
    assert proposed.dependency_table(p)==baseline.dependency_table(old)
    assert proposed.generated_source(p)==baseline.generated_source(old)
    receipt=dict(
        scope='SP29 exact constructor/cache graph, SF source, layout and parameter identity with retained D2Q family member',
        proposed_rule_change=True,force_duration=2048,baseline_force_duration=4096,
        proposed_params=asdict(p),Q=p.Q,U=p.U,T_wf=p.T_wf,width=proposed.width(p),
        full_boolean_netlist_sha256=actual.digest,retained_D2Q_family_netlist_sha256=retained.digest,
        gates=len(actual.gates),input_names=len(actual.inputs),output_bits=len(actual.outputs),
        complete_graph_arrays_compared=True,construction_cache_is_same_complete_graph=True,
        own_compiler_family_bound_to_new_module=True,no_other_parameter_or_SF_equation_change=True,
        layout_and_capture_table_identity=True,whole_netlist_identity_proved=True,
        checksum_equality_is_not_the_only_graph_identity_check=True,
        checker_sha256=digest(__file__),proposal_source_sha256=digest(proposed.__file__),
        parent_source_sha256=digest(baseline.__file__),duration_family_source_sha256=digest(family.__file__),
        netlist_library_sha256=digest(ROOT/'gacsca/netlist.py'),
        active_G17_modified=False,SP28_modified=False,
        matching_programme_or_encoded_simulation_verified=False,global_reliability_established=False)
    path=ROOT/'figs/robustness/SP29_interface_identity.json'
    path.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({k:receipt[k] for k in ('Q','U','T_wf','width','gates','whole_netlist_identity_proved',
                                          'global_reliability_established')},indent=2))


if __name__=='__main__':
    main()
