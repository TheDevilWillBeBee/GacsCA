"""Build only private retimed CUDA libraries; no device allocation or evolution."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time
from gacsca.fixed_rule import retimed_holder_resident_period as period
from gacsca.fixed_rule import retimed_holder_resident_independent as independent


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args()
    output=Path(args.output)
    if output.exists():raise FileExistsError(output)
    started=time.perf_counter();result={'passed':False,'libraries':[]}
    try:
        for module in (period,independent):
            tick=time.perf_counter();lib=module.library();binary=Path(lib._name)
            result['libraries'].append(dict(module=module.__name__,binary=str(binary),sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),seconds=time.perf_counter()-tick))
            print(json.dumps(result['libraries'][-1]),flush=True)
        result['passed']=True
    finally:
        result.update(seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,children_max_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)
        output.write_text(json.dumps(result,indent=2)+'\n')

if __name__=='__main__':main()
