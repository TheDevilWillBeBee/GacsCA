#!/usr/bin/env python3
"""Pin the premises/arithmetic of ROBUSTNESS J70's complete-encoding proof.

The proof reuses J29's copy induction and aligned E0 flag-retreat bounds;
this script checks identities and receipts, not every damaged trajectory.
No Bernoulli-noise reliability theorem is certified.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import proposed_sparse_liveness448 as sp5
import proposed_sparse_tail448 as sp8
import proposed_sparse_corrected_source448 as sp9


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = ROOT/'figs/robustness'
    baseline = sp5.proposed_build()[1]
    result = dict(checker_sha256=digest(Path(__file__)),active_G17_modified=False,
                  rules={},global_reliability_established=False,
                  scope='premise and reserve validation for complete-encoding E0-only theorem ROBUSTNESS J70; no general damaged-island or iid claim')
    for module,source_length in ((sp8,1120),(sp9,1792)):
        candidate = module.load_artifact()
        p = candidate.p
        prefix = module.identity(p)['proposal']
        assert module.proposed_build()[1] == baseline
        # J24/J26's conservative rescaled aligned-geometry bounds include
        # their reset allowance. The boundary start times below already
        # have zero computed Workspace, so retaining that allowance is safe.
        f1_reserve,f2_reserve = 252,247
        t1,t2 = f1_reserve-1,f2_reserve-1
        assert 2*t1-2*((t1+8)//9)>=p.Q-2
        assert 1+2*t2-2*((t2+10)//11)>=p.Q-1
        source1_free = p.T_wf+2*p.Q+1
        source2_free = p.T_wf+source_length+1
        f1_quiet = source1_free+f1_reserve
        flags_quiet = max(f1_quiet,source2_free)+f2_reserve
        assert flags_quiet == (26741 if prefix=='SP8' else 27385)
        assert flags_quiet < p.U-1
        deps = {key:digest(out/name) for key,name in (
            ('build_receipt_sha256',prefix+'_program_build.json'),
            ('schedule_receipt_sha256',prefix+'_symbolic_schedule.json'),
            ('front_receipt_sha256',prefix+'_front_certificate.json'),
            ('clean_closure_receipt_sha256',prefix+'_encoded_closure_certificate.json'),
            ('SP5_maintenance_receipt_sha256','SP5_maintenance_certificate.json'),
            ('SP4_maintenance_receipt_sha256','SP4_maintenance_certificate.json'),
            ('SP3_E0_prefix_receipt_sha256','SP3_E0_prefix_certificate.json'))}
        if prefix=='SP9':
            deps['corrected_source_receipt_sha256'] = digest(out/'SP9_corrected_source_certificate.json')
        result['rules'][prefix] = dict(proposed_rule_change=True,active_G17_modified=False,
             proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
             proposal_source_sha256=digest(Path(module.__file__)),
             actual_maintenance_source_sha256=hashlib.sha256(baseline.encode()).hexdigest(),
             full_generated_source_sha256=hashlib.sha256(module.actual_net(p)[1].encode()).hexdigest(),
             Q=p.Q,U=p.U,**deps,Flag1_E0_reserve=f1_reserve,Flag2_E0_reserve=f2_reserve,
             Workspace1_source_free_clock=source1_free,Workspace2_source_free_clock=source2_free,
             Flag1_quiet_by_clock=f1_quiet,all_four_computed_flags_quiet_by_clock=flags_quiet,
             complete_initial_encoding_with_N0_punctures_required=True,
             globally_24_24_separated_singleton_or_adjacent_pair_E0_groups_required=True,
             boundary_full_word_identity_outside_current_overwrites=True,
             decoded_boundary_identity_for_every_period=True,
             arbitrary_initial_Physical_GF_islands_covered=False,
             global_reliability_established=False,proof='ROBUSTNESS J70')
    (out/'SP8_SP9_encoded_e0_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({prefix:row['all_four_computed_flags_quiet_by_clock'] for prefix,row in result['rules'].items()}))


if __name__ == '__main__':
    main()
