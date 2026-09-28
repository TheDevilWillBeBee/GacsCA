"""Join local descriptor lemmas into a canonical global structural invariant.

This checks proof dependencies and the spatial composition obligations. It is
not an evolution executor and does not infer correct simulated macrosteps.
"""
import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import resource
import time

from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c
from gacsca.fixed_rule.wordcode import LIT
from experiments.fixed_rule import certify_small_holder_head_invariant as head


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def support(description=None):
    desc=f.self_description() if description is None else description
    @lru_cache(None)
    def used(wire):
        if wire<desc.inputs:
            name=f.SCHEMA[wire%f.FIELDS][0]
            return frozenset((wire,)) if name.startswith('s') and '_' in name and name.split('_',1)[1] in ('head',*c.CONTROL) else frozenset()
        op,a,b=desc.operations[wire-desc.inputs]
        return frozenset() if op==LIT else used(a)|used(b)
    rows={};static=0
    for index,((name,_),wire) in enumerate(zip(f.SCHEMA,desc.outputs)):
        if name.startswith('p'):
            assert wire==7*f.FIELDS+index,('static metadata changed',name);static+=1
        if name.startswith(('s','w')) and '_' in name:
            slot,suffix=name.split('_',1)
            if suffix not in ('data','head',*c.CONTROL,'wf1','wf2'):continue
            primary=int(slot[1:])-2
            sources=[]
            for source in used(wire):
                holder=source//f.FIELDS-7;old_name=f.SCHEMA[source%f.FIELDS][0]
                old_slot=int(old_name.split('_',1)[0][1:])-2
                sources.append(holder+old_slot-primary)
            relative=sorted(set(sources))
            assert all(abs(offset)<=1 for offset in relative),('head/controller logical support exceeds one',name,relative)
            rows[name]=relative
    assert static==len(f.STATIC)==49
    return dict(passed=True,static_fields_preserved=static,logical_head_controller_dependency_offsets=rows,
                maximum_head_controller_logical_radius=max(abs(x) for row in rows.values() for x in row))


def validate_certificate(path):
    data=json.loads(Path(path).read_text())
    assert data['passed'] and data['descriptor_sha256']==f.self_description().digest()
    for source,wanted in data['source_sha256'].items():assert sha(source)==wanted,source
    return data


def join(head_certificate,image_certificate):
    h=validate_certificate(head_certificate);image=validate_certificate(image_certificate)
    assert not h['pilot'] and h['geometry']==head.geometry()
    for proof in (h,image):
        assert len(proof['cases'])==9 and {row['phase'] for row in proof['cases']}=={None,*range(8)}
        assert all(row['passed'] and row['all_clock_ages']==f.U for row in proof['cases'])
    assert all(row['routing_destinations_disjoint'] and row['active_head_survives_iff_not_halted'] for row in h['cases'])
    assert all(row['checked_primaries']==[-1,0,1] and row['canonical_geometry_preserved'] for row in image['cases'])
    dependencies=support();gap=h['geometry']['minimum_gap_to_next_colony_core']
    # A holder computes primaries at offsets -2..2, each reading head/control at
    # offsets -1..1; physical corrected() also constructs a harmless -4..4 halo.
    # Gap >=8 ensures this nine-primary halo never contains two legal heads.
    assert gap>=8,('two colony heads can enter one symbolic local case',gap)
    assert dependencies['maximum_head_controller_logical_radius']<=1
    # Image cases -1,0,1 cover the affected primaries. All other primaries are
    # identical to the no-head case as far as the relevant outputs are concerned.
    return dict(passed=True,spatial_support=dependencies,minimum_gap=gap,
                certificate_sha256={str(path):sha(path) for path in (head_certificate,image_certificate)},
                domain=dict(geometry='Address=i mod Q, uniform Age; infinite lattice or periodic ring of a positive integer number of colonies',
                            static='Actual fixed-ROM metadata coherent across holders',
                            procedure='Data/head/controller replicas coherent; inactive controller fields zero',
                            heads=f"At most one logical head in each core [kQ,kQ+{h['geometry']['core_cells']-1}], none outside cores",
                            unconstrained='Raw mail replicas, physical Flag1/Flag2, Signals and all raw Wf fields'),
                conclusion='Every literal synchronous physical F step preserves this domain; induction gives preservation for every finite number of physical ticks.',
                obligation_order=['Fixed-ROM static fields are unchanged; canonical geometry survives.',
                                  'Core spacing gives zero/one head per local proof domain.',
                                  'Head routes are disjoint, reflect at endpoints, wait or halt; reboot creates only the unique entry head.',
                                  'Output-image coherence and inactive-controller bit implications restore the procedure premise.',
                                  'Other raw fields remain unrestricted; no mail or Signal projection is inserted.'],
                limitation='Structural invariant only. Does not prove the actual instruction schedule, Data computations, Signal/capture/flag profiles, decoded macrosteps, damaged-geometry repair, finite-cap stability or nested/noise correctness.')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--head',required=True);parser.add_argument('--image',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    started=time.perf_counter();result=join(args.head,args.image)
    result.update(source_sha256={str(path):sha(path) for path in (Path(__file__),Path(head.__file__))},
                  seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='spatial_support'},indent=2),flush=True)


if __name__=='__main__':main()
