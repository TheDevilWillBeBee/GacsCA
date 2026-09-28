"""Disambiguate the retained WRITE value from a newly executed represented WRITE.

The reusable macrostep audit has an historical active_simulated_WRITE label. On
the second period it refers to the retained result; that step moves the active
head. This audit classifies the actual input phase and raw controller changes.
"""
import argparse,hashlib,json
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import holder_core as c,holder_projected as r,holder_rule as f


def execute(stems,output):
    output=Path(output)
    if output.exists():raise FileExistsError('preserve evidence')
    rows=[]
    for stem in map(Path,stems):
        record=json.loads(stem.with_suffix('.json').read_text());assert hashlib.sha256(stem.with_suffix('.npz').read_bytes()).hexdigest()==record['artifact_sha256']
        with np.load(stem.with_suffix('.npz'),allow_pickle=False) as data:old=r.cells_from_array(data['initial_top']);new=r.cells_from_array(data['decoded'])
        names=[f's{d+2}_{name}' for d in f.OFFSETS for name in ('head',*c.CONTROL)]
        changed=sum(getattr(a,n)!=getattr(b,n) for a,b in zip(old,new) for n in names)
        writes=[i for i,cell in enumerate(old) if cell.s2_head and cell.s2_phase==c.WRITE and cell.s2_rd==cell.address]
        assert changed>0
        rows.append(dict(stem=str(stem),active_primary_WRITE_inputs=writes,raw_controller_words_changed=changed,center_primary_data_before=old[7].s2_data,center_primary_data_after=new[7].s2_data))
    assert rows[0]['active_primary_WRITE_inputs']==[7] and rows[1]['active_primary_WRITE_inputs']==[]
    result=dict(passed=True,periods=rows,correction='The second macrostep audit boolean active_simulated_WRITE denotes its retained WRITE result, not a second newly executed WRITE. Both periods execute active raw controller dynamics.')
    output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',nargs=2,required=True,type=Path);p.add_argument('--output',required=True,type=Path);a=p.parse_args();execute(a.input,a.output)
