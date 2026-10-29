#!/usr/bin/env python3
"""Pin J87's module and forced maintenance to SP14's actual full circuit.

Zero raw Info closes births. All other bits, including instruction and
GF/Age, are free. This proves wiring, not authentic birth in damaged data.
"""
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca import rule_g
from gacsca.netlist import Net
import check_fast_mail_proposal as transport
import proposed_sparse_framed448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    _, source = proposed.actual_net(p)
    class BoundNet(Net):
        def input(self, key):
            if key[0] == 'x' and key[2] == 'info':
                return 0
            return super().input(key)
    namespace = dict(rule_g.__dict__, Net=BoundNet,
        maintenance=SimpleNamespace(build=proposed.proposed_build()[0]),
        schema=proposed.schema, service_build=proposed.service.build,
        OFFSETS=tuple(range(-12, 13)), sparse_controls=transport.sparse_controls,
        sparse_table=proposed.dependency_table(p))
    exec(compile(source, '<SP14 no-birth full incorporation cofactor>', 'exec'), namespace)
    n = namespace['build'](p)
    cells = {j: dict(
        packet_tag=[n.input_node['x', j, 'packet_tag', bit] for bit in range(4)],
        packet_valid=n.input_node['x', j, 'packet_valid', 0],
        packet_count=[n.input_node['x', j, 'packet_count', bit] for bit in range(11)],
        wf2=n.input_node['x', j, 'wf2', 0],
        flag_valid=n.input_node['x', j, 'service_valid', 0],
        flag_position=[n.input_node['x', j, 'service_position', bit] for bit in range(9)],
        flag_count=[n.input_node['x', j, 'service_count', bit] for bit in range(11)])
        for j in range(-5, 6)}
    expected = proposed.service.build(n, cells)
    correspondence = dict(wf2='wf2', packet_valid='packet_valid',
                          packet_tag='packet_tag', packet_count='packet_count',
                          service_valid='flag_valid', service_position='flag_position',
                          service_count='flag_count')
    component_count = 0
    for actual, module_field in correspondence.items():
        values = expected[module_field]
        values = values if isinstance(values, list) else [values]
        for bit, node in enumerate(values):
            assert n.outputs['y', actual, bit] == node, (actual, bit)
            component_count += 1
    maintenance_cells = {j: dict(
        addr=[n.input_node['x', j, 'addr', bit] for bit in range(p.k)],
        age=[n.input_node['x', j, 'age', bit] for bit in range(p.m)],
        **{key: n.input_node['x', j, key, 0] for key in ('f1', 'f2', 'wf1', 'wf2')})
        for j in range(-12, 13)}
    mt = proposed.proposed_build()[0](n, maintenance_cells, p.k, p.m,
        Q=p.Q, nb=p.nb, radix=p.R, pos_bits=p.PB, service_force=expected['service_force'])
    maintenance_count = 0
    for field in ('addr', 'age', 'f1', 'f2'):
        values = mt[field]
        values = values if isinstance(values, list) else [values]
        for bit, node in enumerate(values):
            assert n.outputs['y', field, bit] == node, (field, bit)
            maintenance_count += 1
    assert (component_count, maintenance_count) == (38, 28)
    out = ROOT / 'figs/robustness'
    receipt = dict(proposal='SP14', proposed_rule_change=True, active_G17_modified=False,
        SP13_modified=False, proposed_candidate_sha256=candidate.digest(),
        proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)),
        checker_sha256=digest(Path(__file__)),
        build_receipt_sha256=digest(out / 'SP14_program_build.json'),
        framed_service_proposal_source_sha256=digest(ROOT / 'Report/proofs/proposed_framed_service.py'),
        framed_service_certificate_sha256=digest(out / 'framed_service_certificate.json'),
        actual_maintenance_source_sha256=hashlib.sha256(proposed.proposed_build()[1].encode()).hexdigest(),
        full_generated_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        component_output_node_identities=component_count,
        maintenance_output_node_identities=maintenance_count,
        actual_pressure_is_computed_coded_valid=True,
        all_raw_Info_zero=True, every_other_raw_bit_and_instruction_free=True,
        actual_no_birth_rule_exactly_incorporates_J87=True,
        source_authenticity_or_no_birth_premise_on_general_GF_established=False,
        full_upper_error_map_established=False, global_reliability_established=False,
        scope='universal full-rule component/maintenance wiring cofactor; conditional eroder retains J87 premises; ROBUSTNESS J88')
    (out / 'SP14_framed_incorporation_certificate.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(component_identities=38, maintenance_identities=28, all_equal=True)))


if __name__ == '__main__':
    main()
