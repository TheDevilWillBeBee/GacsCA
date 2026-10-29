#!/usr/bin/env python3
"""SP8 scalar-source loss under four E0 erasures: conditional subsystem only.

This does not establish full-rule reachability of the initial shifted colony
or an iid failure. It tests the exact maintenance circuit and proves the
full-rule latch recurrence once all raw Info inputs are zero, with a common
active clock. This stronger cofactor avoids assuming an unwarranted copy frame.
"""
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca import rule_g
from gacsca.gray_errors import level0_points
from gacsca.netlist import Net, Compiled, mixed_age_increment, w_in_range
from check_fast_flag_proposal import invoke
from check_shifted_halfline import dominant_bit
import check_fast_mail_proposal as transport
import proposed_sparse_tail448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def recurrence():
    p = proposed.parameters()
    maintenance, _ = proposed.proposed_build(symbolic=True)
    _, source = proposed.actual_net(p)
    class BoundNet(Net):
        def input(self, key):
            if key[0] == 'x':
                _, offset, field, bit = key
                if field == 'age':
                    return super().input(('common_clock', bit))
                if field == 'info':
                    return 0
            return super().input(key)
    namespace = dict(rule_g.__dict__, Net=BoundNet, maj5=dominant_bit,
                     maintenance=SimpleNamespace(build=maintenance),
                     OFFSETS=tuple(range(-12, 13)),
                     sparse_controls=transport.sparse_controls,
                     sparse_table=proposed.dependency_table(p))
    exec(compile(source, '<SP8 zero-command latch identity>', 'exec'), namespace)
    net = namespace['build'](p)
    clock = [net.input_node['common_clock', bit] for bit in range(p.m)]
    gate = w_in_range(net, clock, p.age_code(p.T_wf),
                      p.age_code(p.T_wf + 5*p.Q//2 - 1) + 1)
    expected = net.AND(gate, net.input_node['x', 0, 'wf2', 0])
    assert net.outputs['y', 'wf2', 0] == expected
    return dict(common_raw_clock_bits_free=p.m, all_raw_Info_input_bits_zero=True,
                all_other_raw_input_bits_and_instructions_free=True,
                output_WF2_equals_gate_AND_own_raw_WF2=True)


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    build, source = proposed.proposed_build(symbolic=True)
    n = Net()
    clock = [n.input(('clock', bit)) for bit in range(p.m)]
    cells = {off: dict(addr=[n.input(('x', off, 'addr', bit)) for bit in range(p.k)],
                       age=clock, **{f:n.input(('x',off,f,0)) for f in ('f1','f2','wf1','wf2')})
             for off in range(-5,9)}
    result = invoke(build,n,cells,p)
    assert result['age_now'] == clock
    assert result['age'] == mixed_age_increment(n,clock,p.PB,p.R,p.nb)
    for bit,node in enumerate(result['addr']):
        n.set_output(('y','addr',bit),node)
    for f in ('f1','f2'):
        n.set_output(('y',f,0),result[f])
    comp = Compiled(n)
    live = set(n.live_nodes())
    assert all(key[1]<4 for key,node in n.input_node.items() if key[0]=='clock' and node in live)
    errors = {(1,400),(2,400),(3,425),(4,425)}
    assert level0_points(errors) == errors
    age_assignments = np.arange(16)
    coordinates = np.arange(p.Q)[None,:]+np.arange(-5,9)[:,None]
    inside = (coordinates>=0)&(coordinates<p.Q)
    clamped = np.clip(coordinates,0,p.Q-1)
    a = (np.arange(p.Q)-1)%p.Q
    f1 = np.arange(p.Q)>0
    f2 = np.zeros(p.Q,dtype=bool)
    wf2 = (np.arange(p.Q)>=1)&(np.arange(p.Q)<=5)
    states = []
    first_canonical = first_GF_F1_quiet = first_quiet = None
    for step in range(1401):
        for x,t in errors:
            if t==step:
                wf2[x] = False
        if step==1120:
            wf2[:] = False
        canonical = np.array_equal(a,np.arange(p.Q))
        if canonical and first_canonical is None:
            first_canonical = step
        if canonical and not f1.any() and first_GF_F1_quiet is None:
            first_GF_F1_quiet = step
        if canonical and not f1.any() and not f2.any() and first_quiet is None:
            first_quiet = step
        states.append(np.stack([a,f1.astype(np.int64),f2.astype(np.int64),wf2.astype(np.int64)]))
        if step==1400:
            break
        A = np.where(inside,a[clamped],np.where(coordinates<0,(coordinates-1)%p.Q,coordinates%p.Q))
        F1,F2,WF2 = inside&f1[clamped],inside&f2[clamped],inside&wf2[clamped]
        inputs = {}
        for key in comp.inputs:
            if key[0]=='clock':
                inputs[key] = np.repeat(((age_assignments>>key[1])&1).astype(bool),p.Q)
            else:
                _,off,f,bit = key
                index = off+5
                value = ((A[index]>>bit)&1).astype(bool) if f=='addr' else F1[index] if f=='f1' else F2[index] if f=='f2' else WF2[index] if f=='wf2' else np.zeros(p.Q,dtype=bool)
                inputs[key] = np.tile(value,16)
        y = comp.evaluate(inputs,bool)
        new_a = sum(y['y','addr',b].astype(np.int64)<<b for b in range(p.k)).reshape(16,p.Q)
        new_f1,new_f2 = y['y','f1',0].reshape(16,p.Q),y['y','f2',0].reshape(16,p.Q)
        assert np.all(new_a==new_a[:1]) and np.all(new_f1==new_f1[:1]) and np.all(new_f2==new_f2[:1]),step
        a,f1,f2 = new_a[0],new_f1[0],new_f2[0]
    assert first_canonical==369
    assert first_GF_F1_quiet is None and first_quiet is None
    assert np.array_equal(a,(np.arange(p.Q)-1)%p.Q)
    assert np.array_equal(f1,np.arange(p.Q)>0) and not f2.any()
    out = ROOT/'figs/robustness'
    asset = out/'SP8_source_erasure_trace.npz'
    np.savez_compressed(asset,states=np.stack(states),errors=np.array(sorted(errors)))
    receipt = dict(proposal='SP8',proposed_rule_change=True,active_G17_modified=False,
                   proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
                   proposal_source_sha256=digest(Path(proposed.__file__)),checker_sha256=digest(Path(__file__)),
                   local_correction_helper_sha256=digest(ROOT/'Report/proofs/check_fast_flag_proposal.py'),
                   dominant_bit_helper_sha256=digest(ROOT/'Report/proofs/check_shifted_halfline.py'),
                   transport_checker_sha256=digest(Path(transport.__file__)),
                   helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
                   error_classifier_sha256=digest(ROOT/'gacsca/gray_errors.py'),
                   actual_maintenance_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                   full_generated_source_sha256=hashlib.sha256(proposed.actual_net(p)[1].encode()).hexdigest(),
                   build_receipt_sha256=digest(out/'SP8_program_build.json'),tracking_asset_sha256=digest(asset),
                   Q=p.Q,errors=sorted(errors),all_four_errors_are_E0_relative_to_this_error_set=True,
                   whole_cell_replacements_preserve_every_bit_except_erased_WF2=True,
                   zero_command_recurrence=recurrence(),source_clock_gate_active_updates=1120,
                   initial_WF2_one_holders=[1,2,3,4,5],Workspace1_prescribed_zero=True,
                   all_raw_Info_input_bits_prescribed_zero_during_trace=True,
                   left_exterior_GF_phase=-1,right_exterior_GF_phase=0,exterior_flags_Workspace_zero=True,
                   common_raw_Age_bits_free=p.m,GF_flag_live_clock_bits=list(range(4)),
                   clock_assignments_per_update=16,checked_updates=1400,all_clock_assignments_identical=True,
                   first_all_canonical_step=first_canonical,
                   first_all_GF_and_Flag1_quiet_step=first_GF_F1_quiet,
                   first_all_GF_and_two_flags_quiet_step=first_quiet,
                   final_all_Address_phase_minus_one=True,final_Flag1_one_at_positive_holders=True,
                   initial_full_rule_reachability_established=False,
                   arbitrary_island_eroder_established=False,global_reliability_established=False,
                   scope='exact conditional subsystem counterexample to scalar-latch noise persistence, with full-rule zero-command recurrence; not an iid unreliability theorem')
    (out/'SP8_source_erasure_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(first_canonical=first_canonical,first_GF_F1_quiet=first_GF_F1_quiet,final_shifted=True,E0_errors=4)))


if __name__ == '__main__':
    main()
