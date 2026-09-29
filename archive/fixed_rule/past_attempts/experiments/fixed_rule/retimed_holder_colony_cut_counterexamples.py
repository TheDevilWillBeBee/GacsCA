"""Concrete full-rule witnesses for two required colony-cut assumptions."""
import argparse
import json
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f
from gacsca.fixed_rule import retimed_holder_inert_storage as storage
from gacsca.fixed_rule import retimed_holder_literal_cone as cone
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    out=Path(parser.parse_args().output);artifact=out.with_suffix('.npz')
    if out.exists() or artifact.exists():raise FileExistsError(out)
    age=1232635846;center=f.Q
    empty=np.zeros((2*f.Q,len(storage.NAMES)),dtype=np.uint64)
    signals=np.zeros(2*f.Q,dtype=np.uint64)
    data={};observations=[];outputs={}
    cases={'baseline':{},'outside_ROM_head':{'head':1,'pc':42},
           'crossing_mail':{'rp_valid':1,'rp_remaining':1,'rp_target':0,'rp_data':85}}
    for name,changes in cases.items():
        words=empty.copy()
        for field,value in changes.items():words[center-1,storage.NAMES.index(field)]=value
        raw=storage.raw_words(words,signals,age,center+np.arange(-7,8))
        scalar=np.array(f.encode_cell(f.local_step(tuple(f.decode_cell(row) for row in raw))),dtype=np.uint64)
        actual=cone.step(raw)[7]
        np.testing.assert_array_equal(actual,scalar)
        data[name+'_input'],data[name+'_output']=raw,actual
        outputs[name]=actual
        observations.append(dict(case=name,changed_logical_site=center-1,source_changes=changes,
                                 right_primary_head=int(actual[f.COL['s2_head']]),
                                 right_primary_pc=int(actual[f.COL['s2_pc']]),
                                 right_primary_Data=int(actual[f.COL['s2_data']])))
    assert outputs['baseline'][f.COL['s2_head']]==0 and outputs['baseline'][f.COL['s2_data']]==0
    assert outputs['outside_ROM_head'][f.COL['s2_head']]==1 and outputs['outside_ROM_head'][f.COL['s2_pc']]==42
    assert outputs['crossing_mail'][f.COL['s2_data']]==85
    np.savez_compressed(artifact,**data)
    sources=(Path(__file__),Path(f.__file__),Path(storage.__file__),Path(cone.__file__))
    result=dict(passed=True,cases=observations,complete_scalar_native_outputs=3,
                descriptor_sha256=f.self_description().digest(),artifact_sha256=sha(artifact),
                source_sha256={str(path):sha(path) for path in sources},
                conclusion='A left-colony tail head enters the right colony; a left-colony packet writes right-colony Data. The cut cannot silently admit either case.',
                scope='Deterministic complete-rule counterexamples to dropping specific cut hypotheses; not a noise-frequency or general repair claim.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
