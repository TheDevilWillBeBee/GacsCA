"""Literal execution of one fixed constant-ROM regenerated self-simulator.

Every macrostep includes locally executed full program-record regeneration.
The fixed Address restriction is intentional and recorded. This is not yet a
Gray/Gacs colony-maintenance or error-correction result.
"""
import argparse
import hashlib
import json
from pathlib import Path
import tarfile
import time
import numpy as np
from gacsca.fixed_rule import regenerated as rule,regenerative,regenerative_block
from gacsca.fixed_rule.regenerated_native import library,run
from gacsca.fixed_rule.regenerated_initial import resource_estimate


def initial_ring():
    g=regenerative_block.layout()
    pc,op=next((i,op) for i,op in enumerate(g.instructions)
               if i>=2*regenerative.WIDTH+2 and op.kind==regenerative.GATE and op.a!=op.b and min(op.a,op.b)>1)
    return (rule.Cell(address=op.a,bit=1,head=1,phase=regenerative.READ_B,
                      rb=op.a,rd=op.b,value=1,pc=pc-1),
            rule.Cell(address=op.b,bit=1),rule.Cell(address=g.memory_count+pc),
            rule.Cell(address=op.d,rp_target=op.a,rp_bit=0,rp_cross=1,rp_valid=1))


def lifted_bits(physical):
    g=regenerative_block.layout()
    return np.stack([physical[base+g.info_start:base+g.info_start+regenerative.WIDTH,rule.COL['bit']]
                     for base in range(0,len(physical),g.colony_cells)]).astype(np.uint8)


def execute(output,steps=8):
    output=Path(output)
    output.parent.mkdir(parents=True,exist_ok=True)
    paths=[output.with_suffix(suffix) for suffix in ('.json','.npz','.tar.gz')]
    if any(path.exists() for path in paths):
        raise FileExistsError('existing evidence must be preserved')
    if steps<8:
        raise ValueError('at least eight steps required for the active NAND trajectory')
    root=Path(__file__).resolve().parents[2]
    sources=sorted([*root.glob('gacsca/fixed_rule/*.py'),*root.glob('gacsca/fixed_rule/*.c'),
                    *root.glob('tests/fixed_rule/*.py'),*root.glob('experiments/fixed_rule/*.py')])
    hashes={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}
    reference=initial_ring()
    physical=rule.encode(reference)
    g=regenerative_block.layout()
    lib=library()
    frames=[np.array([rule.encode_cell(cell) for cell in reference],dtype=np.uint8)]
    expanded=[lifted_bits(physical)]
    logs=[]
    for period in range(1,steps+1):
        start=time.monotonic()
        metrics=run(physical,g.period_ticks,lib)
        metrics['elapsed_seconds']=time.monotonic()-start
        reference=rule.step_ring(reference)  # diagnostic only; never installed
        actual=rule.decode(physical)
        bits=np.array([rule.encode_cell(cell) for cell in actual],dtype=np.uint8)
        expected=np.array([rule.encode_cell(cell) for cell in reference],dtype=np.uint8)
        raw_mismatches=int(np.count_nonzero(bits!=expected))
        full=lifted_bits(physical)
        expected_full=np.array([regenerative.encode_cell(rule.lift(cell)) for cell in reference],dtype=np.uint8)
        full_mismatches=int(np.count_nonzero(full!=expected_full))
        boundary=rule.check_boundary(physical)
        row=dict(period=period,**metrics,raw_bit_mismatches=raw_mismatches,
                 lifted_raw_bit_mismatches=full_mismatches,admissible_boundary=boundary,
                 memory=[actual[1].bit,actual[3].bit])
        print(json.dumps(row),flush=True)
        if raw_mismatches or full_mismatches or not boundary:
            raise AssertionError(row)
        logs.append(row)
        frames.append(bits)
        expanded.append(full)
    with tarfile.open(paths[2],'x:gz') as archive:
        for name in hashes:
            archive.add(root/name,arcname=name)
    with paths[1].open('xb') as stream:
        np.savez_compressed(stream,frames=np.stack(frames),lifted_frames=np.stack(expanded),
                            physical_final=physical,rom=rule.rom())
    data=dict(schema=1,scope='complete-controller self-simulation with local program regeneration; static Address, no Gray/Gacs maintenance',
              fixed_rule=rule.identity(),colony_cells=g.colony_cells,physical_cells=len(physical),
              instructions=len(g.instructions),description_gates=len(regenerative.self_description().gates),
              timing=g.timing_certificate(),rom_bytes=rule.rom().nbytes,
              compiled_binary_sha256=hashlib.sha256(Path(lib._name).read_bytes()).hexdigest(),
              periods=logs,total_ticks=sum(row['physical_ticks'] for row in logs),
              total_seconds=sum(row['elapsed_seconds'] for row in logs),
              executed_regenerated_computing_links=1,executed_gray_gacs_levels=0,
              initialization_only_depth_estimates=[resource_estimate(1,d) for d in (1,2,3)],
              source_sha256=hashes,artifact_sha256=hashlib.sha256(paths[1].read_bytes()).hexdigest(),
              source_archive_sha256=hashlib.sha256(paths[2].read_bytes()).hexdigest())
    with paths[0].open('x') as stream:
        json.dump(data,stream,indent=2)
        stream.write('\n')
    return data


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    parser.add_argument('--steps',default=8,type=int)
    args=parser.parse_args()
    execute(args.output,args.steps)
