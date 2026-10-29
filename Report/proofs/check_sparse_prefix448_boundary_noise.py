#!/usr/bin/env python3
"""Literal fresh-boundary decoder counterexample to the former raw J36 map.

No trajectory experiment or reliability claim. The fresh overwrite changes
the raw decoder at time U; the proposed core map assigned only time2U.
The pristine boundary is supplied by the proved encoded-simulation lemma.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca import codec
import proposed_sparse_prefix448 as proposed
from check_sparse_prefix448_physical import augmented


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    out = ROOT / 'figs/robustness'
    candidate = proposed.load_artifact()
    p = candidate.p
    top = np.zeros((candidate.W, 1), dtype=np.uint8)
    z0 = augmented(candidate, top)
    z1 = candidate.step_numpy(z0)
    j = p.Q//2
    bit_address = int(candidate.layout[candidate.row['addr', 0]])
    assert bit_address == 59
    start = j*p.Q+bit_address-2
    sites = np.arange(start, start+16)
    before = augmented(candidate, z1)
    assert np.array_equal(codec.decode(candidate, before), z1)
    after = before.copy()
    replacements = np.ones((candidate.W, 16), dtype=np.uint8)
    after[:, sites] = replacements
    decoded = codec.decode(candidate, after)
    changed = np.flatnonzero(np.any(decoded != z1, axis=0))
    assert changed.tolist() == [j]
    old_addr, new_addr = int(candidate.field(z1, 'addr')[j]), int(candidate.field(decoded, 'addr')[j])
    assert old_addr == j and new_addr == 511
    assert (old_addr & 1) == 0 and (new_addr & 1) == 1
    tau = p.U
    closest_right = start+1
    anchor = (closest_right+15)//p.Q-1
    assert j in (anchor, anchor+1)
    former_tick = tau//p.U+1
    assert former_tick == 2 and tau//p.U == 1
    assert np.array_equal(candidate.step_numpy(decoded), candidate.step_numpy(z1))
    asset = out / 'SP4_boundary_noise_inputs.npz'
    np.savez_compressed(asset, top=top, clean_upper=z1, raw_decoder=decoded,
                        overwrite_sites=sites, replacements=replacements,
                        relative_real_level1_points=np.array([(x,t) for x in range(16) for t in range(16)], dtype=np.int32))
    receipt = dict(
        proposal='SP4', proposed_rule_change=True, active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)), checker_sha256=digest(Path(__file__)),
        augmented_helper_sha256=digest(ROOT / 'Report/proofs/check_sparse_prefix448_physical.py'),
        build_receipt_sha256=digest(out / 'SP4_program_build.json'), input_asset_sha256=digest(asset),
        first_core_tick=tau, assigned_former_upper_error_tick=former_tick,
        actual_raw_decoder_changed_upper_tick=1, computed_decoder_clean_upper_tick=1,
        changed_upper_cells=changed.tolist(), old_Address=old_addr, new_Address=new_addr,
        relative_error_set=dict(width=16, duration=16, points=256, real_level1=True, level0=0,
                                classification='diameters below16; dense connected rectangle; no isolated E0 group'),
        literal_upper_next_update_correct=True,
        former_raw_boundary_J36_formula_false=True,
        computed_before_fresh_noise_map_not_refuted=True,
        scope='literal codec counterexample using a proved clean boundary; no CA trajectory experiment or iid conclusion',
        global_reliability_established=False)
    (out / 'SP4_boundary_noise_certificate.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(dict(raw_decoder_error_tick=1, former_assigned_tick=2,
                          changed_upper_cells=changed.tolist(), old_Address=old_addr, new_Address=new_addr)), flush=True)


if __name__ == '__main__':
    main()
