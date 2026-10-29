#!/usr/bin/env python3
"""Universal own-ROM certificate for GR1's separate physical windows.

The inherited abstract machine replay starts with undefined registers and
scratch, so final replay depends on no early evaluator residue. Physical
register/pending routing, native controls and programme fetching remain
explicit hypotheses. The Workspace current-SimBit change is not hidden.
"""
from pathlib import Path
import hashlib,inspect,json,sys
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT)); sys.path.insert(0,str(ROOT/'Report/proofs'))
import check_g17_schedule as inherited
import gray_staged_rule as proposed
import gray_staged_transport as staged


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    out=ROOT/'figs/gray_counterexamples'
    build=json.loads((out/'GR1_program_build.json').read_text())
    assert build['build_complete']
    assert build['proposal_sha256']==digest(proposed.__file__)
    assert build['asset_sha256']==digest(out/'GR1_program.npz')
    assert build['listing_sha256']==digest(out/'GR1_program_listing.json')
    candidate=proposed.load_artifact(); assert candidate.digest()==build['candidate_sha256']
    listing=json.loads((out/'GR1_program_listing.json').read_text())
    source=inspect.getsource(inherited.main)
    capture_start=source.index('    capture_checks = 0\n')
    capture_end=source.index('    rom = np.zeros_like(c.rom)\n',capture_start)
    adapted='''    capture_checks = 0
    for gather in range(3):
        for lane, (offset, skew) in enumerate(zip(staged.LANES, staged.SKEW)):
            capture = staged.capture_age(gather, lane)
            distance = capture - p.gathers_q[gather] * p.Q - 2
            if offset:
                displacement = -distance if offset < 0 else distance
                require(skew + displacement == offset * p.Q, "staged gather address")
            else:
                require(capture == p.gathers_q[gather] * p.Q + 1, "own snapshot")
            require(capture < (p.gathers_q[gather] + 16) * p.Q, "gather active deadline")
            capture_checks += 1
    _, left_load, right_load = p.courier_ticks()
    require(left_load + 1 + lo - 3 == p.T_sig, "left courier arrival")
    require(right_load + 1 + p.Q - 3 - (hi - 1) == p.T_sig, "right courier arrival")
    require(proposed.EARLY_START + (p.NPe - 1) * period < min(left_load, right_load),
            "early flag deadline precedes couriers")
    require(p.T_sig < 80 * p.Q, "flag delivery before third active end")
    require(proposed.FINAL_START > 112 * p.Q + 1, "final follows stored temporal vote")
    require(proposed.FINAL_START + p.NP * period < 120 * p.Q,
            "final completes before fifth active end")
'''
    source=source[:capture_start]+adapted+source[capture_end:]
    replacements={
        'c = candidates.load("G17")':'c = proposed.load_artifact()',
        '''    require(c.digest() == "23a14aab4d3dc4fde5562cf3e26a4536b05456f84e65850fcb3bd95a104d8ceb",
            "G17 identity changed: re-audit before changing this verifier")''':
        '    require(c.digest() == build["candidate_sha256"], "GR1 candidate identity")',
        '''    eng = jobsched.Engine(p, comp, c.layout, MP=p.MP,
                          **candidates.RECIPES["G17"]["compile"]["jobs"])
    eng.run()''':'    eng = SimpleNamespace(prog=SimpleNamespace(listing=listing))',
        'candidate="G17"':'candidate="GR1"',
        'flag_stores[cell] = p.E0 + clock':'flag_stores[cell] = proposed.EARLY_START + clock',
        'early_flag_deadline_age=p.E0 + (p.NPe - 1) * period':
        'early_flag_deadline_age=proposed.EARLY_START + (p.NPe - 1) * period',
        'evaluation_end_age=p.E0 + p.NP * period':
        'evaluation_end_age=proposed.FINAL_START + p.NP * period',
        'ROOT / "figs/robustness/symbolic_schedule.json"':
        'ROOT / "figs/gray_counterexamples/GR1_symbolic_schedule.json"',
    }
    for old,new in replacements.items():
        assert source.count(old)==1,old
        source=source.replace(old,new)
    namespace=dict(inherited.__dict__)
    namespace.update(ROOT=ROOT,__file__=__file__,proposed=proposed,staged=staged,
        listing=listing,build=build,SimpleNamespace=SimpleNamespace)
    exec(compile(source,'<GR1 universal own-schedule checker>','exec'),namespace)
    namespace['main']()
    path=out/'GR1_symbolic_schedule.json'; r=json.loads(path.read_text())
    assert r['counts']['instructions']==27571
    assert r['key_equalities']==23 and r['final_hold_equalities']==386
    assert r['early_flag_equalities']==2
    # All early stores are checked before the prefix stops, and full replay
    # starts anew with every register/scratch term undefined. Matching input
    # snapshot values in the early and final windows are separate premises.
    r.update(proposal_sha256=digest(proposed.__file__),transport_primitive_sha256=digest(staged.__file__),
        build_receipt_sha256=digest(out/'GR1_program_build.json'),
        inherited_checker_sha256=digest(inherited.__file__),
        generated_checker_sha256=hashlib.sha256(source.encode()).hexdigest(),
        own_programme_verified=True,early_prefix_verified=True,
        final_abstract_replay_requires_no_early_registers_or_scratch=True,
        early_input_premise='Majority of the three separately retained gathers supplies each compiler input during the early flag prefix.',
        final_input_premise='The stored voted bank supplies the same compiler inputs during the fresh full fifth-stage replay.',
        explicit_healthy_flag2_repair_h=1,explicit_current_corrected_SimBit_Workspace_change=True,
        gray_verbatim_simulation=False,physical_self_simulation_proved=False,
        full_physical_E0_lift_proved=False,global_reliability_established=False)
    path.write_text(json.dumps(r,indent=2)+'\n')


if __name__=='__main__':
    main()
