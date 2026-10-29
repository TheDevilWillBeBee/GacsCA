#!/usr/bin/env python3
"""SP13 full-rule packet retention equals the certified isolated module.

Zero raw Info disables all births. Every GF/flag/Age/packet/data/I input
is otherwise free. This pins the module's actual incorporation; general
command birth and full damaged-input simulation remain unproved.
"""
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca import rule_g
from gacsca.netlist import Net,at_least,w_in_range
import check_fast_mail_proposal as transport
import proposed_sparse_timed448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    _,source = proposed.actual_net(p)
    class BoundNet(Net):
        def input(self,key):
            if key[0]=='x' and key[2]=='info':return 0
            return super().input(key)
    namespace = dict(rule_g.__dict__,Net=BoundNet,
        maintenance=SimpleNamespace(build=proposed.proposed_build()[0]),schema=proposed.schema,
        packet_build=proposed.timed_build_with_witness()[0],OFFSETS=tuple(range(-12,13)),
        sparse_controls=transport.sparse_controls,sparse_table=proposed.dependency_table(p))
    exec(compile(source,'<SP13 no-command actual packet cofactor>','exec'),namespace)
    n = namespace['build'](p)
    cells = {j:dict(tag=[n.input_node['x',j,'packet_tag',b] for b in range(4)],
                    valid=n.input_node['x',j,'packet_valid',0],wf2=n.input_node['x',j,'wf2',0],
                    count=[n.input_node['x',j,'packet_count',b] for b in range(11)])
             for j in range(-5,6)}
    expected = proposed.packet.build(n,cells)
    assert n.outputs['y','wf2',0] == expected['wf2']
    assert n.outputs['y','packet_valid',0] == expected['valid']
    assert [n.outputs['y','packet_tag',b] for b in range(4)] == expected['tag']
    assert [n.outputs['y','packet_count',b] for b in range(11)] == expected['count']
    exposed = proposed.timed_build_with_witness()[0](n,cells)
    assert {key:exposed[key] for key in expected}==expected
    out = ROOT/'figs/robustness'
    receipt = dict(proposal='SP13',proposed_rule_change=True,active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)),checker_sha256=digest(Path(__file__)),
        actual_maintenance_source_sha256=hashlib.sha256(proposed.proposed_build()[1].encode()).hexdigest(),
        full_generated_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        build_receipt_sha256=digest(out/'SP13_program_build.json'),
        timed_packet_proposal_source_sha256=digest(ROOT/'Report/proofs/proposed_timed_cohort_packet.py'),
        timed_packet_generated_source_sha256=hashlib.sha256(proposed.timed_build_with_witness()[1].encode()).hexdigest(),
        timed_packet_certificate_sha256=digest(out/'timed_cohort_packet_certificate.json'),
        packet_ancestry_certificate_sha256=digest(out/'cohort_packet_ancestry_certificate.json'),
        packet_output_node_identities=17,all_raw_Info_zero=True,
        every_other_raw_bit_and_instruction_free=True,
        no_command_actual_packet_equals_certified_module=True,
        witness_wrapper_preserves_all_seventeen_packet_output_bits=True,
        general_command_birth_or_full_damaged_input_map_established=False,
        global_reliability_established=False,scope='universal actual full-rule retention cofactor; ROBUSTNESS J84')
    (out/'SP13_packet_retention_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(output_identities=17,all_equal=True)))


if __name__=='__main__':
    main()
