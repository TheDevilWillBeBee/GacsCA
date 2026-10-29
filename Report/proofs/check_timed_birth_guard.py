#!/usr/bin/env python3
"""Actual SP13 retention when any protected three-word cohort exists.

Every GF/Age/command/other input is free. The six centers cover every
possible birth position on binary-phase GF; no general damaged-GF birth
or full-field repair assertion is made.
"""
from itertools import combinations
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca import rule_g
from gacsca.netlist import Net
import check_fast_mail_proposal as transport
import proposed_sparse_timed448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def case(p,x,holders):
    _,source = proposed.actual_net(p)
    class BoundNet(Net):
        def input(self,key):
            if key[0]=='x':
                _,off,field,bit = key
                y = x+off
                if y in holders:
                    if field in ('wf2','packet_valid'):return 1
                    if field=='packet_tag':return ((y-1)>>bit)&1
                    if field=='packet_count':return super().input(('common_packet_count',bit))
            return super().input(key)
    namespace = dict(rule_g.__dict__,Net=BoundNet,
        maintenance=SimpleNamespace(build=proposed.proposed_build()[0]),schema=proposed.schema,
        packet_build=proposed.timed_build_with_witness()[0],OFFSETS=tuple(range(-12,13)),
        sparse_controls=transport.sparse_controls,sparse_table=proposed.dependency_table(p))
    exec(compile(source,'<SP13 birth guard with all GF Age Info free>','exec'),namespace)
    n = namespace['build'](p)
    cells = {j:dict(tag=[n.input(('x',j,'packet_tag',b)) for b in range(4)],
                    count=[n.input(('x',j,'packet_count',b)) for b in range(11)],
                    valid=n.input(('x',j,'packet_valid',0)),wf2=n.input(('x',j,'wf2',0)))
             for j in range(-5,6)}
    exposed = proposed.timed_build_with_witness()[0](n,cells)
    assert exposed['cohort_exists']==1,(x,holders,'cohort')
    expected = proposed.packet.build(n,cells)
    assert n.outputs['y','wf2',0] == expected['wf2']
    assert n.outputs['y','packet_valid',0] == expected['valid']
    assert [n.outputs['y','packet_tag',b] for b in range(4)] == expected['tag']
    assert [n.outputs['y','packet_count',b] for b in range(11)] == expected['count']


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    cases = 0
    for x in range(1,7):
        for holders in combinations(range(1,6),3):
            case(p,x,holders)
            cases += 1
    out = ROOT/'figs/robustness'
    receipt = dict(proposal='SP13',proposed_rule_change=True,active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)),checker_sha256=digest(Path(__file__)),
        build_receipt_sha256=digest(out/'SP13_program_build.json'),
        full_generated_source_sha256=hashlib.sha256(proposed.actual_net(p)[1].encode()).hexdigest(),
        actual_maintenance_source_sha256=hashlib.sha256(proposed.proposed_build()[1].encode()).hexdigest(),
        timed_packet_proposal_source_sha256=digest(ROOT/'Report/proofs/proposed_timed_cohort_packet.py'),
        timed_packet_generated_source_sha256=hashlib.sha256(proposed.timed_build_with_witness()[1].encode()).hexdigest(),
        timed_packet_certificate_sha256=digest(out/'timed_cohort_packet_certificate.json'),
        retention_receipt_sha256=digest(out/'SP13_packet_retention_certificate.json'),
        protected_three_word_cohort_cases=cases,common_counter_bits_free=11,
        candidate_birth_centers_in_binary_phase_GF=list(range(1,7)),
        every_other_GF_Age_Info_packet_work_data_and_instruction_bit_free=True,
        actual_packet_equals_retention_with_all_commands_free=True,
        inactive_output_frame_still_suppresses_birth=True,
        arbitrary_GF_birth_locations_or_source_initialization_established=False,
        global_reliability_established=False,
        scope='universal full-rule birth suppression under a three-word packet witness; ROBUSTNESS J85')
    (out/'SP13_birth_guard_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(full_rule_cofactor_cases=cases,packet_bits_per_case=17,all_passed=True)))


if __name__=='__main__':
    main()
