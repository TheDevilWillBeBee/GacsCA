"""Independent raw-cone, encoded-repair and saved complete-state rejoin audit."""
import argparse,hashlib,json,resource,time
from pathlib import Path
import numpy as np
from experiments.fixed_rule.audit_retimed_holder_cpu_encoded_repair import ring,probe
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_core as c
from gacsca.fixed_rule import retimed_holder_program as p,retimed_holder_quotient as q,retimed_holder_packed as packed
from gacsca.fixed_rule import retimed_holder_resident_period as period


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def state(data,prefix,n,expected_time):
    shapes={'bank':(n,p.layout().memory_count+5),'active_rows':(n,period.SLOTS,len(q.SCHEMA)),
            'counts':(n,),'flags':(n*f.Q//64,2),'signals':(n,2),'age':(),'time':()}
    result={name:data[prefix+name] for name in shapes}
    for name,shape in shapes.items():assert result[name].shape==shape and result[name].dtype==np.uint64,(prefix,name)
    assert int(result['time'])==expected_time and int(result['age'])==expected_time%f.U
    assert np.all(result['signals']<=1)
    on=f.WF_START<=int(result['age'])<f.WF_END;g=p.layout()
    for col,count in enumerate(result['counts']):
        assert int(count)<=period.SLOTS
        rows=result['active_rows'][col,:int(count)];packed.pack(rows)
        addresses=rows[:,q.COL['address']].tolist();assert addresses==sorted(set(addresses))
        assert not np.any(result['active_rows'][col,int(count):]),'unused diagnostic rows must be zero'
        left,right=map(int,result['signals'][col]);seen_signal=set()
        for row in rows:
            address=int(row[q.COL['address']]);assert address<f.Q
            pos=col*f.Q+address;word,bit=divmod(pos,64)
            first=(int(result['flags'][word,0])>>bit)&1;second=(int(result['flags'][word,1])>>bit)&1
            assert (int(row[q.COL['f1']]),int(row[q.COL['f2']]))==(first,second)
            assert row[q.COL['age']]==result['age']
            assert row[q.COL['wf1']]==int(on and address>=f.Q-5 and right)
            assert row[q.COL['wf2']]==int(on and address<=4 and left and not first)
            bank=address if address<g.memory_count else g.memory_count+address-(f.Q-5) if address>=f.Q-5 else None
            assert row[q.COL['data']]==(0 if bank is None else result['bank'][col,bank])
            signal=left<<(5-address) if 1<=address<=5 else right<<(f.Q-1-address) if address>=f.Q-5 else 0
            assert row[q.COL['signal']]==signal
            if signal:seen_signal.add(address)
            assert any(row[q.COL[name]] for name in period.ACTIVE)
        required=(set(range(1,6)) if left else set())|(set(range(f.Q-5,f.Q)) if right else set())
        assert seen_signal==required,'missing physical Signal holder'
    return result


def validate(z,old):
    n=15;initial=z['initial'];dirty=z['faulty_upper_initial'];first=ring(initial);second=ring(first)
    np.testing.assert_array_equal(initial,old['initial'])
    np.testing.assert_array_equal(ring(dirty),first)
    assert not np.array_equal(ring(z['negative_three_copy_initial']),first)
    expected=np.stack((first,second))
    for name in ('decoded','expected'):np.testing.assert_array_equal(z[name],expected)
    np.testing.assert_array_equal(z['Hold_after_executed_upper_repair'],first)
    np.testing.assert_array_equal(z['after_first_lower_tick'],dirty)
    differences=np.argwhere(initial!=dirty);assert len(differences)==2
    for col,field in differences:
        assert f.SCHEMA[int(field)][0].endswith('_rb') and int(initial[col,field])^int(dirty[col,field])==1
    delta=np.argwhere(z['initial_probe_clean']!=z['initial_probe_faulty']);assert len(delta)==6
    for row,field in delta:
        assert f.SCHEMA[int(field)][0].endswith('_data')
        assert int(z['initial_probe_clean'][row,field])^int(z['initial_probe_faulty'][row,field])==1
    initial_cone=probe(z['initial_probe_positions'],z['initial_probe_clean'],z['initial_probe_faulty'],z['initial_probe_after_one_tick'],n*f.Q,healed=False)
    late_cone=probe(z['late_probe_positions'],z['late_probe_before'],z['late_probe_faulty'],z['late_probe_after_one_tick'],n*f.Q,healed=True)
    assert late_cone['changed_input_sites']==2
    for _,field in np.argwhere(z['late_probe_before']!=z['late_probe_faulty']):
        name=f.SCHEMA[int(field)][0];assert name.startswith('s') and '_' in name and name.split('_',1)[1] in dict(f.PROCEDURE)
    for epoch in (1,2):
        saved=state(z,f'boundary_{epoch}_',n,epoch*f.U)
        np.testing.assert_array_equal(saved['bank'][:,list(p.layout().info)],expected[epoch-1])
        full=old[f'physical_boundary_{epoch}_Data'];bank=np.concatenate((full[:,:p.layout().memory_count],full[:,f.Q-5:]),axis=1)
        np.testing.assert_array_equal(saved['bank'],bank)
        assert not np.any(saved['flags'])
        for col,count in enumerate(saved['counts']):
            rows=saved['active_rows'][col,:int(count)]
            assert not np.any(rows[:,[q.COL[name] for name in period.ACTIVE if name!='signal']])
        np.testing.assert_array_equal(saved['signals'][:,0],expected[epoch-1,:,f.COL['f2']])
        np.testing.assert_array_equal(saved['signals'][:,1],expected[epoch-1,:,f.COL['f1']])
    assert not np.array_equal(z['boundary_1_bank'],z['healthy_boundary_1_bank'])
    for a,b,time_ in (('rejoin_actual_','rejoin_healthy_',f.U+1),('boundary_2_','healthy_boundary_2_',2*f.U)):
        damaged=state(z,a,n,time_);healthy=state(z,b,n,time_)
        for name in damaged:np.testing.assert_array_equal(damaged[name],healthy[name],err_msg='complete rejoin '+name)
    rejoin=old['healthy_rejoin_Data'];np.testing.assert_array_equal(z['rejoin_actual_bank'],np.concatenate((rejoin[:,:p.layout().memory_count],rejoin[:,f.Q-5:]),axis=1))
    fields=[f.COL[f's{k}_{name}'] for k in range(5) for name in ('head',*c.CONTROL)]
    changed=[int(np.count_nonzero(a[:,fields]!=b[:,fields])) for a,b in ((initial,first),(first,second))]
    assert all(changed)
    return dict(initial_physical_cone=initial_cone,late_physical_cone=late_cone,encoded_two_copy_repair_matches=True,three_copy_negative_control_differs=True,complete_raw_words_per_macrostep=n*f.FIELDS,represented_controller_words_changed=changed,all_saved_physical_rejoin_fields_match=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
    path=Path(args.input);out=Path(args.output)
    if out.exists():raise FileExistsError(out)
    start=time.perf_counter();receipt=json.loads(path.read_text());assert receipt['passed']
    assert receipt['physical_ticks']==receipt['healthy_reference_ticks']==2*f.U
    assert receipt['complete_physical_rejoin_time']==f.U+1
    assert receipt['descriptor_sha256']==f.self_description().digest()
    assert receipt['rom_sha256']==hashlib.sha256(p.base_rom().tobytes()).hexdigest()
    for name,digest in {**receipt['source_sha256'],**receipt['binaries']}.items():assert sha(name)==digest,name
    assert sha(path.with_suffix('.npz'))==receipt['artifact_sha256']
    reference=Path(receipt['reference']);assert sha(reference)==receipt['reference_sha256']
    assert sha(reference.with_suffix('.npz'))==receipt['reference_artifact_sha256']
    with np.load(path.with_suffix('.npz'),allow_pickle=False) as z,np.load(reference.with_suffix('.npz'),allow_pickle=False) as old:result=validate(z,old)
    result.update(passed=True,input=str(path),input_sha256=sha(path),seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
