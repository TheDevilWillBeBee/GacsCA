"""Private build of mixed-right and gather CUDA adapters; no GPU evolution."""
import argparse,hashlib,json,resource,time
from pathlib import Path
from gacsca.fixed_rule import retimed_holder_resident_mixed as mixed,retimed_holder_resident_gather as gather

def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
 if out.exists():raise FileExistsError(out)
 start=time.perf_counter();result=dict(passed=False,libraries=[])
 try:
  for module in (mixed,gather):
   tick=time.perf_counter();lib=module.library();binary=Path(lib._name)
   result['libraries'].append(dict(module=module.__name__,binary=str(binary),sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),seconds=time.perf_counter()-tick))
   print(json.dumps(result['libraries'][-1]),flush=True)
  result['passed']=True
 finally:
  result.update(seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,children_max_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss)
  out.write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
