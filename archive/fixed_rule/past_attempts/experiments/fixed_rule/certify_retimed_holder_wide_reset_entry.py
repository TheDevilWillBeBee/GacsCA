"""Bind the normalized diagnostic twin to a literal reset of a valid entry.

Together with the physical normalization coupling and the retained-Data
commutation certificate, this discharges the entry-domain issue for the actual
saved contextual trajectory. No generated reference is installed into a run.
"""
import argparse
import json
from pathlib import Path
import resource
import time
import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_projected as r
from gacsca.fixed_rule import retimed_holder_wide_inert_storage as storage
from gacsca.fixed_rule import retimed_holder_global_events as events
from gacsca.fixed_rule import retimed_holder_literal_cone as cone,retimed_holder_program as p
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--input',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();path,out=Path(args.input),Path(args.output)
    if out.exists():raise FileExistsError(out)
    started=time.perf_counter();run=json.loads(path.read_text())
    assert run['completed'] and run['error'] is None
    assert sha(path.with_suffix('.npz'))==run['artifact_sha256']
    proof=storage.certificate()
    with np.load(path.with_suffix('.npz'),allow_pickle=False) as z:
        fields=('bank','active_rows','counts','flags','signals','age','time')
        state={k:z['initial_normalized_'+k] for k in fields}
        pos,values=z['retained_positions'],z['retained_values']
        assert set((pos%f.Q).tolist())<=set(proof['selected_addresses'])
        parents=tuple(r.project(f.decode_cell(row)) for row in z['decoded_before'])
        expected=np.array([f.encode_cell(r.lift(cell)) for cell in parents],dtype=np.uint64)
        np.testing.assert_array_equal(state['bank'][:,p.layout().info],expected)
        # BankImage is an E entry: fixed physical ROM/canonical geometry, Age0,
        # complete iota(parent) Info, arbitrary MEM scratch, no controller/mail/
        # flags/Wf, zero nonMEM Data and coherent localized Signals.
        image=cone.BankImage(state['bank'],state['signals'],age=0)
        size=len(parents)*f.Q
        def entry(sites):
            sites=np.asarray(sites,dtype=np.int64)%size
            raw=image.cells(sites)
            for a,value in zip(pos,values):
                for d in f.OFFSETS:
                    raw[sites==(int(a)-d)%size,f.COL[f's{d+2}_data']]=value
            return raw
        world=events.World(entry,size=size,time=f.U)
        assert not world.heads
        world.advance(1)
        twin=storage.View(state,pos,values)
        for start in range(0,size,f.Q):
            sites=np.arange(start,start+f.Q)
            np.testing.assert_array_equal(world.cells(sites),twin.cells(sites))
        assert world.time==int(state['time'])==f.U+1
        assert world.heads==tuple(range(0,size,f.Q))
    sources=(Path(__file__),Path(storage.__file__),Path(events.__file__),Path(cone.__file__),Path(f.__file__),Path(r.__file__))
    result=dict(passed=True,valid_encoded_entry_modulo_certified_retained_Data=True,literal_global_G_reset_steps=1,complete_raw_words_verified=size*f.FIELDS,normalized_twin_is_exact_reset_image=True,Info_is_complete_hardwired_parent_encoding=True,retained_Data_words=len(pos),source_receipt_sha256=sha(path),artifact_sha256=run['artifact_sha256'],source_sha256={str(x):sha(x) for x in sources},seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,scope='Specific normalized comparison state is G of a valid E entry with the proven inert Data overlay. Combined with audited physical prefix coupling, the existing conditional macrostep/terminal relation applies to this actual trajectory. Not a general arbitrary-corruption entry theorem.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
