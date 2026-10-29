#!/usr/bin/env python3
"""Exact local certificate: a one-cell pressure valve is not a barrier.

Correct GF/common active Age, empty packet/code fields, all other state
and I free. Prove the full native/component outputs and pressure recurrence.
The noise-free half-line consequence in ROBUSTNESS is not island failure.
"""
import hashlib,json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,Compiled,const_word,at_least
import proposed_sparse_backward_fitted448 as proposed

COMPONENTS=('wf2','packet_valid','packet_tag','packet_count',
            'service_valid','service_position','service_count')


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def case(p,address):
    clock=p.T_wf+449
    class BoundNet(Net):
        def input(self,key):
            if key[0]=='x':
                _,off,field,bit=key
                if field=='addr': return (((address+off)%p.Q)>>bit)&1
                if field=='age': return (p.age_code(clock)>>bit)&1
                if field in COMPONENTS: return 0
            return super().input(key)
    n,_=proposed.full_net(p,net_class=BoundNet)
    expected=0 if address==p.Q-1 else at_least(n,[n.input(('x',j,'backward_pressure',0)) for j in range(1,6)],3)
    assert n.outputs['y','backward_pressure',0]==expected,address
    for f,w,v in (('addr',p.k,address),('age',p.m,p.age_code(clock+1))):
        assert [n.outputs['y',f,b] for b in range(w)]==const_word(v,w),(address,f)
    zeros=0
    for field,width in proposed.schema(p):
        if field in COMPONENTS:
            assert all(n.outputs['y',field,b]==0 for b in range(width)),(address,field)
            zeros+=width
    assert zeros==38
    if address==p.Q-2:
        # Its right neighbor is the valve; the other four are pressure1.
        assignments={j:int((address+j)%p.Q!=p.Q-1) for j in range(1,6)}
        assert sum(assignments.values())==4
    return zeros


def main():
    p=proposed.parameters(); candidate=proposed.load_artifact()
    assert Compiled(proposed.full_net(p)[0]).digest==candidate.comp.digest
    for address in range(p.Q):
        case(p,address)
    # Arithmetic of the support stencil at every possible colony phase.
    checks=0
    for front in range(p.Q):
        for x in (front-2,front-1,front,front+1,front+2,front+3):
            if x%p.Q!=p.Q-1:
                ones=sum(y>=front and y%p.Q!=p.Q-1 for y in range(x+1,x+6))
                assert ones>=3,(front,x,ones)
                checks+=1
    out=ROOT/'figs/robustness'
    receipt=dict(proposal='SP22',proposed_rule_change=False,active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        checker_sha256=digest(Path(__file__)),proposal_source_sha256=digest(Path(proposed.__file__)),
        local_module_source_sha256=digest(Path(proposed.local.__file__)),helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
        native_receipt_sha256=digest(out/'SP22_backward_native_certificate.json'),
        incorporation_receipt_sha256=digest(out/'SP22_incorporation_encoded_certificate.json'),
        Q=p.Q,U=p.U,width=candidate.W,clock=p.T_wf+449,
        full_rule_free_pressure_native_component_cofactors=448,
        component_zero_bits_per_cofactor=38,native_GF_Age_bits_per_cofactor=p.k+p.m,
        free_pressure_recurrence_output_identities=448,
        periodic_pressure_pattern_one_except_GF447_is_preserved_in_active_window=True,
        all_phase_two_cell_covered_ray_support_checks=checks,
        minimum_noise_free_pressure_ray_advance_per_update=2,
        halfline_active_updates=1792,halfline_covered_nonvalve_extent_after_window=3584,
        packets_and_codes_empty_and_GF_Age_correct_required=True,
        arbitrary_flags_workspace_Info_and_instruction_allowed=True,
        later_noise_allowed=False,finite_error_island_or_pristine_hierarchy_counterexample=False,
        GF_Age_damage_or_iid_failure_established=False,global_reliability_established=False,
        scope='ROBUSTNESS J123: pressure-majority can cross a one-cell zero valve; exact noise-free recurrence under canonical native/empty-component premises, no finite-island or iid failure')
    (out/'SP22_pressure_valve_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(full_cofactors=448,ray_checks=checks,valve_is_spatial_barrier=False,iid_failure=False)),flush=True)


if __name__=='__main__':
    main()
