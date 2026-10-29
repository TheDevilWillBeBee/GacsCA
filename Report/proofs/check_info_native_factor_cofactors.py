#!/usr/bin/env python3
"""Selected full-net Info/native factor identities with other private bits free."""
from pathlib import Path
import hashlib
import json
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca.netlist import Compiled
from check_g17_schedule import Terms
import proposed_sparse_distant_epoch1024 as baseline
import proposed_sparse_short_epoch_duration as family


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    started = time.monotonic()
    out = ROOT / 'figs/robustness'
    p = baseline.parameters()
    N = 256 * p.Q
    cases = []
    pairs = ((0, 1), (1, 2), (1791, 1792), (1792, 1793), (1793, 1794), (2048, 2049))
    asset = out / 'SP28_info_factor_states.npz'
    with np.load(asset) as stored:
        for duration in (p.Q, 2 * p.Q):
            net, source = family.full_net(p, duration)
            comp = Compiled(net)
            for mode in (0, 1, 2):
                for offset, after in pairs:
                    prefix = f'SP28_info_factor_{duration}_mode{mode}'
                    key = f'{prefix}_initial_0' if offset == 0 else f'{prefix}_trace_{offset}'
                    old = stored[key + '_planes']
                    code = stored[key + '_code']
                    info = stored[key + '_info']
                    new = stored[f'{prefix}_trace_{after}_planes']
                    newcode = stored[f'{prefix}_trace_{after}_code']
                    edges = list(map(int, np.flatnonzero(old[0] != np.roll(old[0], 1))))
                    mid = int(np.flatnonzero(old[0])[len(np.flatnonzero(old[0])) // 2])
                    readers = sorted(set([x + d for x in edges for d in (-3, 0, 2)] +
                                         [(mid // p.Q) * p.Q + r for r in (509, 1021)] +
                                         [16 * p.Q + r for r in (509, 1021)]))
                    for site in readers:
                        terms = Terms()
                        nodes = [0, 1]
                        for name in comp.inputs:
                            if name[0] != 'x':
                                value = terms.var(name)
                            else:
                                _, off, field, bit = name
                                y = (site + off) % N
                                words = dict(addr=(y + 512 * int(old[0, y])) % p.Q,
                                    age=p.age_code(p.T_wf + offset), f1=int(old[1, y]),
                                    f2=int(old[2, y]), wf1=int(old[3, y]), wf2=int(old[4, y]),
                                    packet_valid=int(old[4, y]), packet_tag=int(old[5, y]),
                                    packet_count=offset - 1 if old[4, y] else 0,
                                    service_valid=int(old[6, y]), service_position=int(code[y]),
                                    service_count=offset - 1 if old[6, y] else 0,
                                    backward_pressure=int(old[7, y]))
                                if field == 'info' and (y + bit - 2) % p.Q in (509, 1021):
                                    value = int(info[(y + bit - 2) % N])
                                elif field in words:
                                    value = (words[field] >> bit) & 1
                                else:
                                    value = terms.var(name)
                            nodes.append(value)
                        for op, a, b in comp.gates:
                            nodes.append(terms.op(op, nodes[a], nodes[b]))
                        expected = dict(addr=(site + 512 * int(new[0, site])) % p.Q,
                            age=p.age_code(p.T_wf + after), f1=int(new[1, site]),
                            f2=int(new[2, site]), wf1=int(new[3, site]), wf2=int(new[4, site]),
                            packet_valid=int(new[4, site]), packet_tag=int(new[5, site]),
                            packet_count=offset if new[4, site] else 0,
                            service_valid=int(new[6, site]), service_position=int(newcode[site]),
                            service_count=offset if new[6, site] else 0,
                            backward_pressure=int(new[7, site]))
                        equalities = 0
                        for name, node in comp.outputs.items():
                            if len(name) != 3 or name[0] != 'y':
                                continue
                            _, field, bit = name
                            if field in expected:
                                wanted = (expected[field] >> bit) & 1
                            elif field == 'info' and (site + bit - 2) % p.Q in (509, 1021):
                                keep = not (new[1, site] and new[0, site] != old[0, site])
                                wanted = int(keep and info[(site + bit - 2) % N])
                            else:
                                continue
                            assert nodes[node] == wanted, (duration, mode, offset, site, name,
                                                           nodes[node], wanted)
                            equalities += 1
                        cases.append(dict(duration=duration, Info_mode=mode, offset=offset,
                                          site=site, constant_output_bit_equalities=equalities,
                                          other_private_and_instruction_bits_free=True,
                                          selected_tracked_Info_copies_coherent=True,
                                          netlist_sha256=comp.digest))
            print(json.dumps(dict(duration=duration, cumulative_cofactors=len(cases))), flush=True)
    result = dict(
        scope='Selected exact Info/native/header full-net cofactors; coherent tracked-Info representatives',
        Q=p.Q, U=p.U, T_wf=p.T_wf, exact_full_net_cofactors=len(cases),
        constant_output_bit_equalities=sum(c['constant_output_bit_equalities'] for c in cases),
        rows=cases, other_private_and_instruction_bits_free=True,
        finite_native_frames_not_an_all_raw_native_state_enumeration=True,
        universal_factor_proof_is_separate_written_vote_source_argument=True,
        all_period_eroder_or_intact_reachability_proved=False,
        global_reliability_established=False, active_G17_modified=False,
        original_SP28_modified=False, checker_sha256=digest(__file__),
        state_asset_sha256=digest(asset),
        baseline_source_sha256=digest(baseline.__file__),
        family_source_sha256=digest(family.__file__),
        terms_source_sha256=digest(ROOT / 'Report/proofs/check_g17_schedule.py'),
        netlist_library_sha256=digest(ROOT / 'gacsca/netlist.py'),
        C_source_sha256=digest(ROOT / 'Report/proofs/native_address_info_factor.c'),
        initial_output_shape_failure_sha256=digest(out / 'SP28_info_native_factor_cofactor_initial_output_shape_failure.json'),
        pulse_certificate_sha256=digest(out / 'SP28_info_native_factor_certificate.json'),
        written_proof_sha256=digest(ROOT / 'Report/proofs/SP28_INFO_NATIVE_FACTOR.md'),
        wall_seconds=time.monotonic() - started)
    (out / 'SP28_info_native_factor_cofactor_certificate.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(dict(exact_full_net_cofactors=len(cases), global_reliability_established=False,
                          wall_seconds=result['wall_seconds'])), flush=True)


if __name__ == '__main__':
    main()
