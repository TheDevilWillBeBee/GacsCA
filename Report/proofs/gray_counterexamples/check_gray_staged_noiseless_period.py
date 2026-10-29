#!/usr/bin/env python3
"""Pin and check the constituents of the written GR1 noiseless-period proof.

The theorem is proved by the explicit composition argument in the owned
Markdown proof, not by exhaustively running U physical updates here.
There is no noisy, real1, literal-Gray or iid theorem in this receipt.
"""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
import numpy as np
import gray_staged_rule as proposed
import gray_staged_transport as staged


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    out=ROOT/'figs/gray_counterexamples'; source=ROOT/'Report/proofs/gray_counterexamples'
    names=('native_geometry_invariant_certificate.json','gray_staged_transport_certificate.json',
           'GR1_program_build.json','GR1_symbolic_schedule.json','GR1_fetch_certificate.json',
           'GR1_frame_certificate.json','GR1_flag_quiet_certificate.json')
    rows={name:json.loads((out/name).read_text()) for name in names}
    candidate=proposed.load_artifact(); p=candidate.p; comp=candidate.comp
    assert (p.Q,p.U,candidate.W)==(8192,1048576,386)
    assert rows[names[0]]['canonical_geometry_noiseless_invariant_proved']
    assert not rows[names[0]]['workspace_zero_required']
    assert rows[names[1]]['all_clock_address_route_classes_proved']
    assert rows[names[3]]['own_programme_verified']
    assert rows[names[3]]['final_abstract_replay_requires_no_early_registers_or_scratch']
    assert rows[names[4]]['correct_work_key_fetch_proved_conditionally']
    assert rows[names[4]]['outside_work_key_instruction_irrelevance_proved']
    assert rows[names[5]]['front_route']['nonmatch_front_route_proved_conditionally']
    assert rows[names[5]]['tracked_coupling']['coherent_pending_forwarding_and_selective_reset_coupling_proved']
    assert rows[names[6]]['all_colony_flags_noiseless_clearing_proved']
    assert rows[names[6]]['all_flags_quiet_by_age']==99*p.Q<112*p.Q
    assert len(set(candidate.layout.tolist()))==candidate.W
    assert np.all((candidate.layout>=p.lo)&(candidate.layout<p.hi))
    assert not set(candidate.layout.tolist())&set(proposed.reserved_cells(p))
    # Structural I-independence of native early flags and lookup keys.
    def dependencies(node):
        stack=[node]; seen=set(); result=set()
        reverse={index:name for name,index in comp.index.items()}
        while stack:
            node=stack.pop()
            if node in seen: continue
            seen.add(node)
            if node in reverse: result.add(reverse[node])
            elif node>=2+len(comp.inputs):
                _,a,b=comp.gates[node-2-len(comp.inputs)]; stack.extend((a,b))
        return result
    independent=[('y','f1',0),('y','f2',0)]+[
        ('laddr',b) for b in range(p.k)]+[('psel',b) for b in range(p.PW)]
    for name in independent:
        assert not any(x[0]=='I' for x in dependencies(comp.outputs[name])),name
    last_capture=max(staged.capture_age(g,lane) for g in range(3) for lane in range(11))
    assert last_capture<proposed.EARLY_START
    listing=json.loads((out/'GR1_program_listing.json').read_text())
    early_stores=[]; final_stores=[]
    for _,page,tick,front,cell,op,kind,a,b,dest,note in listing:
        assert page!=p.MP
        if kind in (1,2):
            final_stores.append(proposed.FINAL_START+page*p.PL+tick+1)
            if kind==1 and cell in proposed.flag_store_cells(p) and page<p.NPe:
                early_stores.append(proposed.EARLY_START+page*p.PL+tick+1)
    assert max(early_stores)<min(staged.LEFT_COURIER,staged.RIGHT_COURIER)
    assert max(final_stores)<120*p.Q
    assert proposed.FINAL_START>112*p.Q+1
    assert proposed.FINAL_START+p.NP*p.PL<120*p.Q
    # No required interpreter write encounters a stage-start clearing.
    stage_starts=[0,32*p.Q,64*p.Q,96*p.Q,112*p.Q]
    for lo,hi in ((proposed.EARLY_START,proposed.EARLY_START+p.NPe*p.PL),
                  (proposed.FINAL_START,proposed.FINAL_START+p.NP*p.PL)):
        assert not any(lo<=age<hi for age in stage_starts)
    # At the boundary all private tracked fields reset; Info consumes old
    # Hold before its reset. Hold then persists through the final rest.
    for f,w in staged.FIELDS:
        for slot in staged.SLOTS:
            for b in range(w):
                expected=('hold',slot,0) if f=='info' else ('zero',)
                assert staged.plan(0,4096,slot,f,b)==expected
    for age in staged.clock_boundaries():
        if 120*p.Q<=age<p.U:
            assert staged.plan(age,4096,0,'hold')==('hold',0,0)
        if 96*p.Q<age<p.U:
            for f in ('mr','ml'):
                assert staged.plan(age,4096,0,f) in (('zero',),(f,0,0))
    proof=source/'GR1_NOISELESS_PERIOD.md'
    result=dict(candidate='GR1',Q=p.Q,U=p.U,width=candidate.W,
        candidate_sha256=candidate.digest(),netlist_sha256=comp.digest,
        checker_sha256=digest(__file__),written_proof_sha256=digest(proof),
        proposal_sha256=digest(proposed.__file__),transport_primitive_sha256=digest(staged.__file__),
        receipt_dependencies_sha256={name:digest(out/name) for name in names},
        proof_kind='Written universal composition proof using the pinned exact local/coordinate and own-programme certificates; no physical trajectory sampling.',
        encoding_family='Canonical GF, common Age0, native/Workspace flags0; all private fields0; five coherent Info copies encode the386 upper bits at the layout; unrepresented coherent Info unrestricted.',
        theorem='For every bi-infinite upper configuration s and every c in E(s), noiseless F^U(c) is in E(F(s)). Hence decoder(F^(nU)(c))=F^n(s) for every n>=0.',
        noiseless_encoded_period_theorem_proved=True,
        continuing_noiseless_boundary_decoding_proved=True,
        upper_state_bits_symbolically_covered=candidate.W,
        early_flags_and_lookup_I_independent_outputs=len(independent),
        last_gather_computed_age=last_capture,
        last_early_pending_store_application_age=max(early_stores),
        last_final_pending_store_application_age=max(final_stores),
        native_flags_quiet_by_age=99*p.Q,
        auxiliary_represented_alias_assumed=False,
        explicit_healthy_flag2_repair_h=1,explicit_current_corrected_SimBit_Workspace_change=True,
        instruction_ROM_shape=list(candidate.rom.shape),instruction_word_bits=p.IW,
        logical_instruction_ROM_bits=int(candidate.rom.size)*p.IW,
        nonzero_instruction_words=int(np.count_nonzero(candidate.rom)),
        nonzero_instruction_payload_bits=int(np.count_nonzero(candidate.rom))*p.IW,
        gray_single_ProgramBit_per_Address_compilation_proved=False,
        full_rest_rule_on_arbitrary_damaged_raw_states_proved=False,
        gray_verbatim_simulation=False,full_physical_E0_lift_proved=False,
        real1_recovery_proved=False,iid_reliability_proved=False,global_reliability_established=False,
        active_rule_modified=False,measured_only=False)
    (out/'GR1_noiseless_period_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ('noiseless_encoded_period_theorem_proved',
        'continuing_noiseless_boundary_decoding_proved','last_gather_computed_age',
        'last_early_pending_store_application_age','last_final_pending_store_application_age',
        'native_flags_quiet_by_age','logical_instruction_ROM_bits','nonzero_instruction_payload_bits',
        'full_physical_E0_lift_proved')}))


if __name__=='__main__': main()
