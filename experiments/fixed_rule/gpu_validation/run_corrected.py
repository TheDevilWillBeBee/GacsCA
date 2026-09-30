"""Run the same physical F with corrected WordCode and corrected own-ROM data."""
import argparse
import hashlib
import json
from pathlib import Path

from gacsca.fixed_rule import stream28_dual_pass20 as physical
from gacsca.fixed_rule.gpu_validation import corrected_circuit, dense_corrected, description
from . import run as base


def run(colonies, periods, stop_tick, seed, output, snapshots=False):
    if output.exists():raise FileExistsError(output)
    metadata=output.with_name(output.stem+'_identity.json')
    if metadata.exists():raise FileExistsError(metadata)
    identity=dict(physical_rule='stream28_dual_pass20.local_step',
        corrected_description_sha256=description.build().digest(),
        corrected_circuit_source_sha256=hashlib.sha256(
            Path(corrected_circuit.__file__).read_bytes()).hexdigest(),
        wrapper_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        clock_source_sha256=hashlib.sha256(
            Path(description.__file__).with_name('clock_description.py').read_bytes()).hexdigest(),
        scope='Initial-data compilation only; dense.World runs all physical ticks.')
    metadata.write_text(json.dumps(identity,indent=2)+'\n')
    old_dense,old_description=base.dense,base.description
    try:
        base.dense,base.description=dense_corrected,description
        with corrected_circuit.corrected_initial_data():
            return base.run(colonies,periods,stop_tick,seed,output,snapshots)
    finally:
        base.dense,base.description=old_dense,old_description


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--colonies',type=int,default=31)
    parser.add_argument('--periods',type=int,default=1)
    parser.add_argument('--stop-tick',type=int)
    parser.add_argument('--seed',type=int,default=20260929)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--snapshots',action='store_true')
    args=parser.parse_args()
    stop=args.stop_tick if args.stop_tick is not None else args.periods*physical.U
    if args.periods not in (1,2) or not 0<=stop<=args.periods*physical.U:
        parser.error('one or two bounded periods required')
    print(json.dumps(run(args.colonies,args.periods,stop,args.seed,
                         args.output,args.snapshots),indent=2))
