"""Independent projected closure checks on saved physical-run checkpoints."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time
import numpy as np
from gacsca.fixed_rule import small_holder_rule as f,small_holder_projected as r
from gacsca.fixed_rule import small_holder_native as native,small_holder_program as p
from gacsca.fixed_rule import small_holder_core as c,small_holder_resident_gather as gpu
from gacsca.fixed_rule import small_holder_resident_independent as independent


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def checked_manifest(stem):
    manifest=json.loads(stem.with_suffix('.json').read_text());assert manifest['passed']
    assert digest(stem.with_suffix('.npz'))==manifest['artifact_sha256']
    for path,wanted in manifest['source_sha256'].items():assert digest(path)==wanted,path
    return manifest


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--geometry',required=True);parser.add_argument('--domain',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
    output=Path(args.output)
    if output.exists():raise FileExistsError('preserve evidence')
    started=time.perf_counter();geometry=Path(args.geometry);domain=Path(args.domain)
    gm=checked_manifest(geometry);dm=checked_manifest(domain);desc=f.self_description()
    assert gm['physical_descriptor_sha256']==dm['descriptor_sha256']==desc.digest()
    assert digest(gpu.library()._name)==gm['binary_sha256']
    assert digest(independent.library()._name)==dm['binary_sha256']
    with np.load(geometry.with_suffix('.npz'),allow_pickle=False) as z:frames={k:z[k] for k in z.files}
    initial=tuple(f.decode_cell(row.tolist()) for row in frames['initial']);state=initial
    assert state[7].address==30000 and all(r.lift(r.project(x))==x for x in state)
    metadata_counts=[]
    for step in range(2):
        raw=f.step_ring(state);assert raw==native.step_ring(state)
        for i,actual in enumerate(raw):
            inputs=tuple(word for j in f.NEIGHBORHOOD for word in f.encode_cell(state[(i+j)%len(state)]))
            assert f.decode_cell(desc.evaluate(inputs))==actual
        target=tuple(r.lift(r.project(x)) for x in raw)
        np.testing.assert_array_equal(native.array_from_cells(raw),frames['raw_outputs'][step])
        np.testing.assert_array_equal(native.array_from_cells(raw),frames['hold_before'][step])
        np.testing.assert_array_equal(native.array_from_cells(target),frames['hold_after'][step])
        np.testing.assert_array_equal(native.array_from_cells(target),frames['decoded'][step])
        differences=[(i,name) for i,(a,b) in enumerate(zip(raw,target)) for name,_ in f.STATIC if getattr(a,name)!=getattr(b,name)]
        assert differences==[tuple(x) for x in gm['cases'][step]['regenerated_fields']]
        assert raw!=target # omission of local regeneration would fail
        metadata_counts.append(len(differences));state=target
    assert frames['decoded'][0,7,f.COL['address']]==107
    assert frames['decoded'][0,7,f.COL['s2_data']]==0
    assert frames['decoded'][1,7,f.COL['s2_data']]==0x123456789ABCDEF0
    with np.load(domain.with_suffix('.npz'),allow_pickle=False) as z:metadata=z['metadata']
    assert metadata.shape==(f.Q,len(f.STATIC)) and dm['addresses']==f.Q
    # Independently totalize the fixed ROM, then check all offsets/selectors.
    table=np.array([[c.fallback(a,s) for s in range(len(c.STATIC))] for a in range(f.Q)],dtype=np.uint64)
    rom=p.base_rom();table[:len(rom)]=rom
    for slot,offset in enumerate(f.STATIC_OFFSETS):
        expected=table[(np.arange(f.Q,dtype=np.int64)+offset)%f.Q]
        np.testing.assert_array_equal(metadata[:,slot*7:(slot+1)*7],expected)
    result=dict(passed=True,two_successive_complete_raw_and_projected_steps=True,pre_and_post_regeneration_checkpoints_match=True,missing_regeneration_has_observed_counterexample=True,address_30000_repaired_to_107=True,cleared_controller_data_recovers_on_second_step=True,changed_metadata_words_per_period=metadata_counts,all_fixed_addresses_physically_regenerated=f.Q,all_offsets_and_selectors=True,checked_metadata_words=int(metadata.size),geometry_manifest_sha256=digest(geometry.with_suffix('.json')),domain_manifest_sha256=digest(domain.with_suffix('.json')),audit_source_sha256=digest(__file__),seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,scope='Independent scalar/native/descriptor and total-ROM checks of saved outputs. Physical evolution and host-call prohibition are runtime assertions in hashed drivers. The Address-domain run tests the clean regeneration subroutine, not all macrostep inputs or noise histories.')
    output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
