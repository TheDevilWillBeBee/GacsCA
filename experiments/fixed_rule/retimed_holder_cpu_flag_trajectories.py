"""All two-colony Signal patterns through exact physical forcing and clearing.

Run-length compression is lossless. Time skips require a measured fixed point
and stop at forcing-clock boundaries. No front shape is assumed for Flag2.
"""
import argparse
import itertools
import json
from pathlib import Path
import resource
import time

import numpy as np

from gacsca.fixed_rule import retimed_holder_flags_cpu as packed
from gacsca.fixed_rule import retimed_holder_cpu_general as general
from gacsca.fixed_rule import retimed_holder_cpu_events as events
from gacsca.fixed_rule import retimed_holder_flag_profile as profile
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_native as native
from experiments.fixed_rule.audit_small_holder_position_events import sha


def unpack(world):
    out = np.empty((world.colonies*packed.WORDS,2),dtype=np.uint64); start = 0
    for end,one,two in world.runs:
        out[start:int(end)] = (one,two); start = int(end)
    return out


def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--output',required=True)
    args = parser.parse_args(); out = Path(args.output); snapshot = out.with_suffix('.npz')
    if out.exists() or snapshot.exists():
        raise FileExistsError('preserve evidence')
    start = time.perf_counter()
    ages = (f.WF_START-1,f.WF_START,f.WF_START+1,f.WF_START+f.Q//2,
            f.WF_START+f.Q,f.WF_END-1,f.WF_END,f.WF_END+f.Q//2,f.WF_END+f.Q)
    patterns = tuple(itertools.product((0,1),repeat=4)); frames = []; metrics = []
    literal_checks = 0
    for pattern in patterns:
        right,left = pattern[:2],pattern[2:]; saved = []
        with packed.World(right,left,age=ages[0]) as world:
            for age in ages:
                world.run(age-world.info['age']); raw = unpack(world); saved.append(raw)
                lo,hi = profile.interval(age)
                for col in range(2):
                    value = ((1<<(hi-lo))-1)<<lo if right[col] else 0
                    expected = np.array([(value>>(64*k))&packed.MASK for k in range(packed.WORDS)],dtype=np.uint64)
                    np.testing.assert_array_equal(raw[col*packed.WORDS:(col+1)*packed.WORDS,0],expected)
                if age >= f.WF_END+f.Q//2:
                    assert not np.any(raw[:,0])
                if age >= f.WF_END+f.Q:
                    assert not np.any(raw)
                # Independent complete-F output checks at colony/word boundaries.
                domain = general.World(np.zeros((2,f.Q),dtype=np.uint64),
                    np.zeros((2,len(events.CONTROL)),dtype=np.uint64),np.zeros(2,dtype=np.uint64),
                    age=age,right=right,left=left,flags=raw)
                positions = [col*f.Q+a for col in range(2) for a in (0,4,7,63,64,f.Q-5,f.Q-1)]
                expected = {at:native.local_step(tuple(domain.cell(at+j) for j in f.NEIGHBORHOOD)) for at in positions}
                next_flags,_ = domain._flags_after(1)
                domain.flags = next_flags; domain.age += 1
                for at,wanted in expected.items():
                    actual = domain.cell(at)
                    for field in ('f1','f2','signal',*(f'w{k}_{name}' for k in range(5) for name in ('wf1','wf2'))):
                        assert getattr(actual,field) == getattr(wanted,field),(pattern,age,at,field)
                    literal_checks += 1
            metrics.append(world.info)
        if any(left):
            assert any(np.any(raw[:,1]) for raw in saved)
        frames.append(saved)
    frames = np.array(frames)
    # Exact interaction across a physical colony boundary, absent in an
    # independent-colony Flag2 model.
    yes = patterns.index((1,1,0,1)); no = patterns.index((1,1,0,0)); cutoff = ages.index(f.WF_END)
    assert np.any(frames[yes,cutoff,:packed.WORDS,1] != frames[no,cutoff,:packed.WORDS,1])
    rng = np.random.default_rng(552)
    arbitrary = rng.integers(0,2**64,size=(3*packed.WORDS,2),dtype=np.uint64); cleared = []
    with packed.World((1,0,1),(1,1,0),age=f.WF_END,runs=general.pack_runs(arbitrary)) as world:
        for age in (f.WF_END+f.Q//2,f.WF_END+f.Q):
            world.run(age-world.info['age']); raw = unpack(world); cleared.append(raw)
            assert not np.any(raw[:,0])
        assert not np.any(cleared[-1])
    np.savez_compressed(snapshot,ages=np.array(ages,dtype=np.uint64),patterns=np.array(patterns,dtype=np.uint8),
                        frames=frames,arbitrary_initial=arbitrary,arbitrary_cleared=np.array(cleared))
    files = [Path(__file__),Path(packed.__file__),Path(packed.__file__).with_suffix('.c'),
             Path(general.__file__),Path(profile.__file__),Path(f.__file__),Path(native.__file__)]
    result = dict(passed=True,patterns=16,sites_per_pattern=2*f.Q,physical_ticks_per_pattern=3*f.Q+1,
                  per_pattern_metrics=metrics,literal_selected_full_F_checks=literal_checks,
                  all_Flag1_frames_match_independent_profile=True,cross_colony_Flag2_witness=True,
                  arbitrary_initial_clearing_sites=3*f.Q,arbitrary_initial_clearing_ticks=f.Q,
                  snapshot=str(snapshot),snapshot_sha256=sha(snapshot),descriptor_sha256=f.self_description().digest(),
                  source_sha256={str(path):sha(path) for path in files},seconds=time.perf_counter()-start,
                  host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  scope='Physical flag projection with canonical geometry, coherent fixed Signals and derived Wf. All two-colony Signal patterns and arbitrary initial flag clearing; no geometry/controller-noise or hierarchy-level amplification claim.')
    out.write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2),flush=True)


if __name__ == '__main__':
    main()
