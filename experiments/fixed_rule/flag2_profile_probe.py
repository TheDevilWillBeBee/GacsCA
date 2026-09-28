"""Bounded, exact one-sided Flag2 profile probe; no constant-speed assumption."""
import argparse
import hashlib
import json
from pathlib import Path
import time
from gacsca.fixed_rule.flag2_bits import Flag2Bits,Q


def execute(output):
    output=Path(output)
    if output.exists():raise FileExistsError('preserve evidence')
    start=time.monotonic();world=Flag2Bits(age=96*Q+1);records=[]
    for tick in (1,2,4,8,16,32,64,128,256,512,1024,2048,4096,8192,16384,32768,65536):
        world.run(tick-world.time)
        records.append(dict(tick=tick,age=world.age,support_end=world.bits.bit_length()-1,count=world.bits.bit_count(),bits_hex=hex(world.bits)))
    root=Path(__file__).resolve().parents[2]
    files=[Path(__file__).resolve(),root/'gacsca/fixed_rule/flag2_bits.py',root/'gacsca/fixed_rule/delivery_rule.py',root/'tests/fixed_rule/test_flag2_bits.py']
    result=dict(scope=__doc__,physical_colony_Q=Q,elapsed_seconds=time.monotonic()-start,records=records,
                limitation='no Flag1, no right signal; 65536 ticks, not full 2Q window; powers-of-two samples hide intermediate holes',
                source_sha256={str(path.relative_to(root)):hashlib.sha256(path.read_bytes()).hexdigest() for path in files})
    output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ('records','source_sha256')},indent=2))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True,type=Path);execute(parser.parse_args().output)
