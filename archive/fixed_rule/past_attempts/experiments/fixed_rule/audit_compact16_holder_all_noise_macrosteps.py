"""Audit all eight actual commits, retaining invalid encoded words unmodified."""
import json
from pathlib import Path
import time
import numpy as np
from gacsca.fixed_rule import compact16_holder_rule as f,compact16_holder_projected as r,compact16_holder_program as p
from gacsca.fixed_rule import compact16_holder_literal_cone as cone
from experiments.fixed_rule.run_compact16_holder_streamed_depth2 import sha


def main():
    output=Path('figs/fixed_rule/compact16_holder_all_noise_macrosteps_audit_v1.json')
    if output.exists():raise FileExistsError(output)
    started=time.perf_counter();root=Path('figs/fixed_rule');batch_path=root/'compact16_holder_all_noise_macrosteps_v2.json';mail_path=root/'compact16_holder_mail_macrostep_v1.json'
    batch=json.loads(batch_path.read_text());mail=json.loads(mail_path.read_text());g=p.layout();rows=[];words=scalar=0
    assert batch['completed_macrosteps']==7 and not batch['passed'] and mail['passed']
    assert sha(batch['artifact'])==batch['artifact_sha256'] and sha(mail['artifact'])==mail['artifact_sha256']
    assert mail['reference_sha256']==sha(batch_path)
    for doc in (batch,mail):
        for source,digest in doc['source_sha256'].items():assert sha(source)==digest
    with np.load(mail['artifact'],allow_pickle=False) as mz,np.load(root/'compact16_holder_headless_macrostep_v1.npz',allow_pickle=False) as old:
        for case in range(8):
            record=batch['trials'][case];assert sha(record['checkpoint_artifact'])==record['checkpoint_artifact_sha256']
            with np.load(record['checkpoint_artifact'],allow_pickle=False) as z:
                if case==4:
                    np.testing.assert_array_equal(z['case4_stopped_raw'],mz['initial_raw'])
                    np.testing.assert_array_equal(cone.step(mz['initial_raw']),mz['emitted_raw']);words+=f.Q*f.FIELDS
                    get=lambda label:mz[label]
                else:get=lambda label:z[f'case{case}_'+label]
                expected=z['expected_upper_raw'];after=get('postcommit');decoded=get('decoded')
                for before_key,after_key in ((f'age{f.ACTIVE_ENDS[-1]-1}',f'age{f.ACTIVE_ENDS[-1]}'),(f'age{f.U-2}',f'age{f.U-1}'),(f'age{f.U-1}','postcommit')):
                    before=get(before_key);wanted=cone.step(before);np.testing.assert_array_equal(wanted,get(after_key));words+=wanted.size
                before=get(f'age{f.U-1}')
                np.testing.assert_array_equal(after[list(g.info),f.COL['s2_data']],decoded)
                for d in f.OFFSETS:np.testing.assert_array_equal(after[(np.array(g.info)-d)%f.Q,f.COL[f's{d+2}_data']],decoded)
                for pos in g.info:
                    hood=tuple(f.decode_cell(before[(pos+j)%f.Q]) for j in range(-7,8))
                    wanted=f.encode_cell(r.lift(r.project(f.local_step(hood))))
                    np.testing.assert_array_equal(after[pos],wanted);scalar+=1
                projected=np.array([decoded[f.COL[name]] for name,_ in r.SCHEMA],dtype=np.uint64)
                target=np.array([expected[f.COL[name]] for name,_ in r.SCHEMA],dtype=np.uint64)
                invalid=[dict(field=name,value=int(value),width=width) for (name,width),value in zip(r.SCHEMA,projected) if int(value)>=1<<width]
                if invalid:
                    try:r.decode_cell(projected)
                    except ValueError:pass
                    else:raise AssertionError('malformed projected state accepted')
                else:r.decode_cell(projected)
                correct=np.array_equal(decoded,expected)
                assert correct==(record.get('decoded_matches_intended_rule',False) if case!=4 else mail['decoded_matches_intended_rule'])
                if case in (3,7):np.testing.assert_array_equal(after,old[f'case{case}_postcommit']);words+=after.size
                row=dict(case=case,correct_complete_raw_macrostep=correct,raw_word_differences=int(np.count_nonzero(decoded!=expected)),
                         projected_word_differences=int(np.count_nonzero(projected!=target)),invalid_projected_words=invalid,
                         all_five_Info_copies_agree=True,independent_scalar_Info_sites=len(g.info),headless_path_crosscheck=case in (3,7))
                rows.append(row);print(json.dumps(row),flush=True)
    assert sum(row['correct_complete_raw_macrostep'] for row in rows)==1 and rows[1]['correct_complete_raw_macrostep']
    result=dict(passed=True,batch_reference=str(batch_path),batch_reference_sha256=sha(batch_path),mail_reference=str(mail_path),mail_reference_sha256=sha(mail_path),
                all_eight_histories_resolved=True,correct_cases=[1],incorrect_cases=[0,2,3,4,5,6,7],cases=rows,
                complete_raw_words_checked=words,independent_scalar_outputs=scalar,headless_paths_agree=True,
                descriptor_sha256=f.self_description().digest(),seconds=time.perf_counter()-started,source_sha256={str(Path(__file__)):sha(__file__)},
                scope='Full native boundary/commit checks and every Info scalar output, replica agreement, unmasked malformed-code detection, crosscheck against independent headless suffix. Not a full replay of every event interval or a noise-threshold estimate.')
    with output.open('x') as out:out.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'}),flush=True)


if __name__=='__main__':main()
