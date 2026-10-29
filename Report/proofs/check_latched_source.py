#!/usr/bin/env python3
"""Exact SP6 command-frame cancellation and SP7 source retention.

All proofs are conditional one-update identities. No eroder or iid theorem.
"""
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca import rule_g
from gacsca.netlist import Net,Compiled,const_word,w_in_range
import proposed_sparse_relay448 as sp6
import proposed_sparse_latched448 as sp7
import check_fast_mail_proposal as transport
from check_shifted_halfline import dominant_bit


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bounded(proposed,kind):
    p = proposed.parameters()
    maintenance,_ = proposed.proposed_build(symbolic=True)
    _,source = proposed.actual_net(p)
    class BoundNet(Net):
        def input(self,key):
            if key[0] == 'x':
                _,offset,field,bit = key
                if kind == 'retain':
                    if field == 'age':
                        return super().input(('common_clock',bit))
                    if field == 'wf2' and offset == 0:
                        return 1
                else:
                    position = 4+offset
                    if field == 'addr':
                        address = (position-1)%p.Q if offset <= 0 else position%p.Q
                        return (address >> bit)&1
                    if field == 'age':
                        return (p.age_code(25710)>>bit)&1
                    if field in ('f1','f2','wf2'):
                        return 1
                    if field == 'wf1':
                        return 0
                    if field == 'info':
                        return int(position+bit-2 == 4)
            return super().input(key)
    namespace = dict(rule_g.__dict__,Net=BoundNet,maj5=dominant_bit,
                     maintenance=SimpleNamespace(build=maintenance),OFFSETS=tuple(range(-12,13)),
                     sparse_controls=transport.sparse_controls,sparse_table=proposed.dependency_table(p))
    exec(compile(source,'<latched source local identity>', 'exec'),namespace)
    return namespace['build'](p),p


def main():
    out = ROOT/'figs/robustness'
    rows = {}
    for proposed in (sp6,sp7):
        candidate = proposed.load_artifact()
        net,p = bounded(proposed,'wipe')
        assert [net.outputs['y','addr',bit] for bit in range(p.k)] == const_word(4,p.k)
        assert [net.outputs['y','age',bit] for bit in range(p.m)] == const_word(p.age_code(25711),p.m)
        assert net.outputs['y','f1',0] == net.outputs['y','f2',0] == 1
        assert net.outputs['y','wf1',0] == 0
        wf2 = 0 if proposed is sp6 else 1
        assert net.outputs['y','wf2',0] == wf2
        copied = [(field,bit) for field,bit in candidate.rows if field not in ('addr','age','f1','f2','wf1','wf2')]
        assert len(copied) == 229 and all(net.outputs['y',field,bit] == 0 for field,bit in copied)
        prefix = proposed.identity(p)['proposal']
        rows[prefix] = dict(proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
                            proposal_source_sha256=digest(Path(proposed.__file__)),
                            actual_generated_source_sha256=hashlib.sha256(proposed.actual_net(p)[1].encode()).hexdigest(),
                            computed_Address=4,computed_Age=p.age_code(25711),computed_Flag1=1,computed_Flag2=1,
                            computed_Workspace_Flag2=wf2,wiped_simulation_output_identities=229)
    net,p = bounded(sp7,'retain')
    common = [net.input_node['common_clock',bit] for bit in range(p.m)]
    expected = w_in_range(net,common,p.age_code(p.T_wf),p.age_code(p.T_wf+2*p.Q-1)+1)
    assert net.outputs['y','wf2',0] == expected
    result = dict(checker_sha256=digest(Path(__file__)),rules=rows,
                  transport_checker_sha256=digest(Path(transport.__file__)),
                  dominant_bit_helper_sha256=digest(ROOT/'Report/proofs/check_shifted_halfline.py'),
                  full_rule_sha256=digest(ROOT/'gacsca/rule_g.py'),
                  wipe_case_physical_holder=4,old_Address=3,old_coherent_command_primary=4,
                  new_signal_read_primary=3,new_signal_read_bit=0,
                  wipe_case_common_clock=25710,old_Workspace_Flag2=1,
                  SP7_retains_source_iff_actual_clock_gate_on=True,
                  retention_common_raw_clock_bits_free=p.m,
                  retention_all_raw_Address_flag_data_and_instruction_bits_free=True,
                  active_G17_modified=False,proposed_rule_changes=True,
                  damaged_trajectory_capture_provenance_established=False,
                  arbitrary_island_eroder_established=False,global_reliability_established=False,
                  scope='exact one-update command-frame cancellation/wipe witness and source-retention identity')
    (out/'SP6_SP7_source_latch_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(SP6_Workspace_Flag2=0,SP7_Workspace_Flag2=1,wiped_bits_per_rule=229,
                          retention_all_raw_clock_and_Address=True)))


if __name__ == '__main__':
    main()
