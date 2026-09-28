"""Independent saved full-period GPU/CPU state and self-simulation audit."""
import argparse,hashlib,json,resource,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_projected as r
from gacsca.fixed_rule import retimed_holder_program as p,retimed_holder_quotient as q
from gacsca.fixed_rule import retimed_holder_packed as packed,retimed_holder_resident_period as resident


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def validate(data,cpu,periods):
    g=p.layout();initial=data['initial_upper'];n=len(initial)
    np.testing.assert_array_equal(initial,cpu['initial_upper'])
    shapes={'initial_bank':(n,g.memory_count+5),'boundary_banks':(periods,n,g.memory_count+5),
            'boundary_sparse':(periods,n,resident.SLOTS,packed.WORDS),'boundary_counts':(periods,n),'boundary_right':(periods,n)}
    for name,shape in shapes.items():assert data[name].shape==shape and data[name].dtype==np.uint64,name
    upper=tuple(r.decode_cell(row) for row in initial);known=np.zeros_like(data['initial_bank'])
    for col,cell in enumerate(upper):known[col,list(g.info)]=f.encode_cell(r.lift(cell))
    np.testing.assert_array_equal(data['initial_bank'],known)
    program=f.self_description();result=[]
    for epoch in range(periods):
        physical=cpu['boundary_data'][epoch]
        assert not np.any(physical[:,g.memory_count:f.Q-5])
        bank=np.concatenate((physical[:,:g.memory_count],physical[:,f.Q-5:]),axis=1)
        np.testing.assert_array_equal(data['boundary_banks'][epoch],bank)
        right=data['boundary_right'][epoch]
        np.testing.assert_array_equal(right,cpu['boundary_right'][epoch]);assert np.all(right<=1)
        for col,count in enumerate(data['boundary_counts'][epoch]):
            assert int(count)==5*int(right[col]),'residual or missing Signal/controller/mail record'
            rows=packed.unpack(data['boundary_sparse'][epoch,col,:int(count)])
            for offset,row in enumerate(rows):
                assert row[q.COL['address']]==f.Q-5+offset
                for name in resident.ACTIVE:
                    expected=1<<(4-offset) if name=='signal' else 0
                    assert row[q.COL[name]]==expected,(epoch,col,name)
        raw=tuple(r.lift(cell) for cell in upper);next_upper=[]
        for col in range(n):
            neighbors=tuple(raw[(col+j)%n] for j in f.NEIGHBORHOOD)
            scalar=f.local_step(neighbors)
            described=f.decode_cell(program.evaluate(tuple(word for cell in neighbors for word in f.encode_cell(cell))))
            assert scalar==described
            parent=r.project(scalar);words=tuple(map(int,bank[col,list(g.info)]))
            assert words==f.encode_cell(r.lift(parent)),'raw Info or represented controller differs'
            next_upper.append(parent)
        controls=[i for i,(name,_) in enumerate(r.SCHEMA) if any(name.endswith('_'+field) for field in ('head','phase','pc','ra','rb','rd','value','alu','direction'))]
        changed=sum(r.encode_cell(a)[i]!=r.encode_cell(b)[i] for a,b in zip(upper,next_upper) for i in controls)
        upper=tuple(next_upper)
        result.append(dict(period=epoch+1,complete_Data_controllers_mail_Signals_match=True,all_raw_Info_matches_scalar_and_descriptor=True,changed_upper_controller_words=changed,decoded_sha256=hashlib.sha256(np.array([r.encode_cell(cell) for cell in upper],dtype=np.uint64).tobytes()).hexdigest()))
    return dict(colonies=n,periods=periods,period_results=result,complete_raw_words_per_commit=n*f.FIELDS)


def main():
 parser=argparse.ArgumentParser();parser.add_argument('--input',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
 path=Path(args.input);out=Path(args.output)
 if out.exists():raise FileExistsError(out)
 start=time.perf_counter();receipt=json.loads(path.read_text());reference=Path(receipt['reference']);cpu_receipt=json.loads(reference.read_text())
 assert receipt['passed'] and receipt['physical_ticks']==receipt['periods']*f.U
 assert receipt['initial_histories_zero'] and receipt['one_retained_physical_state']
 assert sha(reference)==receipt['reference_sha256'] and sha(reference.with_suffix('.npz'))==receipt['reference_artifact_sha256']
 assert sha(path.with_suffix('.npz'))==receipt['artifact_sha256']
 assert receipt['descriptor_sha256']==f.self_description().digest() and receipt['rom_sha256']==hashlib.sha256(p.base_rom().tobytes()).hexdigest()
 for name,digest in {**receipt['source_sha256'],**receipt['binaries']}.items():assert sha(name)==digest,name
 with np.load(path.with_suffix('.npz'),allow_pickle=False) as data,np.load(reference.with_suffix('.npz'),allow_pickle=False) as cpu:
  result=validate(data,cpu,receipt['periods'])
 for epoch,row in enumerate(result['period_results']):
  assert row['decoded_sha256']==cpu_receipt['period_results'][epoch]['decoded_sha256']
  assert cpu_receipt['period_results'][epoch]['full_entry_relation']['validated_sites']==receipt['colonies']*f.Q
 result.update(passed=True,input=str(path),input_sha256=sha(path),seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
 out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)
if __name__=='__main__':main()
