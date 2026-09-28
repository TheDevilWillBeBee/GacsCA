"""Full-rule GPU bank checks on frozen complete-macrostep physical witnesses."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time
import numpy as np
from gacsca.fixed_rule import small_holder_bank as bank, small_holder_bank_cuda as gpu
from gacsca.fixed_rule import small_holder_rule as f


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as source:
        for part in iter(lambda:source.read(1024*1024),b''):h.update(part)
    return h.hexdigest()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
    started=time.perf_counter();prefix=Path(args.input);manifest=json.loads(prefix.with_suffix('.json').read_text())
    assert manifest['rule']['full_rule']['description_sha256']==f.self_description().digest()
    artifact=prefix.with_suffix('.npz');assert digest(artifact)==manifest['artifact_sha256']
    with np.load(artifact) as archive:
        inputs=archive['sample_inputs'];outputs=archive['sample_outputs'];keys=archive['sample_keys']
    selected=set(map(int,np.linspace(0,len(inputs)-1,64,dtype=int)))
    # Include observed controller/flag activity in addition to uniform coverage.
    for field in ('s2_head','s2_pc','s2_rp_valid','s2_lp_valid','f1','f2','w2_wf1','w2_wf2','signal'):
        where=np.flatnonzero(inputs[:,7,f.COL[field]])
        if len(where):selected.update((int(where[0]),int(where[-1])))
    selected=sorted(selected);b=bank.Builder(1,0);positions=[]
    for i,index in enumerate(selected):
        center=16*i+7;positions.append(center)
        for offset,row in enumerate(inputs[index]):
            b.set_raw_fields(16*i+offset,**dict(zip((name for name,_ in f.SCHEMA),map(int,row))))
    snapshot=b.freeze()
    with gpu.Resident(snapshot) as resident:
        old=resident.evaluate(positions,reconstruct=True);new=resident.evaluate(positions);device=resident.device_bytes
    np.testing.assert_array_equal(old,inputs[selected,7]);np.testing.assert_array_equal(new,outputs[selected])
    out=Path(args.output);out.parent.mkdir(parents=True,exist_ok=True)
    np.savez_compressed(out.with_suffix('.npz'),selected=np.array(selected),sample_keys=keys[selected],inputs=inputs[selected],new=new,expected=outputs[selected])
    result=dict(passed=True,archived_macrostep=str(prefix),artifact_sha256=manifest['artifact_sha256'],description_sha256=f.self_description().digest(),witnesses=len(selected),raw_fields=f.FIELDS,all_controller_and_metadata_fields_compared=True,source_cells_relocated_with_all_raw_metadata_retained=True,storage_bytes=snapshot.storage_bytes,explicit_device_bytes=device,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,seconds=time.perf_counter()-started,source_sha256={str(path):digest(path) for path in (Path(__file__),Path(bank.__file__),Path(gpu.__file__),Path(gpu.__file__).with_suffix('.cu'))},binary_sha256=digest(gpu.library()._name),limitation='local witnesses from an existing CPU macrostep; this does not execute a full macrostep on GPU')
    out.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='source_sha256'},indent=2))


if __name__=='__main__':main()
