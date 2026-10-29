#!/usr/bin/env python3
"""SP5 shifted-colony GF/Flag trap and blocked physical Flag2 output.

The adjoining GF/flag inputs are prescribed at each tick. This is a local
invariant under driven inputs, not an autonomous finite-island theorem.
All simulation data, instruction bits, and the common17-bit clock are free.
"""
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca import rule_g
from gacsca.netlist import Net,Compiled,const_word,mixed_age_increment
import proposed_sparse_liveness448 as proposed
import check_fast_mail_proposal as transport


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    maintenance,maintenance_source = proposed.proposed_build()
    actual,source = proposed.actual_net(p)
    assert Compiled(actual).digest == candidate.comp.digest
    rows = []
    for physical in range(p.Q):
        class BoundNet(Net):
            def input(self,key):
                if key[0] == 'x':
                    _,offset,field,bit = key
                    position = physical+offset
                    in_prefix = 0 <= position < p.Q
                    if field == 'addr':
                        address = (position-1)%p.Q if position < p.Q else position%p.Q
                        return (address >> bit) & 1
                    if field == 'age':
                        return super().input(('common_clock',bit))
                    if field == 'f1':
                        return int(1 <= position < p.Q)
                    if field in ('f2','wf2'):
                        return 0
                    if field == 'wf1' and not in_prefix:
                        return 0
                return super().input(key)

        namespace = dict(rule_g.__dict__,Net=BoundNet,maintenance=SimpleNamespace(build=maintenance),
                         OFFSETS=tuple(range(-12,13)),sparse_controls=transport.sparse_controls,
                         sparse_table=proposed.dependency_table(p))
        exec(compile(source,'<actual SP5 with shifted-colony conditional input>', 'exec'),namespace)
        bounded = namespace['build'](p)
        clock = [bounded.input_node['common_clock',bit] for bit in range(p.m)]
        new_clock = mixed_age_increment(bounded,clock,p.PB,p.R,p.nb)
        assert [bounded.outputs['y','addr',bit] for bit in range(p.k)] == const_word((physical-1)%p.Q,p.k),physical
        assert [bounded.outputs['y','age',bit] for bit in range(p.m)] == new_clock,physical
        assert bounded.outputs['y','f1',0] == int(physical > 0),physical
        assert bounded.outputs['y','f2',0] == 0,physical
        assert bounded.outputs['y','wf2',0] == 0,physical
        if physical > 0:
            assert all(bounded.outputs['y','ml',bit] == 0 for bit in range(5)),physical
            assert all(bounded.outputs['y','mr',bit] == 0 for bit in range(5)),physical
        # Even a correct command already sitting at the special Info position
        # cannot affect Workspace.Flag2: left_end entails computed Flag1=1.
        rows.append(dict(physical_site=physical,computed_Address=(physical-1)%p.Q,
                         computed_Flag1=int(physical > 0),computed_Flag2=0,computed_Workspace_Flag2=0))
    out = ROOT/'figs/robustness'
    result = dict(proposal='SP5',proposed_rule_change=True,active_G17_modified=False,SP4_modified=False,
                  proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
                  proposal_source_sha256=digest(Path(proposed.__file__)),checker_sha256=digest(Path(__file__)),
                  full_rule_sha256=digest(ROOT/'gacsca/rule_g.py'),
                  transport_checker_sha256=digest(Path(transport.__file__)),
                  liveness_helper_sha256=digest(ROOT/'Report/proofs/check_blank_neighbor_clock.py'),
                  actual_generated_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                  actual_maintenance_source_sha256=hashlib.sha256(maintenance_source.encode()).hexdigest(),
                  build_receipt_sha256=digest(out/'SP5_program_build.json'),
                  holder_cases=len(rows),physical_GF_and_two_flags_output_identities=len(rows)*(p.k+p.m+2),
                  Workspace_Flag2_zero_output_identities=len(rows),common_raw_clock_bits_free=p.m,
                  all_ML_and_MR_zero_output_identities=2*5*(p.Q-1),
                  all_simulation_data_and_instruction_bits_free=True,
                  Workspace_Flag1_inputs_free_in_damaged_prefix=True,
                  prescribed_left_geometry_phase=-1,prescribed_right_geometry_phase=0,
                  exterior_flags_Workspace_zero=True,rows=rows,
                  source_load_copy_holders=[p.lo-1,p.lo,p.lo+1,p.lo+2,p.lo+3],
                  source_load_all_five_ML_copies_cleared_by_Flag1=True,
                  trapped_lower_flag_pattern='Flag1=1 at physical1..447,0 at physical0; Flag2=Workspace.Flag2=0',
                  status='proved one-update conditional Boolean identities; iteration holds while adjoining GF/flag inputs keep these prescribed values',
                  autonomous_finite_island_persistence_established=False,
                  initial_infinite_hierarchy_reachability_established=False,
                  positive_iid_threshold_established=False,global_reliability_established=False)
    (out/'SP5_colony_trap_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(holders=len(rows),GF_two_flags_identities=result['physical_GF_and_two_flags_output_identities'],
                          Workspace_Flag2_zero_identities=len(rows),global_reliability_established=False)),flush=True)


if __name__ == '__main__':
    main()
