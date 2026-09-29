"""Conditional full-state join for the selected nine fresh replacement marks.

The damaged world is related by complete-descriptor induction to an independently
evolved healthy world. No healthy state is installed into a damaged executor.
"""
import argparse
import json
from pathlib import Path
import resource
import time
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_core as c
from gacsca.fixed_rule import retimed_holder_projected as r, retimed_holder_program as p
from gacsca.fixed_rule import retimed_holder_geometry_projection as geometry
from gacsca.fixed_rule import retimed_holder_compiled_events as events
from gacsca.fixed_rule import retimed_holder_literal_cone as cone
from experiments.fixed_rule.audit_retimed_holder_prefix_embedding import sha
from experiments.fixed_rule.join_retimed_holder_full_ring_repair import post_reset_words


def neighbor_static_independence(description=None):
    from gacsca.fixed_rule.wordcode import LIT
    desc=f.self_description() if description is None else description
    forbidden=[i//f.FIELDS!=7 and i%f.FIELDS<len(f.STATIC) for i in range(desc.inputs)]
    for kind,a,b in desc.operations:
        forbidden.append(False if kind==LIT else forbidden[a] or forbidden[b])
    assert not any(forbidden[index] for index in desc.outputs), 'neighbor static metadata affects output'
    return dict(unused_neighbor_static_inputs=14*len(f.STATIC),complete_outputs_checked=len(desc.outputs))


def healthy_heads(stop=16989):
    """Scalar fixed-ROM head trace; prove no Data read/write or packet birth."""
    if stop!=16989:raise ValueError('certified early interval required')
    record=dict(head=1,**{name:0 for name in c.CONTROL});trace={1:record.copy()}
    for age in range(1,stop):
        address=age-1
        cell=c.Cell(**r.record(address),**record,address=address,age=age)
        assert not cell.last and not cell.direction and not c.waiting(cell) and not c.halted(cell)
        assert cell.phase!=c.TRANSMIT
        assert not (cell.kind==c.MEM and cell.phase==c.WRITE and cell.index==cell.rd)
        # For this trace, changing any encountered memory Data cannot affect
        # the complete next controller; no represented Info is read yet.
        alternate=c.Cell(**{**cell.__dict__,'data':(1<<64)-1})
        assert c.advance(cell)==c.advance(alternate)
        record=dict(head=1,**c.advance(cell),direction=c.RIGHT)
        trace[age+1]=record.copy()
    return trace


def check_zero_neighborhoods(data, head_position, centers):
    """The complete raw radius-seven stencil covers logical offsets -9..9."""
    assert data.shape==(f.Q,) and data.dtype==np.uint64
    logical=(np.asarray(centers,dtype=np.int64)[:,None]+np.arange(-9,10))%f.Q
    assert not np.any(data[logical]), 'nonzero Data in dangerous geometry neighborhood'
    assert not np.any(logical==head_position), 'healthy controller in dangerous geometry neighborhood'
    return int(logical.size)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    out=Path(parser.parse_args().output);artifact=out.with_suffix('.npz')
    if out.exists() or artifact.exists():raise FileExistsError(out)
    started=time.perf_counter();root=Path('figs/fixed_rule')
    names=('geometry_procedure_effects_v1','fresh_geometry_recovery_128_v1',
           'early_geometry_projection_v1','fresh_geometry_projection_v1','geometry_flags_v1',
           'full_ring_repair_v1','wide_next_periods_3_v2','normalization_prefix_v1','noiseless_period_v1')
    paths={name:root/('retimed_holder_'+name+'.json') for name in names}
    docs={name:json.loads(path.read_text()) for name,path in paths.items()}
    for name,doc in docs.items():
        assert doc.get('passed',doc.get('completed')) is True,name
        for source,digest in {**doc.get('source_sha256',{}),**doc.get('input_sha256',{})}.items():assert sha(source)==digest,source
        if 'artifact_sha256' in doc:assert sha(paths[name].with_suffix('.npz'))==doc['artifact_sha256']
    assert docs['geometry_flags_v1']['final_age']==16989
    assert docs['normalization_prefix_v1']['first_SEND_birth_age']>16989
    assert docs['full_ring_repair_v1']['conditional_full_ring_physical_repair_join']
    with np.load(paths['full_ring_repair_v1'].with_suffix('.npz'),allow_pickle=False) as saved:
        assert not np.any(saved['period3_full_healthy'][:,[f.COL['f1'],f.COL['f2']]])
    with np.load(paths['wide_next_periods_3_v2'].with_suffix('.npz'),allow_pickle=False) as saved:
        bank=saved['period3_bank'][36:37].copy();signals=saved['period3_signals'][36:37].copy()
        assert not np.any(saved['period3_signals'][35:39])
        assert not np.any(saved['period3_bank'][35:39,-5:])
        info=bank[0,np.array(p.layout().info)].copy()
    with np.load(paths['fresh_geometry_recovery_128_v1'].with_suffix('.npz'),allow_pickle=False) as saved:
        actual,reference,positions=saved['final_actual'],saved['final_reference'],saved['final_positions']
        common=[j for j,(name,_) in enumerate(f.SCHEMA) if not name.startswith('p') and name not in ('address','f1','f2')]
        np.testing.assert_array_equal(actual[:,common],reference[:,common])
        assert np.all(actual[:,f.COL['age']]==128)
        assert not np.any(actual[:,f.COL['signal']])
        cone_support=(positions[0]<=1210608-5-7*128 and positions[-1]>=1210608+5+7*128)
        assert cone_support
    with np.load(paths['fresh_geometry_projection_v1'].with_suffix('.npz'),allow_pickle=False) as saved:
        geom=saved['tick128_geometry'].copy();expected_640=saved['tick640_geometry'];expected_1024=saved['tick1024_geometry']
    np.testing.assert_array_equal(actual[:,[f.COL[x] for x in ('address','f1','f2')]],geom[positions%f.Q])

    metadata_independence=neighbor_static_independence()
    trace=healthy_heads();g=p.layout();first_times=g.schedule(0,1)[1][0]
    assert first_times==(9913,65349) and g.computation_cells>16989
    image=cone.BankImage(bank,signals)
    world=events.World(image.cells,size=f.Q,time=4*f.U)
    world.advance(1)
    expected=post_reset_words(info)
    np.testing.assert_array_equal(world.words,expected)
    initial_data=world.words[:,events.global_events.COL['data']].copy()
    checks=0
    for age in (128,640,9912,9913,16989):
        world.advance(4*f.U+age-world.time)
        assert world.heads==(age-1,)
        np.testing.assert_array_equal(world.words[:,events.global_events.COL['data']],initial_data)
        assert not np.any(world.words[:,events.global_events.MAIL]) and not np.any(world.signals)
        for name,value in trace[age].items():assert world.words[age-1,events.global_events.COL[name]]==value
        no_head=world.words.copy();no_head[age-1,events.global_events.CONTROL]=0
        assert not np.any(no_head[:,events.global_events.CONTROL])
        checks+=world.words.size+len(world.signals)
    # Confirm the initial literal window is this same healthy trajectory at128.
    # The controller is far outside the window; Data has not changed after reset.
    np.testing.assert_array_equal(reference,world.cells(positions%f.Q,age=128))

    canonical=np.arange(f.Q);danger_count=neighborhood_words=0;first_canonical=None
    for age in range(128,1024):
        nxt=geometry.step(geom,age)
        danger=np.flatnonzero((geom[:,0]!=canonical)|(nxt[:,0]!=canonical))
        if len(danger):
            assert np.all(danger>=30960), 'address defect escaped the empty tail corridor'
            neighborhood_words+=check_zero_neighborhoods(initial_data,age-1,danger)
            danger_count+=len(danger)
        elif first_canonical is None:first_canonical=age
        geom=nxt
        if age+1==640:np.testing.assert_array_equal(geom,expected_640)
    np.testing.assert_array_equal(geom,expected_1024)
    assert first_canonical is not None and first_canonical<=640
    # After canonical Address returns, only zero-mail Flag1 clearing can affect
    # procedures; the reference trace excludes all packet generation until16989.
    np.savez_compressed(artifact,healthy_final_procedures=world.words,healthy_final_Signals=world.signals,
                        healthy_physical_event_trace=np.array(world.trace,dtype=np.uint64),
                        healthy_initial_reset_Data=initial_data)
    sources=(Path(__file__),Path(events.__file__),Path(events.__file__).with_suffix('.cc'),
             Path(events.global_events.__file__),Path(geometry.__file__),Path(f.__file__),Path(c.__file__),Path(p.__file__),
             Path('experiments/fixed_rule/join_retimed_holder_full_ring_repair.py'))
    result=dict(passed=True,conditional_complete_selected_fresh_fault_repair=True,
                full_state_rejoin_age=16989,full_state_rejoin_local_physical_time=4*f.U+16989,
                first_canonical_input_age_seen=first_canonical,
                dangerous_old_or_new_Address_output_cases=danger_count,
                healthy_zero_logical_operand_checks=neighborhood_words,
                healthy_complete_procedure_and_Signal_words_compared=checks,
                healthy_scalar_head_transitions=16988,healthy_first_fetch=9913,healthy_first_write=65349,
                all_Data_unchanged_after_healthy_reset=True,all_healthy_mail_zero=True,
                entry_complete_nonROM_nongeometry_equality=True,
                neighbor_metadata_independence=metadata_independence,
                raw_procedure_outputs_covered=docs['geometry_procedure_effects_v1']['effects']['complete_procedure_outputs'],
                no_actual_reference_state_installation=True,
                inherited_geometry_projection_backend_limitations=True,
                full_noisy_world_literal_ticks=128,new_literal_full_ring_GPU_execution=False,
                descriptor_sha256=f.self_description().digest(),
                input_sha256={str(path):sha(path) for path in paths.values()},
                source_sha256={str(path):sha(path) for path in sources},
                artifact_sha256=sha(artifact),seconds=time.perf_counter()-started,
                host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                scope='Conditional complete-state induction from the actual noisy tick128 '
                      'entry to equality with the fault-free trajectory at16989. Uses complete '
                      'descriptor identities, checked empty dangerous neighborhoods, exact '
                      'healthy physical execution and the prior geometry restoration evidence. '
                      'No new literal noisy suffix or general noise theorem is claimed.')
    with out.open('x') as stream:stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
