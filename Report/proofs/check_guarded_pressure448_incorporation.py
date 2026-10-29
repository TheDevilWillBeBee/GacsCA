#!/usr/bin/env python3
"""J100: full SP15 guard/pressure wiring and canonical birth cofactors.

All original equations are used. Proof observations add no stored state.
This pins standalone J94/J99 modules to SP15; initialized-source proof
does not become general damaged-input bootstrap or iid reliability.
"""
from itertools import combinations
from pathlib import Path
from types import FunctionType, SimpleNamespace
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca import rule_g
from gacsca.netlist import Net, Compiled, w_mux, w_add_const
from check_shifted_halfline import dominant_bit
import check_fast_mail_proposal as transport
import proposed_sparse_guarded_pressure448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def full_net(p, net_class=Net, majority=None, maintenance=None, observe=False):
    _, source = proposed.actual_net(p)
    if observe:
        marker = "    packet_birth = n.all([w_eq_const(n, repair_age, p.age_code(p.T_wf)), packet_command, n.NOT(packet_guard)])\n"
        assert source.count(marker) == 1
        source = source.replace(marker, marker + "    n.set_output(('proof', 'guard'), packet_guard)\n    n.set_output(('proof', 'birth'), packet_birth)\n")
    namespace = dict(rule_g.__dict__, Net=net_class,
        LANE_OFFSETS=proposed.LANE_OFFSETS, logical_width=proposed.logical_width,
        source_names=proposed.source_names, schema=proposed.schema,
        maintenance=SimpleNamespace(build=maintenance or proposed.proposed_build()[0]),
        service_build=proposed.service.build, packet_guard_build=proposed.guard.build,
        OFFSETS=tuple(range(-12, 13)), sparse_controls=transport.sparse_controls,
        sparse_table=proposed.dependency_table(p))
    for name, fn in rule_g.__dict__.items():
        if isinstance(fn, FunctionType) and fn.__module__ == rule_g.__name__:
            namespace[name] = FunctionType(fn.__code__, namespace, fn.__name__, fn.__defaults__, fn.__closure__)
    namespace.update(logical_width=proposed.logical_width,
        source_names=proposed.source_names, schema=proposed.schema)
    if majority is not None:
        namespace['maj5'] = majority
    exec(compile(source, '<SP15 exact full-rule proof namespace>', 'exec'), namespace)
    return namespace['build'](p), source


def wiring(candidate):
    p = candidate.p
    raw, _ = full_net(p)
    assert Compiled(raw).digest == candidate.comp.digest
    n, observed_source = full_net(p, observe=True)
    cells = {j: dict(packet_tag=[n.input_node['x', j, 'packet_tag', b] for b in range(4)],
        packet_valid=n.input_node['x', j, 'packet_valid', 0],
        packet_count=[n.input_node['x', j, 'packet_count', b] for b in range(11)],
        wf2=n.input_node['x', j, 'wf2', 0], flag_valid=n.input_node['x', j, 'service_valid', 0],
        flag_position=[n.input_node['x', j, 'service_position', b] for b in range(9)],
        flag_count=[n.input_node['x', j, 'service_count', b] for b in range(11)]) for j in range(-6, 7)}
    result = proposed.service.build(n, {j: cells[j] for j in range(-5, 6)})
    assert n.outputs['proof', 'guard'] == proposed.guard.build(n, cells)
    mt_cells = {j: dict(addr=[n.input_node['x', j, 'addr', b] for b in range(p.k)],
        age=[n.input_node['x', j, 'age', b] for b in range(p.m)],
        **{f: n.input_node['x', j, f, 0] for f in ('f1', 'f2', 'wf1', 'wf2')}) for j in range(-12, 13)}
    mt = proposed.proposed_build()[0](n, mt_cells, p.k, p.m, Q=p.Q, nb=p.nb,
        radix=p.R, pos_bits=p.PB, service_force=result['service_force'])
    birth = n.outputs['proof', 'birth']
    expected = dict(wf2=n.OR(birth, result['wf2']),
        packet_valid=n.OR(birth, result['packet_valid']),
        packet_tag=w_mux(n, birth, w_add_const(n, mt['addr'][:4], 15), result['packet_tag']),
        packet_count=w_mux(n, birth, [0]*11, result['packet_count']),
        service_valid=result['flag_valid'], service_position=result['flag_position'], service_count=result['flag_count'])
    components, maintenance = 0, 0
    for field, value in expected.items():
        for b, node in enumerate(value if isinstance(value, list) else [value]):
            assert n.outputs['y', field, b] == node, (field, b)
            components += 1
    for field in ('addr', 'age', 'f1', 'f2'):
        for b, node in enumerate(mt[field] if isinstance(mt[field], list) else [mt[field]]):
            assert n.outputs['y', field, b] == node
            maintenance += 1
    assert (components, maintenance) == (38, 28)
    return components, maintenance, observed_source


def canonical_birth(p, address, faults):
    class BoundNet(Net):
        def input(self, key):
            if key[0] == 'x':
                _, off, field, bit = key
                if off not in faults:
                    if field == 'addr':
                        return ((address+off)%p.Q >> bit)&1
                    if field == 'age':
                        return (p.age_code(p.T_wf) >> bit)&1
                    if field in ('wf2','packet_tag','packet_valid','packet_count','service_valid','service_position','service_count'):
                        return 0
                    if field == 'info' and (address+off+bit-2)%p.Q == 3:
                        return super().input(('command',))
            return super().input(key)
    n, _ = full_net(p, net_class=BoundNet, majority=dominant_bit,
        maintenance=proposed.proposed_build(symbolic=True)[0])
    command = n.input(('command',))
    assert n.outputs['y', 'wf2', 0] == command
    assert n.outputs['y', 'packet_valid', 0] == command
    for b in range(4):
        assert n.outputs['y', 'packet_tag', b] == (command if ((address-1)>>b)&1 else 0)
    assert all(n.outputs['y', 'packet_count', b] == 0 for b in range(11))
    assert n.outputs['y', 'service_valid', 0] == 0
    assert all(n.outputs['y', 'service_position', b] == 0 for b in range(9))
    assert all(n.outputs['y', 'service_count', b] == 0 for b in range(11))


def main():
    candidate = proposed.load_artifact()
    components, maintenance, observed = wiring(candidate)
    cases = 0
    for address in range(1, 6):
        for faults in combinations(range(-6, 7), 2):
            canonical_birth(candidate.p, address, faults)
            cases += 1
        print(json.dumps(dict(canonical_birth_cases=cases)), flush=True)
    assert cases == 390
    out = ROOT/'figs/robustness'
    receipt = dict(proposal='SP15', proposed_rule_change=True, active_G17_modified=False, SP14_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)), checker_sha256=digest(Path(__file__)),
        guard_source_sha256=digest(Path(proposed.guard.__file__)),
        pressure_source_sha256=digest(Path(proposed.service.__file__)),
        base_rule_source_sha256=digest(ROOT/'gacsca/rule_g.py'),
        helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
        dominant_bit_helper_sha256=digest(ROOT/'Report/proofs/check_shifted_halfline.py'),
        transport_checker_sha256=digest(Path(transport.__file__)),
        build_receipt_sha256=digest(out/'SP15_program_build.json'),
        schedule_receipt_sha256=digest(out/'SP15_symbolic_schedule.json'),
        guard6_certificate_sha256=digest(out/'packet_guard6_certificate.json'),
        packet_pressure_certificate_sha256=digest(out/'packet_pressure_certificate.json'),
        actual_maintenance_source_sha256=hashlib.sha256(proposed.proposed_build()[1].encode()).hexdigest(),
        full_generated_source_sha256=hashlib.sha256(proposed.actual_net(candidate.p)[1].encode()).hexdigest(),
        proof_observation_generated_source_sha256=hashlib.sha256(observed.encode()).hexdigest(),
        independent_namespace_reconstruction_matches_actual_full_netlist=True,
        actual_unrestricted_packet_pressure_wiring=True, actual_radius_six_birth_guard_node_identity=True,
        free_all_raw_inputs_component_output_identities=components,
        free_all_raw_inputs_maintenance_output_identities=maintenance,
        canonical_thirteen_site_two_fault_birth_cofactors=cases,
        common_command_bit_free=True, every_other_Info_flag_data_and_instruction_bit_free=True,
        good_canonical_GF_and_clock_and_empty_components_required_for_birth_cofactors=True,
        initialized_packet_later_birth_E0_persistence_transfers_J94_J99=True,
        authentic_source_from_arbitrary_damaged_inputs_established=False,
        general_force_envelope_or_autonomous_boundary_established=False,
        full_encoded_or_higher_error_simulation_proved_by_this_checker=False,
        global_reliability_established=False,
        scope='actual full SP15 guard/pressure and output wiring identities plus canonical birth cofactors, ROBUSTNESS J100; no damaged-input bootstrap or iid theorem')
    (out/'SP15_guarded_pressure_incorporation_certificate.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(dict(component_identities=components, maintenance_identities=maintenance, birth_cases=cases)))


if __name__ == '__main__':
    main()
