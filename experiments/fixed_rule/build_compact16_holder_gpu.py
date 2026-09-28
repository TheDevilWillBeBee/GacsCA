"""Build private compact GPU libraries without device allocation or evolution."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time
from gacsca.fixed_rule import compact16_holder_resident_period as period
from gacsca.fixed_rule import compact16_holder_resident_independent as independent
from gacsca.fixed_rule import compact16_holder_resident_mixed as mixed
from gacsca.fixed_rule import compact16_holder_resident_gather as gather
from gacsca.fixed_rule import compact16_holder_resident_general as general
from gacsca.fixed_rule import compact16_holder_flags_gpu as flags


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        raise FileExistsError(args.output)
    start = time.perf_counter()
    result = dict(passed=False, libraries=[])
    try:
        for module in (period, independent, mixed, gather, general, flags):
            tick = time.perf_counter()
            lib = module.library()
            binary = Path(lib._name)
            row = dict(module=module.__name__, binary=str(binary),
                       sha256=hashlib.sha256(binary.read_bytes()).hexdigest(),
                       seconds=time.perf_counter()-tick)
            result['libraries'].append(row)
            print(json.dumps(row), flush=True)
        result['passed'] = True
    finally:
        result.update(seconds=time.perf_counter()-start,
                      host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                      children_max_rss_kib=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,
                      GPU_evolution=False)
        with args.output.open('x') as stream:
            stream.write(json.dumps(result, indent=2)+'\n')


if __name__ == '__main__':
    main()
