#!/usr/bin/env python3
"""All-private cofactors of measured short-epoch enclosure corners.

This does not prove that the endpoint corners are dynamically reachable.
It proves that the two allowed raw words really give different native
outputs in the explicitly changed full Boolean transitions.
"""
from pathlib import Path
import hashlib, json, sys, time
import numpy as np
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca.netlist import Compiled
from check_g17_schedule import Terms
import proposed_sparse_distant_epoch1024 as baseline
import proposed_sparse_short_epoch_duration as short


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    start = time.monotonic()
    out = ROOT/'figs/robustness'
    p = baseline.parameters()
    N = 256*p.Q
    asset = out/'SP28_short_epoch_initial_enclosure_traces.npz'
    rows = []
    with np.load(asset) as stored:
        for duration, offset, site in ((1024,2064,124365), (2048,2368,123453)):
            n, source = short.full_net(p, duration)
            comp = Compiled(n)
            raw = stored[f'{duration}_ambiguous_{offset}_planes']
            code = stored[f'{duration}_ambiguous_{offset}_code']
            assert not np.any(raw[[5,6,8,9]])
            for upper in (False, True):
                terms = Terms()
                nodes = [0,1]
                f1, f2 = (2,4) if upper else (1,3)
                for name in comp.inputs:
                    if name[0] != 'x':
                        value = terms.var(name)
                    else:
                        _, off, field, bit = name
                        y = (site+off)%N
                        words = dict(addr=(y+512*int(raw[0,y]))%p.Q,
                            age=p.age_code(p.T_wf+offset),
                            f1=int(raw[f1,y]), f2=int(raw[f2,y]), wf1=0,
                            wf2=int(raw[6,y]), packet_valid=int(raw[6,y]),
                            packet_tag=int(raw[7,y]), packet_count=0,
                            service_valid=int(raw[8,y]), service_position=int(code[y]),
                            service_count=0, backward_pressure=int(raw[9,y]))
                        value = (words[field]>>bit)&1 if field in words else terms.var(name)
                    nodes.append(value)
                for op, a, b in comp.gates:
                    nodes.append(terms.op(op, nodes[a], nodes[b]))
                outputs = {}
                for field, width in (('addr',p.k), ('age',p.m), ('f1',1), ('f2',1)):
                    bits = [nodes[comp.outputs['y',field,b]] for b in range(width)]
                    assert all(value in (0,1) for value in bits), (duration,upper,field,bits)
                    outputs[field] = sum(value<<b for b,value in enumerate(bits))
                expected_addr = (site+(512 if upper else 0))%p.Q
                assert outputs == dict(addr=expected_addr,
                    age=p.age_code(p.T_wf+offset+1), f1=1, f2=int(upper))
                rows.append(dict(duration=duration, offset=offset, site=site,
                    upper_native_corner=upper, outputs=outputs,
                    all_private_and_instruction_bits_free=True,
                    netlist_sha256=comp.digest,
                    generated_source_sha256=hashlib.sha256(source.encode()).hexdigest()))
    result = dict(name='Short SP28 epochs: exact local ambiguity of flag enclosure',
        Q=p.Q,U=p.U,T_wf=p.T_wf,error_separation_c=16,
        explicit_duration_only_rule_changes=[1024,2048],
        exact_full_native_free_private_cofactors=len(rows), corner_rows=rows,
        allowed_native_enclosure_corners_give_distinct_GF_outputs_proved=True,
        measured_projection_is_full_universal_refinement_proved=False,
        corners_dynamically_reachable_from_intact_hierarchy_proved=False,
        changed_duration_own_programme_or_self_simulation_proved=False,
        short_duration_finite_island_eroder_or_obstruction_proved=False,
        iid_failure_proved=False, global_reliability_established=False,
        active_G17_modified=False, original_SP28_modified=False,
        checker_sha256=digest(__file__), family_source_sha256=digest(short.__file__),
        epoch_helper_source_sha256=digest(ROOT/'Report/proofs/proposed_sparse_epoch_duration_family.py'),
        baseline_source_sha256=digest(baseline.__file__),
        term_library_sha256=digest(ROOT/'Report/proofs/check_g17_schedule.py'),
        netlist_library_sha256=digest(ROOT/'gacsca/netlist.py'),
        measured_trace_asset_sha256=digest(asset),
        exploratory_source_sha256=digest(out/'SP28_short_epoch_initial_projection.c'),
        exploratory_receipts_sha256={name:digest(out/name) for name in
            ('SP28_short_epoch_1024_exploratory.json','SP28_short_epoch_2048_exploratory.json')},
        seconds=time.monotonic()-start,
        scope='Exact raw-state full-rule native cofactors; exploration/reachability/universal trajectory remain separate')
    (out/'SP28_short_epoch_local_corner_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(cofactors=len(rows),native_GF_outputs=[r['outputs']['addr'] for r in rows],
        dynamic_reachability_proved=False, global_reliability_established=False)), flush=True)


if __name__ == '__main__':
    main()
