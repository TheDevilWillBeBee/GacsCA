"""Audit longer raw continuations and the projected headless macrostep failures."""
import json
from pathlib import Path
import time
import numpy as np
from gacsca.fixed_rule import compact16_holder_rule as f,compact16_holder_projected as r,compact16_holder_program as p
from gacsca.fixed_rule import compact16_holder_literal_cone as cone,compact16_holder_late_idle_gpu as idle
from experiments.fixed_rule.audit_compact16_holder_dense_noise import restore
from experiments.fixed_rule.run_compact16_holder_streamed_depth2 import sha


def read_receipt(stem):
    path=Path('figs/fixed_rule')/(stem+'_v1.json');doc=json.loads(path.read_text())
    assert doc['passed'] and sha(doc['artifact'])==doc['artifact_sha256']
    for source,digest in doc['source_sha256'].items():assert sha(source)==digest
    return path,doc


def main():
    output=Path('figs/fixed_rule/compact16_holder_canonical_noise_audit_v1.json')
    if output.exists():raise FileExistsError(output)
    start=time.perf_counter();path,doc=read_receipt('compact16_holder_canonical_noise');macro_path,macro=read_receipt('compact16_holder_headless_macrostep')
    words=0;scalar=0;rows=[];g=p.layout()
    with np.load(doc['artifact'],allow_pickle=False) as z:
        for case in range(8):
            before=restore(z,case,16383);after=restore(z,case,16384)
            np.testing.assert_array_equal(cone.step(before),after);words+=after.size
            for pos in (0,1,f.Q-2,f.Q-1):
                neighbors=tuple(f.decode_cell(before[(pos+j)%f.Q]) for j in range(-7,8))
                wanted=f.encode_cell(r.lift(r.project(f.local_step(neighbors))))
                np.testing.assert_array_equal(after[pos],wanted);scalar+=1
            for row in doc['trials'][case]['trace']:
                tick=row['additional_ticks'];actual=restore(z,case,tick);different=actual!=z[f'healthy_{tick}']
                assert np.count_nonzero(different)==row['different_raw_words']
                assert np.count_nonzero(np.any(different,axis=1))==row['different_sites']
                fields={name:int(np.count_nonzero(different[:,k])) for k,(name,_) in enumerate(f.SCHEMA) if np.any(different[:,k])}
                assert fields==row['different_fields']
            assert not np.any(after[:,[f.COL['f1'],f.COL['f2'],*(f.COL[f'w{k}_{name}'] for k in range(5) for name in ('wf1','wf2'))]])
    with np.load(macro['artifact'],allow_pickle=False) as z:
        expected=z['expected_upper_raw'];expected_projected=r.encode_cell(r.project(f.decode_cell(expected)))
        for case in (3,7):
            raw=z[f'case{case}_initial'];before=z[f'case{case}_precommit'];after=z[f'case{case}_postcommit']
            assert idle.LAST_EVENT<int(raw[0,f.COL['age']])<f.U-1
            # Independently check all GPU idle premises on complete saved state.
            for d in f.OFFSETS:
                for name,_ in f.PROCEDURE:
                    data=raw[:,f.COL[f's{d+2}_{name}']]
                    if name=='data':np.testing.assert_array_equal(data,np.roll(raw[:,f.COL['s2_data']],-d))
                    else:assert not np.any(data)
                for name in ('wf1','wf2'):assert not np.any(raw[:,f.COL[f'w{d+2}_{name}']])
                np.testing.assert_array_equal((raw[:,f.COL['signal']]>>np.uint64(d+2))&np.uint64(1),np.roll((raw[:,f.COL['signal']]>>np.uint64(2))&np.uint64(1),-d))
            assert not np.any(raw[:,[f.COL['f1'],f.COL['f2']]])
            expected_before=raw.copy();expected_before[:,f.COL['age']]=f.U-1
            np.testing.assert_array_equal(before,expected_before);words+=before.size
            np.testing.assert_array_equal(after,cone.step(before));words+=after.size
            decoded=after[list(g.info),f.COL['s2_data']];np.testing.assert_array_equal(decoded,z[f'case{case}_decoded'])
            for d in f.OFFSETS:
                positions=(np.array(g.info)-d)%f.Q
                np.testing.assert_array_equal(after[positions,f.COL[f's{d+2}_data']],decoded)
            actual_projected=r.encode_cell(r.project(f.decode_cell(decoded)))
            differences=[name for (name,_),a,b in zip(r.SCHEMA,actual_projected,expected_projected) if a!=b]
            assert differences,'failure must survive removal of metadata'
            # Independently scalar-check every physical primary Info output.
            for pos in g.info:
                neighbors=tuple(f.decode_cell(before[(pos+j)%f.Q]) for j in range(-7,8))
                wanted=f.encode_cell(r.lift(r.project(f.local_step(neighbors))))
                np.testing.assert_array_equal(after[pos],wanted);scalar+=1
            rows.append(dict(case=case,raw_decoded_differences=int(np.count_nonzero(decoded!=expected)),projected_decoded_differences=len(differences),
                             projected_differing_fields=differences,all_five_Info_copies_agree=True,actual_age=int(decoded[f.COL['age']]),expected_age=int(expected[f.COL['age']])))
    result=dict(passed=True,reference=str(path),reference_sha256=sha(path),macrostep_reference=str(macro_path),macrostep_reference_sha256=sha(macro_path),
                complete_raw_words_checked=words,scalar_outputs_checked=scalar,all_saved_counts_checked=True,all_eight_final_flag_planes_zero=True,
                independently_verified_idle_premises=True,failed_projected_macrosteps=rows,seconds=time.perf_counter()-start,
                source_sha256={str(Path(__file__)):sha(__file__)},
                scope='Native final-tick and complete-state/idle checks; scalar seams and every physical Info output. Two actual projected macrostep failures; other six macrostep outcomes remain open. Long factored trajectories not all independently replayed.')
    with output.open('x') as out:out.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result),flush=True)


if __name__=='__main__':main()
