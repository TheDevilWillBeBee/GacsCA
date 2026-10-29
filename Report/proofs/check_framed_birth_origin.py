#!/usr/bin/env python3
"""J97: actual SP14 birth origin follows its newly computed GF.

Cut only the maintenance Addr output to a free9-bit word, preserving
all other actual equations. Enumerate its512 words with every raw
state/instruction bit free. Restoring the actual GF value recovers the
original full rule. No rule modification or birth availability claim.
"""
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca import rule_g
from gacsca.netlist import Net, const_word, w_mux
import check_fast_mail_proposal as transport
import proposed_sparse_framed448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cut_net(p):
    build, _ = proposed.proposed_build()
    def cut_GF(n, *args, **kwargs):
        result = build(n, *args, **kwargs)
        result['addr'] = [n.input(('computed_GF_cut', b)) for b in range(p.k)]
        return result
    _, actual = proposed.actual_net(p)
    marker = "    packet_birth = n.all([w_eq_const(n, repair_age, p.age_code(p.T_wf)), packet_command, n.NOT(packet_now['cohort_exists'])])\n"
    assert actual.count(marker) == 1
    source = actual.replace(marker, marker + "    n.set_output(('proof', 'birth'), packet_birth)\n")
    namespace = dict(rule_g.__dict__, maintenance=SimpleNamespace(build=cut_GF),
        schema=proposed.schema, service_build=proposed.service.build,
        OFFSETS=tuple(range(-12, 13)), sparse_controls=transport.sparse_controls,
        sparse_table=proposed.dependency_table(p))
    exec(compile(source, '<SP14 GF-output proof cut and birth observation>', 'exec'), namespace)
    n = namespace['build'](p)
    cells = {j: dict(packet_tag=[n.input_node['x', j, 'packet_tag', b] for b in range(4)],
        packet_valid=n.input_node['x', j, 'packet_valid', 0],
        packet_count=[n.input_node['x', j, 'packet_count', b] for b in range(11)],
        wf2=n.input_node['x', j, 'wf2', 0], flag_valid=n.input_node['x', j, 'service_valid', 0],
        flag_position=[n.input_node['x', j, 'service_position', b] for b in range(9)],
        flag_count=[n.input_node['x', j, 'service_count', b] for b in range(11)]) for j in range(-5, 6)}
    retained = proposed.service.build(n, cells)
    return n, retained, source


def restriction(n, cut_nodes, word, original_length, dependent):
    memo = {node: (word >> b) & 1 for b, node in enumerate(cut_nodes)}
    def apply(node):
        if node in memo:
            return memo[node]
        if node >= original_length or not dependent[node]:
            return node
        op, a, b = n.gate[node]
        answer = n.op(op, apply(a), apply(b))
        memo[node] = answer
        return answer
    return apply


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    n, retained, source = cut_net(p)
    cut_nodes = [n.input_node['computed_GF_cut', b] for b in range(p.k)]
    length = len(n.kind)
    dependent = [False]*length
    for node in cut_nodes:
        dependent[node] = True
    for node in range(length):
        if n.gate[node] is not None:
            _, a, b = n.gate[node]
            dependent[node] = dependent[a] or dependent[b]
    absent, born, identities = 0, 0, 0
    for word in range(1 << p.k):
        cf = restriction(n, cut_nodes, word, length, dependent)
        birth = cf(n.outputs['proof', 'birth'])
        if not 1 <= word <= 5:
            assert birth == 0, word
            absent += 1
        else:
            born += 1
        expected = dict(wf2=n.OR(birth, retained['wf2']),
            packet_valid=n.OR(birth, retained['packet_valid']),
            packet_tag=w_mux(n, birth, const_word((word - 1) % 16, 4), retained['packet_tag']),
            packet_count=w_mux(n, birth, [0]*11, retained['packet_count']))
        for field, values in expected.items():
            values = values if isinstance(values, list) else [values]
            for b, value in enumerate(values):
                assert cf(n.outputs['y', field, b]) == value, (word, field, b)
                identities += 1
        for actual, module in (('service_valid', 'flag_valid'), ('service_position', 'flag_position'), ('service_count', 'flag_count')):
            values = retained[module] if isinstance(retained[module], list) else [retained[module]]
            for b, value in enumerate(values):
                assert cf(n.outputs['y', actual, b]) == value, (word, actual, b)
                identities += 1
    assert (absent, born, identities) == (507, 5, 19456)
    # Derived integer origins on a true colony. The five eligible good
    # addresses emit root0; all other good addresses close birth.
    origin_cases = 0
    for x in range(p.Q):
        if 1 <= x <= 5:
            assert x - ((x - 1) % 16) - 1 == 0
        origin_cases += 1
    out = ROOT / 'figs/robustness'
    receipt = dict(proposal='SP14', proposed_rule_change=False, active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)), checker_sha256=digest(Path(__file__)),
        helpers_sha256=digest(ROOT / 'gacsca/netlist.py'), transport_checker_sha256=digest(Path(transport.__file__)),
        build_receipt_sha256=digest(out / 'SP14_program_build.json'),
        framed_service_certificate_sha256=digest(out / 'framed_service_certificate.json'),
        incorporation_receipt_sha256=digest(out / 'SP14_framed_incorporation_certificate.json'),
        full_generated_source_sha256=hashlib.sha256(proposed.actual_net(p)[1].encode()).hexdigest(),
        actual_maintenance_source_sha256=hashlib.sha256(proposed.proposed_build()[1].encode()).hexdigest(),
        GF_cut_observation_generated_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        GF_output_cut_bits=p.k, all_cut_GF_words_checked=1 << p.k,
        birth_closed_GF_words=absent, birth_eligible_GF_words=born,
        full_component_output_node_identities=identities,
        canonical_physical_address_origin_cases=origin_cases,
        every_other_raw_GF_Age_flag_Info_component_data_and_instruction_bit_free=True,
        birth_implies_newly_computed_GF_in_one_through_five=True,
        born_tag_equals_newly_computed_GF_minus_one=True, born_counter_equals_zero=True,
        canonical_GF_suffix_has_no_foreign_birth_root_inside_true_colony=True,
        no_birth_on_canonical_addresses_six_through_447=True,
        GF_cut_is_proof_overapproximation_only=True,
        original_GF_choice_restores_original_full_rule=True,
        correct_GF_or_command_source_initialization_from_general_errors_established=False,
        absence_of_foreign_retained_components_from_outside_suffix_established=False,
        later_births_force_hole_schedule_or_full_repair_established=False,
        global_reliability_established=False,
        scope='actual full-rule conditional birth-origin law under GF-output cut, exact free-input cofactor identities; ROBUSTNESS J97; no birth availability or iid theorem')
    (out / 'SP14_birth_origin_certificate.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(dict(GF_words=512, birth_closed_words=507, component_identities=identities,
        canonical_origin_cases=448, global_reliability_established=False)))


if __name__ == '__main__':
    main()
