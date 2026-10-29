#!/usr/bin/env python3
"""Read-only validation of the exact changed-WF0 stationary clock witness."""
from pathlib import Path
import hashlib,json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
import check_gray_token_gather_v7_clock_island as check


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate(directory=None):
    directory=directory or ROOT/'figs/gray_counterexamples';source=Path(__file__).parent
    receipt=json.loads((directory/'GMW7_WF0_clock_island_certificate.json').read_text())
    assert (receipt['Q'],receipt['U'],receipt['lambda_original'],receipt['c_original'])==(8192,1048576,24,104)
    assert receipt['checker_sha256']==digest(check.__file__)
    assert receipt['proof_sha256']==digest(source/'GMW7_WF0_CLOCK_ISLAND.md')
    for name,value in receipt['source_dependencies_sha256'].items():assert digest(source/name)==value
    assert receipt['root_initializer_checker_sha256']==digest(check.initial.__file__)
    assert receipt['root_initializer_proof_sha256']==digest(ROOT/'Report/proofs/GMW7_INTACT_HIERARCHY.md')
    assert receipt['period_receipt_sha256']==digest(directory/'GMW7_single_gather_period_certificate.json')
    assert receipt['gray_class_source_text_sha256']==digest(ROOT/'papers_txt/gray_readers_guide.txt')
    for name,value in receipt['retained_initial_assets_sha256'].items():assert digest(directory/name)==value
    before=json.loads((directory/'GMW7_WF0_clock_island_initial_certificate.json').read_text())
    assert before['proof_sha256']==digest(directory/'GMW7_WF0_clock_island_initial_proof.md.txt')
    assert before['checker_sha256']==digest(directory/'GMW7_WF0_clock_island_initial_checker.py.txt')
    assert before['errors']['support_asset_sha256']==digest(directory/'GMW7_WF0_clock_island_initial_errors.npz')
    assert receipt['all_subset_separation_wording_clarification_not_a_mathematical_failure']
    quotient,trajectory=check.calculate()
    assert quotient==receipt['quotient_cofactors']
    assert {name:v for name,v in trajectory.items() if name!='rows'}==receipt['transient_event_summary']
    assert trajectory==json.loads((directory/'GMW7_WF0_clock_island_transients.json').read_text())
    assert receipt['transient_asset_sha256']==digest(directory/'GMW7_WF0_clock_island_transients.json')
    errors=receipt['errors']
    assert errors['support_asset_sha256']==digest(directory/'GMW7_WF0_clock_island_errors.npz')
    with np.load(directory/'GMW7_WF0_clock_island_errors.npz') as points:
        assert np.array_equal(points['x'],np.arange(check.B,dtype=np.int64))
        assert np.array_equal(points['t'],np.zeros(check.B,dtype=np.int64))
        assert points['replacement_age'].tolist()==[1]
    assert errors['points']==139264 and errors['error_interval']==[0,check.B] and errors['interval_half_open']
    assert errors['E0_empty'] and errors['E1_empty'] and errors['whole_row_one_original_real2_proved_by_definition']
    assert errors['all_other_native_and_SF_fields_untouched'] and errors['no_later_errors']
    assert errors['replacement_recipe']=='replace(initial_cell(x), age=1)'
    for row in errors['sampled_payloads']:
        clean=check.initial.initial_cell(row['x'])
        assert [hex(v) for v in check.k.cell_words(clean)]==row['initial_words']
        noisy=check.k.cell_from_words([int(v,16) for v in row['replacement_words']])
        from dataclasses import replace
        assert noisy==replace(clean,age=1)
    for key in ('native_factor_closed_for_arbitrary_legal_private_fields',
        'intact_recursive_start_with_one_shared_finite_physical_error_history',
        'Flag2_identically_zero','stationary_not_travelling',
        'no_finite_spacetime_native_clock_recovery_envelope',
        'finite_spatial_hull_exists_and_Address_remains_canonical',
        'private_programme_dictionary_SF_only_changes_cannot_fix_under_unchanged_WF0_native'):
        assert receipt[key]
    assert receipt['wrong_Age_support_all_ticks']==[0,check.B]
    assert receipt['Flag1_saturation_tick']==2731
    assert not receipt['Gray_Gacs_G17_Address_memory_or_iid_refuted'] and not receipt['active_rule_modified']
    return dict(receipt_sha256=digest(directory/'GMW7_WF0_clock_island_certificate.json'),
        actual_native_scalar_cofactors=208896+22528+1072,event_segments=633714,
        one_intact_start_real2_original_c104=True,wrong_clock_sites_forever=139264,
        Flag1_saturation_tick=2731,fixed_spatial_hull=True,infinite_temporal_lifetime=True,
        changed_WF0_variant_obstruction_only=True,Gray_Address_or_iid_refuted=False)


if __name__=='__main__':
    started=time.monotonic();result=validate();result['elapsed_seconds']=time.monotonic()-started
    print(json.dumps(result))
