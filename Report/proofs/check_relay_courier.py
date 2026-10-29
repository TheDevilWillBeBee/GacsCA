#!/usr/bin/env python3
"""SP6 actual-rule protected ML/Info/Workspace identities.

Conditional coherent copies and prescribed geometry are explicit premises;
this does not prove capture provenance, island erosion or iid reliability.
"""
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca import rule_g
from gacsca.netlist import Net, Compiled, const_word
import proposed_sparse_relay448 as proposed
import check_fast_mail_proposal as transport
from check_shifted_halfline import dominant_bit


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    actual, source = proposed.actual_net(p)
    assert Compiled(actual).digest == candidate.comp.digest
    maintenance, _ = proposed.proposed_build(symbolic=True)
    tagged = set(proposed.fivefold_fields(p))
    phase = -1
    source_primary = 1+p.lo
    load = p.courier_ticks()[1]
    rows = []

    def bound(physical, clock):
        class BoundNet(Net):
            def input(self, key):
                if key[0] == 'x':
                    _, offset, field, bit = key
                    position = physical+offset
                    if field == 'addr':
                        address = (position+phase)%p.Q if position < p.Q else position%p.Q
                        return (address >> bit) & 1
                    if field == 'age':
                        return (p.age_code(clock) >> bit) & 1
                    if field == 'f1':
                        return int(1 <= position < p.Q)
                    if field in ('f2', 'wf1', 'wf2', 'pend'):
                        return 0
                    if field in tagged:
                        width = proposed.logical_width(field, p)
                        primary = position+bit//width-2
                        return super().input(('coherent', primary, field, bit%width))
                return super().input(key)
        namespace = dict(rule_g.__dict__, Net=BoundNet, maj5=dominant_bit,
                         maintenance=SimpleNamespace(build=maintenance),
                         OFFSETS=tuple(range(-12, 13)),
                         sparse_controls=transport.sparse_controls,
                         sparse_table=proposed.dependency_table(p))
        exec(compile(source, '<SP6 coherent protected relay>', 'exec'), namespace)
        net = namespace['build'](p)
        assert [net.outputs['y','addr',bit] for bit in range(p.k)] == const_word((physical-1)%p.Q,p.k)
        assert [net.outputs['y','age',bit] for bit in range(p.m)] == const_word(p.age_code(clock+1),p.m)
        assert net.outputs['y','f1',0] == 1
        return net

    # Load at input clock25288, then55 unit-left transfers. Each of the
    # five holders of the moving logical bit is already flagged.
    for clock in range(load,p.T_sig):
        primary = source_primary-(clock-load)
        expected_field = 'hold' if clock == load else 'ml'
        expected_primary = primary if clock == load else primary+1
        for physical in range(primary-2,primary+3):
            net = bound(physical,clock)
            slot = primary-physical
            got = net.outputs['y','ml',slot+2]
            expected = net.input(('coherent',expected_primary,expected_field,0))
            assert got == expected, (clock,primary,physical,got,expected)
        rows.append(dict(input_clock=clock,target_physical_primary=primary,
                         computed_logical_Address=primary-1,
                         five_flagged_holders=list(range(primary-2,primary+3)),
                         source_field=expected_field,source_physical_primary=expected_primary))
    assert len(rows) == 56 and rows[-1]['target_physical_primary'] == 4
    signal_outputs = 0
    for physical in range(2,7):
        net = bound(physical,p.T_sig)
        got = net.outputs['y','info',4-physical+2]
        assert got == net.input(('coherent',4,'ml',0))
        signal_outputs += 1
    workspace_outputs = 0
    for clock in (p.T_wf,p.T_wf+2*p.Q-1):
        for physical in range(1,6):
            net = bound(physical,clock)
            assert net.outputs['y','wf2',0] == net.input(('coherent',4,'info',0))
            workspace_outputs += 1
    for clock in (p.T_wf-1,p.T_wf+2*p.Q):
        for physical in range(1,6):
            assert bound(physical,clock).outputs['y','wf2',0] == 0
    result = dict(proposal='SP6',proposed_rule_change=True,active_G17_modified=False,
                  proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
                  proposal_source_sha256=digest(Path(proposed.__file__)),checker_sha256=digest(Path(__file__)),
                  SP5_proposal_source_sha256=digest(ROOT/'Report/proofs/proposed_sparse_liveness448.py'),
                  transport_checker_sha256=digest(Path(transport.__file__)),
                  dominant_bit_helper_sha256=digest(ROOT/'Report/proofs/check_shifted_halfline.py'),
                  build_receipt_sha256=digest(ROOT/'figs/robustness/SP6_program_build.json'),
                  actual_generated_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                  majority_truth_assignments_checked=transport.maj5_truth(),
                  prescribed_left_geometry_phase=-1,prescribed_right_geometry_phase=0,
                  coherent_copy_premise=True,pending_writes_zero_premise=True,
                  Flag1_one_on_all_checked_holders=True,rows=rows,
                  protected_ML_copy_identities=5*len(rows),special_Info_copy_identities=signal_outputs,
                  Workspace_Flag2_active_endpoint_identities=workspace_outputs,
                  Workspace_Flag2_inactive_endpoint_zero_identities=10,
                  active_Workspace_clock_interval=[p.T_wf,p.T_wf+2*p.Q-1],
                  interval_interior_uses_same_literal_control_value=True,
                  signal_reaches_Info_if_source_Hold_copies_coherent=True,
                  capture_provenance_established=False,arbitrary_island_repair_established=False,
                  infinite_hierarchy_equivalence_established=False,global_reliability_established=False,
                  status='proved conditional actual-rule source identities; no repair or positive iid theorem')
    (ROOT/'figs/robustness/SP6_relay_courier_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(ML_identities=280,Info_identities=signal_outputs,Workspace_identities=workspace_outputs)))


if __name__ == '__main__':
    main()
