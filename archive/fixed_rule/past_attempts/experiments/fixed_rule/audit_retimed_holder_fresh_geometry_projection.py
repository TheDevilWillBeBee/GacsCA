"""Diagnostic early geometry continuation with scalar and literal-prefix checks."""
import argparse
import json
from pathlib import Path
import resource
import time
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_core as c
from gacsca.fixed_rule import retimed_holder_geometry_projection as projection
from experiments.fixed_rule.audit_retimed_holder_prefix_embedding import sha


def scalar_output(state, age, site):
    cells=tuple(c.Cell(address=int(state[(site+j)%len(state),0]),age=age,
                       f1=int(state[(site+j)%len(state),1]),f2=int(state[(site+j)%len(state),2])) for j in range(-5,6))
    value=c.maintenance(cells)
    assert value['age']==age+1
    return np.array([value['address'],value['f1'],value['f2']],dtype=np.int64)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    args=parser.parse_args();out=Path(args.output);artifact=out.with_suffix('.npz')
    if out.exists() or artifact.exists(): raise FileExistsError(out)
    started=time.perf_counter();root=Path('figs/fixed_rule')
    paths={key:root/('retimed_holder_'+name+'.json') for key,name in (
        ('certificate','early_geometry_projection_v1'),('entry','residual_reactivation_audit_v3'),
        ('literal','fresh_geometry_recovery_128_v1'))}
    for key,path in paths.items():
        doc=json.loads(path.read_text());assert doc['passed']
        for source,digest in doc.get('source_sha256',{}).items(): assert sha(source)==digest,source
        if key!='certificate': assert sha(path.with_suffix('.npz'))==doc['artifact_sha256']
    with np.load(paths['entry'].with_suffix('.npz'),allow_pickle=False) as saved:
        marks=[(int(t),int(pos)%f.Q,row[[f.COL[x] for x in ('address','f1','f2')]].astype(np.int64))
               for t,pos,row in zip(saved['fault_times'],saved['fault_positions'],saved['fault_replacements'])]
        prefix={key:saved[key] for key in saved.files if key.startswith('tick')}
    with np.load(paths['literal'].with_suffix('.npz'),allow_pickle=False) as saved:
        literal=saved['final_actual'];literal_positions=saved['final_positions']%f.Q
    state=np.column_stack((np.arange(f.Q),np.zeros((f.Q,2),dtype=np.int64)))
    healthy_address=state[:,0].copy();anchor=30960
    raw_columns=[f.COL[x] for x in ('address','f1','f2')]
    rng=np.random.default_rng(1941);checks=0;rows=[];arrays={}
    for age in range(1024):
        for t,pos,row in marks:
            if t==age: state[pos]=row
        updated=projection.step(state,age)
        # Check every local pattern near Address defects and flag boundaries,
        # plus reproducible interior/background sites on every physical tick.
        critical=np.flatnonzero((state[:,0]!=healthy_address)|np.any(state[:,1:]!=np.roll(state[:,1:],1,axis=0),axis=1))
        sites=set(int(x) for x in rng.integers(0,f.Q,size=16))
        sites.update(int((x+d)%f.Q) for x in critical for d in range(-5,6))
        for site in sorted(sites):
            np.testing.assert_array_equal(updated[site],scalar_output(state,age,site))
            checks+=3
        state=updated;tick=age+1
        if tick<=5:
            idx=prefix[f'tick{tick}_positions']%f.Q
            np.testing.assert_array_equal(state[idx],prefix[f'tick{tick}_actual'][:,raw_columns])
        if tick==128:
            np.testing.assert_array_equal(state[literal_positions],literal[:,raw_columns])
        different=(state[:,0]!=healthy_address)|np.any(state[:,1:]!=0,axis=1)
        offsets=(np.flatnonzero(different)-anchor+f.Q//2)%f.Q-f.Q//2
        assert np.all(np.abs(offsets)<=5+5*tick)
        if tick in (5,8,16,32,64,128,256,512,600,601,602,603,604,605,640,768,1024):
            bad=np.flatnonzero(state[:,0]!=healthy_address)
            row=dict(tick=tick,wrong_Addresses=len(bad),Flag1=int(np.count_nonzero(state[:,1])),
                     Flag2=int(np.count_nonzero(state[:,2])),
                     wrong_Address_offsets=((bad-anchor+f.Q//2)%f.Q-f.Q//2).tolist(),
                     wrong_Address_values=state[bad,0].tolist(),
                     support_min=int(offsets.min()) if len(offsets) else None,
                     support_max=int(offsets.max()) if len(offsets) else None)
            rows.append(row);arrays[f'tick{tick}_geometry']=state.copy()
            print(json.dumps(row),flush=True)
    np.savez_compressed(artifact,**arrays)
    result=dict(passed=True,projected_physical_ticks=1024,observations=rows,
                independently_checked_scalar_geometry_words=checks,
                every_tick_boundary_patterns_and_random_sites_checked=True,
                every_vector_output_independently_scalar_checked=False,
                literal_prefix_geometry_words_matched=(len(literal_positions)+sum(len(prefix[f'tick{t}_positions']) for t in range(1,6)))*3,
                domain_uniform_age_and_zero_Wf=True,full_simulation_state_executed=False,
                periodic_diagnostic_cells=f.Q,full_ring_geometry_relation_by_radius_five=True,
                geometry_rejoined=not np.any(different),descriptor_sha256=f.self_description().digest(),
                input_sha256={str(x):sha(x) for x in paths.values()},
                source_sha256={str(x):sha(x) for x in (Path(__file__),Path(projection.__file__),Path(c.__file__))},
                artifact_sha256=sha(artifact),seconds=time.perf_counter()-started,
                host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                scope='Diagnostic physical geometry projection through tick1024 under the '
                      'checked uniform-clock/Wf0 domain. Complete literal geometry prefix '
                      'through128 and scalar boundary/random cases agree. The suffix does '
                      'not execute controller/Data state or prove their repair.')
    with out.open('x') as stream: stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='observations'},indent=2),flush=True)


if __name__=='__main__': main()
