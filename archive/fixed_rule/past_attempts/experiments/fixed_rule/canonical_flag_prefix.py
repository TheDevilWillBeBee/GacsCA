"""Bounded physical flag-projection prefixes; no source signal initiator yet."""
import argparse
import hashlib
import json
from pathlib import Path
import time
from gacsca.fixed_rule import clock_rule as f
from gacsca.fixed_rule.canonical_flag_world import FlagProjection
from gacsca.fixed_rule.canonical_clock_description import build


def execute(output):
    output=Path(output)
    if output.exists():raise FileExistsError('preserve prior evidence')
    cases={'right_wf1':{p:4 for p in range(f.Q-5,f.Q)},
           'both_edges':dict({p:4 for p in range(f.Q-5,f.Q)},**{}) ,
           'printed_flag2_singleton':{100:2}}
    cases['both_edges'].update({p:8 for p in range(5)})
    started=time.monotonic();records={}
    for name,initial in cases.items():
        world=FlagProjection(initial,age=96*f.Q+1);frames=[]
        for tick in (0,1,2,4,8,16,32,64,128,256):
            world.run(tick-world.time)
            frames.append(dict(tick=tick,age=world.age,evaluations=world.evaluations,
                               flags=[sum(bool(value&(1<<bit)) for value in world.states.values()) for bit in range(4)],
                               states=sorted(world.states.items())))
        records[name]=frames
    root=Path(__file__).resolve().parents[2]
    files=[Path(__file__).resolve(),*[root/'gacsca/fixed_rule'/name for name in ('canonical_flags.py','canonical_clock_description.py','canonical_clock_native.py','canonical_flag_world.py','clock_rule.py','clock_description.py','word_rule.py','word_description.py','wordcode.py')],*[root/'tests/fixed_rule'/name for name in ('test_canonical_flags.py','test_canonical_clock.py','test_canonical_flag_world.py')]]
    result=dict(scope='closed physical four-flag projection of current clock rule on canonical geometry; short manually seeded prefixes, no self-simulation/noise-robustness claim',
                Q=f.Q,U=f.U,physical_sites=f.Q,complete_rule_description=f.self_description().digest(),canonical_kernel=build().digest(),
                elapsed_seconds=time.monotonic()-started,records=records,source_sha256={str(path.relative_to(root)):hashlib.sha256(path.read_bytes()).hexdigest() for path in files})
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(elapsed_seconds=result['elapsed_seconds'],final={name:{k:v for k,v in rows[-1].items() if k!='states'} for name,rows in records.items()}),indent=2))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();execute(args.output)
