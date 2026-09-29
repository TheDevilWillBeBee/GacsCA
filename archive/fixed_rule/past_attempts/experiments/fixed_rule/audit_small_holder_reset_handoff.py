"""Independent clean-boundary hashes, decoded transitions and reset proof audit."""
import argparse,hashlib,json,resource,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import small_holder_rule as f,small_holder_core as c,small_holder_projected as r
from gacsca.fixed_rule import small_holder_native as native,small_holder_program as p,small_holder_quotient as q
from gacsca.fixed_rule.wordcode import LIT
from experiments.fixed_rule.prove_small_holder_reset_encoding import prove


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def clean_hash(parents,left=None,right=None):
    """Independent dense-per-colony construction; at most 6.25 MiB staging."""
    digest=hashlib.sha256();g=p.layout();addresses=np.arange(f.Q,dtype=np.uint64)
    for i,parent in enumerate(parents):
        rows=np.zeros((f.Q,len(q.SCHEMA)),dtype=np.uint64)
        rows[:,q.COL['address']]=addresses;rows[:,q.COL['age']]=1
        rows[0,q.COL['head']]=1;rows[0,q.COL['pc']]=g.entries[0]
        rows[np.array(g.info),q.COL['data']]=f.encode_cell(r.lift(parent))
        bits=np.array([16,8,4,2,1],dtype=np.uint64)
        rows[1:6,q.COL['signal']]=bits*(parent.f2 if left is None else left[i])
        rows[-5:,q.COL['signal']]=bits*(parent.f1 if right is None else right[i])
        digest.update(rows.tobytes())
    return digest.hexdigest()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input',required=True);parser.add_argument('--proof',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
    stem=Path(args.input);out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();manifest=json.loads(stem.with_suffix('.json').read_text());certificate=json.loads(Path(args.proof).read_text())
    assert manifest['passed'] and certificate['passed']
    assert sha('experiments/fixed_rule/prove_small_holder_reset_encoding.py')==certificate['source_sha256']
    for path,wanted in manifest['source_sha256'].items():assert sha(path)==wanted,path
    assert sha(stem.with_suffix('.npz'))==manifest['artifact_sha256']
    result_proof=prove();desc=f.self_description()
    assert result_proof['descriptor_sha256']==manifest['physical_descriptor_sha256']
    # Verify that the proof did not fix any actually referenced exterior static
    # word or logical Data input outside its quantified -4..4 support to zero.
    used={w for op,a,b in desc.operations if op!=LIT for w in (a,b) if w<desc.inputs}
    used.update(w for w in desc.outputs if w<desc.inputs)
    for wire in used:
        offset,field=divmod(wire,f.FIELDS);offset-=7;name=f.SCHEMA[field][0]
        if field<len(f.STATIC):assert offset==0
        if name.startswith('s') and name.endswith('_data'):assert -4<=offset+int(name[1])-2<=4
    # Exhaustively instantiate reset marker assumptions using every fixed ROM or
    # fallback address. Only Info survives among actual MEM Data cells.
    retained=[];first=[]
    for address in range(f.Q):
        record=r.record(address)
        if record['first']:first.append(address)
        if record['kind']==c.MEM and not record['first'] and not (record['a']&1):retained.append(address)
    assert retained==list(p.layout().info) and first==[0]
    assert r.record(0)['a']&((1<<32)-1)==p.layout().entries[0]
    upper_outputs=0;probe_outputs=0
    with np.load(stem.with_suffix('.npz'),allow_pickle=False) as archive:
        parents=tuple(r.project(x) for x in native.cells_from_array(archive['initial']))
        assert clean_hash(parents,archive['initial_left'],archive['initial_right'])==manifest['initial']['sha256']
        for which,checkpoint in enumerate(manifest['checkpoints'],1):
            raw=tuple(r.lift(x) for x in parents);updated=[]
            for i in range(len(parents)):
                neighborhood=tuple(raw[(i+j)%len(raw)] for j in f.NEIGHBORHOOD)
                a=f.local_step(neighborhood);b=native.local_step(neighborhood)
                expression=f.decode_cell(desc.evaluate(tuple(x for cell in neighborhood for x in f.encode_cell(cell))))
                assert a==b==expression;updated.append(r.project(a));upper_outputs+=1
            parents=tuple(updated)
            np.testing.assert_array_equal(archive[f'decoded{which}'],native.array_from_cells(tuple(r.lift(x) for x in parents)))
            assert clean_hash(parents)==checkpoint['after_reset']['sha256']
            assert checkpoint['after_reset']['coherent_rows_checked']==15*f.Q
            assert checkpoint['before_reset']['coherent_rows_checked']==15*f.Q
            assert checkpoint['physical_time']==which*f.U
            for before,after in zip(native.cells_from_array(archive[f'before_reset{which}']),native.cells_from_array(archive[f'after_reset{which}'])):
                changes=dict(age=1)
                assert before.age==0 and before.f1==before.f2==0
                for d in f.OFFSETS:
                    prefix=f'p{d+3}_';first=getattr(before,prefix+'first');kind=getattr(before,prefix+'kind');a=getattr(before,prefix+'a')
                    for name,_ in f.PROCEDURE:changes[f's{d+2}_{name}']=0
                    changes[f's{d+2}_data']=0 if first or (kind==c.MEM and a&1) else getattr(before,f's{d+2}_data')
                    changes[f's{d+2}_head']=first;changes[f's{d+2}_pc']=(a&((1<<32)-1)) if first else 0
                from dataclasses import replace
                assert replace(before,**changes)==after;probe_outputs+=1
    result=dict(passed=True,reset_identity_reproved=True,all_ROM_and_fallback_addresses_checked=f.Q,only_Info_MEM_survives_reset=True,exterior_static_and_Data_support_checked=True,complete_decoded_upper_outputs_checked=upper_outputs,full_raw_reset_probes_checked=probe_outputs,complete_clean_row_hashes_rebuilt=3,coherent_rows_per_hash=15*f.Q,source_sha256=sha(__file__),input_manifest_sha256=sha(stem.with_suffix('.json')),proof_manifest_sha256=sha(args.proof),artifact_sha256=sha(stem.with_suffix('.npz')),seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,limitation='Independent boundary reconstruction and saved decoded/probe audit; pre-reset whole-state hypotheses are runtime checks in the hashed driver. Does not prove all-input whole-period closure or independently replay full lower trajectories.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
