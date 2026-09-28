"""Physical capture -> preserved redundant signals -> Wf -> short flag waves.

Locally initialized Data stands in for the NOT YET IMPLEMENTED delivery of
computed upper flags. No simulated dynamics or robustness claim is made.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time
from gacsca.fixed_rule import signal_rule as r,signal_native as native
from gacsca.fixed_rule.signal_world import SignalWorld


def execute(output):
    output=Path(output)
    if output.exists():raise FileExistsError('preserve prior evidence')
    started=time.monotonic();records={};lib=native.library()
    for name,targets in (('right_signal',(r.Q-3,)),('both_signals',(3,r.Q-3))):
        data={target+e:1 for target in targets for e in range(-2,3)}
        world=SignalWorld({},data=data,age=r.CAPTURE_AGE-2);frames=[]
        def save(label):
            frames.append(dict(label=label,tick=world.time,age=world.age,evaluations=world.evaluations,quiet_ticks=world.quiet_ticks,
                               flags=[sum(bool(v&(1<<b)) for v in world.states.values()) for b in range(4)],states=sorted(world.states.items())))
        save('initial_local_payload');world.run(2);save('captured')
        before=world.age;world.skip_quiet(96*r.Q-1-world.age);save('before_Wf_window')
        for tick in (1,2,4,8,16,32,64,128,256):
            current=world.age-(96*r.Q-1);world.run(tick-current);save('window_prefix_'+str(tick))
        records[name]=dict(data=sorted(data.items()),quiet_age_interval=[before,96*r.Q-1],frames=frames)
    root=Path(__file__).resolve().parents[2]
    files=[Path(__file__).resolve(),*[root/'gacsca/fixed_rule'/name for name in ('signal_rule.py','signal_description.py','signal_native.py','signal_world.py','canonical_flag_world.py','clock_rule.py','clock_description.py','word_rule.py','word_description.py','wordcode.py')],*[root/'tests/fixed_rule'/name for name in ('test_signal_rule.py','test_signal_world.py')]]
    result=dict(scope=__doc__,identity=r.identity(),operations=len(r.self_description().operations),physical_sites=r.Q,
                elapsed_seconds=time.monotonic()-started,records=records,binary_sha256=hashlib.sha256(Path(lib._name).read_bytes()).hexdigest(),
                source_sha256={str(path.relative_to(root)):hashlib.sha256(path.read_bytes()).hexdigest() for path in files})
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(elapsed_seconds=result['elapsed_seconds'],operations=result['operations'],final={name:{k:v for k,v in x['frames'][-1].items() if k!='states'} for name,x in records.items()}),indent=2))
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,required=True)
    execute(parser.parse_args().output)
