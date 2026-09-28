"""Verify exact full-state continuity and active control through two work periods."""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import parallel_holder_rule as f,parallel_holder_projected as r,parallel_holder_quotient as q,parallel_holder_core as core


def read(stem):
    stem=Path(stem);record=json.loads(stem.with_suffix('.json').read_text());data_path=stem.with_suffix('.npz')
    assert hashlib.sha256(data_path.read_bytes()).hexdigest()==record['artifact_sha256']
    with np.load(data_path,allow_pickle=False) as data:arrays={name:data[name] for name in data.files}
    return record,arrays


def audit(first,second_prefix,second,output):
    output=Path(output)
    if output.exists():raise FileExistsError('preserve evidence')
    a,x=read(first);b,y=read(second_prefix);c,z=read(second)
    assert a['rule']==b['rule']==c['rule']==json.loads(json.dumps(r.identity()))
    np.testing.assert_array_equal(x['logical_final'],y['logical_initial']);np.testing.assert_array_equal(y['logical_stored_final'],z['logical_initial'])
    np.testing.assert_array_equal(x['decoded'],y['initial_top']);np.testing.assert_array_equal(y['initial_top'],z['initial_top'])
    names=[n for n,_ in r.SCHEMA if any(n==f's{d+2}_{field}' for d in f.OFFSETS for field in ('head',*core.CONTROL))]
    cols=[r.COL[n] for n in names];changes=[]
    for arrays in (x,z):
        changed=int(np.count_nonzero(arrays['initial_top'][:,cols]!=arrays['decoded'][:,cols]));assert changed>0;changes.append(changed)
    assert np.any(x['logical_final'][:,q.COL['signal']])
    for stem in (first,second):
        checked=Path(stem).with_name(Path(stem).stem.replace('_v1','_audit_v1')).with_suffix('.json')
        evidence=json.loads(checked.read_text());assert evidence['passed'] and evidence['complete_macrostep_ticks']==f.U
    result=dict(passed=True,successive_periods=2,physical_ticks=2*f.U,identical_rule_alphabet_neighborhood_and_ROM=True,raw_controller_changes=changes,exact_physical_state_handoff=True,old_signal_carried=True,represented_cells=len(x['decoded']),limitation='two complete one-link periods in the certified physical family; no depth-two dynamics or general noise-robustness claim')
    output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    for name in ('first','second-prefix','second','output'):p.add_argument('--'+name,required=True,type=Path)
    a=p.parse_args();audit(a.first,a.second_prefix,a.second,a.output)
