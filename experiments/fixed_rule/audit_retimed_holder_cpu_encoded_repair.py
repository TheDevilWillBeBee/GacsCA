"""Independent audit of physical defect cones and executed encoded repair.

Consumes saved raw snapshots, never the event backend. Scalar F and its word
descriptor are evaluated separately, followed by the fixed projection/lift.
"""
import argparse
import json
from pathlib import Path
import resource
import time
import numpy as np

from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_projected as r
from gacsca.fixed_rule import retimed_holder_program as p,retimed_holder_core as c
from experiments.fixed_rule.audit_small_holder_position_events import sha


def transition(cells):
    scalar = f.local_step(cells)
    values = tuple(word for cell in cells for word in f.encode_cell(cell))
    described = f.decode_cell(f.self_description().evaluate(values))
    assert scalar == described,'scalar/descriptor disagreement'
    return r.lift(r.project(scalar))


def ring(raw):
    cells = tuple(f.decode_cell(row.tolist()) for row in raw)
    assert all(r.lift(r.project(cell)) == cell for cell in cells),'unnormalized represented metadata'
    return np.array([f.encode_cell(transition(tuple(cells[(col+d)%len(cells)] for d in f.NEIGHBORHOOD)))
                     for col in range(len(cells))],dtype=np.uint64)


def probe(positions, clean, dirty, after, sites, *, healed):
    positions = tuple(map(int,positions)); assert len(set(positions)) == len(positions)
    assert clean.shape == dirty.shape == after.shape == (len(positions),f.FIELDS)
    before = {pos:f.decode_cell(row.tolist()) for pos,row in zip(positions,dirty)}
    healthy = {pos:f.decode_cell(row.tolist()) for pos,row in zip(positions,clean)}
    final = {pos:f.decode_cell(row.tolist()) for pos,row in zip(positions,after)}
    changes = [pos for pos in positions if before[pos] != healthy[pos]]
    assert changes,'probe has no actual defect'
    affected = sorted({(pos-d)%sites for pos in changes for d in f.NEIGHBORHOOD})
    disagreements = 0
    for pos in affected:
        neighborhood = tuple((pos+d)%sites for d in f.NEIGHBORHOOD)
        assert all(source in before for source in neighborhood),'missing full physical causal halo'
        actual = transition(tuple(before[source] for source in neighborhood))
        expected = transition(tuple(healthy[source] for source in neighborhood))
        assert actual == final[pos],('saved faulty transition differs',pos)
        disagreements += actual != expected
    if healed:
        assert disagreements == 0,'late procedure fault did not rejoin its actual background'
    else:
        assert disagreements > 0,'initial three-copy corruption was silently erased'
    return dict(changed_input_sites=len(changes),complete_raw_outputs_checked=len(affected),
                outputs_different_from_unperturbed=disagreements)


def audit(path):
    receipt = json.loads(Path(path).read_text()); assert receipt['passed']
    for source,wanted in receipt['source_sha256'].items():
        assert sha(source) == wanted,source
    assert receipt['descriptor_sha256'] == f.self_description().digest()
    assert sha(receipt['snapshot']) == receipt['snapshot_sha256']
    n = receipt['colonies']; assert n == 15
    with np.load(receipt['snapshot'],allow_pickle=False) as z:
        assert z['initial'].shape == (n,f.FIELDS)
        initial = z['initial']; dirty = z['faulty_upper_initial']
        first = ring(initial); assert np.array_equal(ring(dirty),first)
        assert not np.array_equal(ring(z['negative_three_copy_initial']),first),'negative control became vacuous'
        second = ring(first)
        expected = np.stack((first,second))
        np.testing.assert_array_equal(z['decoded'],expected)
        np.testing.assert_array_equal(z['expected'],expected)
        np.testing.assert_array_equal(z['Hold_after_executed_upper_repair'],first)
        np.testing.assert_array_equal(z['after_first_lower_tick'],dirty)
        assert not np.array_equal(dirty,initial),'encoded corruption was absent'
        changed_upper = np.argwhere(initial != dirty)
        assert len(changed_upper) == 2
        assert all(f.SCHEMA[int(field)][0].endswith('_rb') for _,field in changed_upper)
        assert all(int(initial[col,field])^int(dirty[col,field]) == 1 for col,field in changed_upper)
        positions = tuple(map(int,z['initial_probe_positions']))
        delta = np.argwhere(z['initial_probe_clean'] != z['initial_probe_faulty'])
        observed = {(positions[int(row)],f.SCHEMA[int(field)][0]) for row,field in delta}
        wanted = {(row['position'],row['field']) for row in receipt['initial_one_bit_faults']}
        assert observed == wanted and len(observed) == 6
        for row,field in delta:
            assert int(z['initial_probe_clean'][row,field])^int(z['initial_probe_faulty'][row,field]) == 1
        initial_probe = probe(z['initial_probe_positions'],z['initial_probe_clean'],z['initial_probe_faulty'],
                              z['initial_probe_after_one_tick'],n*f.Q,healed=False)
        late_probe = probe(z['late_probe_positions'],z['late_probe_before'],z['late_probe_faulty'],
                           z['late_probe_after_one_tick'],n*f.Q,healed=True)
        assert late_probe['changed_input_sites'] == 2
        for _,field in np.argwhere(z['late_probe_before'] != z['late_probe_faulty']):
            name = f.SCHEMA[int(field)][0]
            assert name.startswith('s') and '_' in name and name.split('_',1)[1] in dict(f.PROCEDURE)
        for epoch in (1,2):
            data = z[f'physical_boundary_{epoch}_Data']; assert data.shape == (n,f.Q)
            np.testing.assert_array_equal(data[:,list(p.layout().info)],expected[epoch-1])
        np.testing.assert_array_equal(z['physical_rejoin_Data'],z['healthy_rejoin_Data'])
        assert not np.any(z['final_heads']) and not np.any(z['final_flags'])
        assert z['final_packets'].shape == (0,5)
        for name,field in (('final_right','f1'),('final_left','f2')):
            np.testing.assert_array_equal(z[name],second[:,f.COL[field]])
        controller_fields = [f.COL[f's{k}_{name}'] for k in range(5) for name in ('head',*c.CONTROL)]
        changed = [int(np.count_nonzero(a[:,controller_fields] != b[:,controller_fields]))
                   for a,b in ((initial,first),(first,second))]
        assert all(changed),'successive active controller dynamics not exercised'
    assert receipt['complete_physical_rejoin_time'] == f.U+1
    assert receipt['physical_ticks'] == 2*f.U
    return dict(passed=True,execution=str(path),execution_sha256=sha(path),snapshot_sha256=receipt['snapshot_sha256'],
                initial_physical_cone=initial_probe,late_physical_cone=late_probe,
                encoded_two_copy_repair_matches=True,encoded_three_copy_negative_control_differs=True,
                complete_raw_words_per_macrostep=n*f.FIELDS,represented_controller_words_changed=changed,
                saved_Data_rejoin_matches=True,
                limitation='Independent saved-cone/output/Data-rejoin audit. Full physical rejoin additionally relies on the execution-time comparison of all background arrays and the empty exception set. No stochastic threshold or full upper work-period claim.')


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--execution',required=True); parser.add_argument('--output',required=True)
    args = parser.parse_args(); out = Path(args.output)
    if out.exists():
        raise FileExistsError('preserve evidence')
    start = time.perf_counter(); result = audit(args.execution)
    result.update(source_sha256={str(path):sha(path) for path in
                                (Path(__file__),*(Path(module.__file__) for module in (f,r,p,c)))},
                  seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    out.write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2),flush=True)


if __name__ == '__main__':
    main()
