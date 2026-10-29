#!/usr/bin/env python3
"""SP12 actual birth output cofactors on corrected canonical geometry.

Two arbitrary whole-cell inputs are allowed in the source's eleven-site
window. Good logical Info copies at target3 share a free command bit.
There is no old packet except these fault words. This is not birth from
arbitrary GF, command provenance or an iid repair certificate.
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
from check_shifted_halfline import dominant_bit
import check_fast_mail_proposal as transport
import proposed_sparse_cohort448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def case(p,address,faults):
    maintenance,_ = proposed.proposed_build(symbolic=True)
    _,source = proposed.actual_net(p)
    class BoundNet(Net):
        def input(self,key):
            if key[0]=='x':
                _,off,field,bit = key
                if off not in faults:
                    if field=='addr':return ((address+off)%p.Q>>bit)&1
                    if field=='age':return (p.age_code(p.T_wf)>>bit)&1
                    if field in ('wf2','packet_tag','packet_valid'):return 0
                    if field=='info' and (address+off+bit-2)%p.Q==3:
                        return super().input(('command',))
            return super().input(key)
    namespace = dict(rule_g.__dict__,Net=BoundNet,maj5=dominant_bit,
        maintenance=SimpleNamespace(build=maintenance),schema=proposed.schema,
        packet_build=proposed.packet.build,OFFSETS=tuple(range(-12,13)),
        sparse_controls=transport.sparse_controls,sparse_table=proposed.dependency_table(p))
    exec(compile(source,'<SP12 canonical two-fault birth cofactor>','exec'),namespace)
    n = namespace['build'](p)
    command = n.input(('command',))
    assert n.outputs['y','wf2',0] == command,(address,faults,'wf2')
    assert n.outputs['y','packet_valid',0] == command,(address,faults,'valid')
    for bit in range(4):
        expected = command if ((address-1)>>bit)&1 else 0
        assert n.outputs['y','packet_tag',bit] == expected,(address,faults,bit)


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    cases = 0
    for address in range(1,6):
        for faults in combinations(range(-5,6),2):
            case(p,address,faults)
            cases += 1
        print(json.dumps(dict(through_address=address,cofactor_cases=cases)),flush=True)
    out = ROOT/'figs/robustness'
    receipt = dict(proposal='SP12',proposed_rule_change=True,active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)),checker_sha256=digest(Path(__file__)),
        build_receipt_sha256=digest(out/'SP12_program_build.json'),
        packet_proposal_source_sha256=digest(ROOT/'Report/proofs/proposed_cohort_packet.py'),
        packet_certificate_sha256=digest(out/'cohort_packet_certificate.json'),
        modal_clock_proposal_source_sha256=digest(ROOT/'Report/proofs/proposed_modal_clock.py'),
        actual_maintenance_source_sha256=hashlib.sha256(proposed.proposed_build()[1].encode()).hexdigest(),
        full_generated_source_sha256=hashlib.sha256(proposed.actual_net(p)[1].encode()).hexdigest(),
        dominant_bit_helper_sha256=digest(ROOT/'Report/proofs/check_shifted_halfline.py'),
        transport_checker_sha256=digest(Path(transport.__file__)),
        canonical_source_holder_two_fault_cofactors=cases,common_command_bit_free=True,
        every_other_Info_flag_data_Workspace_and_instruction_input_free=True,
        good_raw_GF_and_clock_required=True,input_clock=p.T_wf,
        good_raw_packet_component_zero_required=True,
        birth_output_packet_holders=list(range(1,6)),birth_output_tags=list(range(5)),
        source_birth_on_arbitrary_GF_established=False,command_provenance_in_damaged_encodings_established=False,
        global_reliability_established=False,scope='actual full-circuit canonical five-holder birth cofactors; ROBUSTNESS J79')
    (out/'SP12_packet_birth_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(cofactor_cases=cases,all_equal=True)))


if __name__=='__main__':
    main()
