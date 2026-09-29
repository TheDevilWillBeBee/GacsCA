"""Independent native audit of coherent procedure and Flag1-masked mail outputs."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import resource
import time

from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c, small_holder_native as native
from experiments.fixed_rule import certify_small_holder_procedure_image as proof
from experiments.fixed_rule.audit_small_holder_clock_mail_factorization import assignment
from experiments.fixed_rule.audit_small_holder_position_events import evaluate,sha


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--certificate',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    started=time.perf_counter();cert=json.loads(Path(args.certificate).read_text())
    assert cert['passed'] and cert['descriptor_sha256']==f.self_description().digest()
    for path,wanted in cert['source_sha256'].items():assert sha(path)==wanted,path
    assert cert['mask_majority']==proof.mask_majority()
    assert {row['phase'] for row in cert['cases']}=={None,*range(8)} and len(cert['cases'])==9
    ages=(0,c.RESET_AGES[2],c.VOTE_AGES[0],c.CAPTURE_AGE-1,c.WF_START-1,c.WF_START,c.WF_END-1,c.WF_END,c.ACTIVE_ENDS[0],f.U-1)
    addresses=(0,3,f.Q-3,f.Q-1)
    rng=random.Random(2026092803);outputs=groups=masks=majorities=0;digest=hashlib.sha256()
    for phase in (None,*range(8)):
        terms,raw,_=proof.raw_mail.prepare(phase)
        rows={pos:tuple(raw(pos+j) for j in f.NEIGHBORHOOD) for pos in range(-3,4)}
        for index,age in enumerate(ages):
            for mode in ('raw','dense','two_bad'):
                values=evaluate(terms,assignment(terms,phase,age,addresses[index%4],mode,rng));actual={}
                assert values[terms.variable('physical_age',32)]==age
                for pos,neighborhood in rows.items():
                    cells=tuple(f.decode_cell(tuple(values[x] for x in row)) for row in neighborhood)
                    actual[pos]=f.local_step(cells);assert actual[pos]==native.local_step(cells);outputs+=1
                for primary in (-1,0,1):
                    holders=[actual[primary+e] for e in f.OFFSETS]
                    for name in ('data','head',*c.CONTROL,'wf1','wf2'):
                        prefix='w' if name in ('wf1','wf2') else 's'
                        copies=[getattr(cell,f'{prefix}{2-e}_{name}') for e,cell in zip(f.OFFSETS,holders)]
                        assert len(set(copies))==1,(phase,age,mode,primary,name);groups+=1
                    survivors=sum(not cell.f1 for cell in holders)
                    for name in proof.raw_mail.MAIL:
                        copies=[getattr(cell,f's{2-e}_{name}') for e,cell in zip(f.OFFSETS,holders)]
                        available=[value for value,cell in zip(copies,holders) if not cell.f1]
                        common=available[0] if available else 0
                        for value,cell in zip(copies,holders):
                            assert value==(0 if cell.f1 else common),(phase,age,mode,primary,name,'mask');masks+=1
                        assert f.majority5(tuple(copies))==(common if survivors>=3 else 0)
                        digest.update(json.dumps((phase,age,mode,primary,name,copies),separators=(',',':')).encode());majorities+=1
    paths=[Path(__file__),Path(proof.__file__),Path('experiments/fixed_rule/audit_small_holder_clock_mail_factorization.py'),Path('experiments/fixed_rule/audit_small_holder_position_events.py')]
    result=dict(passed=True,complete_scalar_native_outputs=outputs,coherent_five_replica_groups_checked=groups,
                holder_mail_mask_identities_checked=masks,decoded_mail_majorities_checked=majorities,
                output_sha256=digest.hexdigest(),sampled_clock_ages=ages,certificate_sha256=sha(args.certificate),
                source_sha256={str(path):sha(path) for path in paths},seconds=time.perf_counter()-started,
                host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                limitation='Finite semantic audit of output shape. No Signal-coherence, head-count/confinement or whole-period/nested/noise induction claim.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
