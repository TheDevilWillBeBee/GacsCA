"""Algebraic device-space accounting; never allocate larger GPU states."""
import argparse,hashlib,json
from pathlib import Path
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_program as p
from gacsca.fixed_rule import retimed_holder_resident_period as resident,retimed_holder_packed as packed


def account():
    header=resident.header()
    macro={line.split()[1]:int(line.split('UINT64_C(')[1].split(')')[0]) for line in header.splitlines() if line.startswith('#define ') and 'UINT64_C(' in line}
    temp=int(next(line.split()[-1] for line in header.splitlines() if line.startswith('#define TEMP_WORDS ')))
    workspace=(12*macro['FIELDS']+temp)*resident.WORKERS
    g=p.layout();bank=g.memory_count+5
    per=8*(bank+2*resident.SLOTS*packed.WORDS+1+resident.CANDIDATES*(1+packed.WORDS)+3)
    fixed=8*(g.computation_cells*7+workspace+resident.CHUNK*f.FIELDS+resident.MAX_READ*(1+packed.WORDS))
    staged=8*(bank+32*6+1)
    measured=json.loads(Path('figs/fixed_rule/retimed_holder_cuda_periods15_v1.json').read_text())
    assert fixed+15*per==measured['base_device_bytes'] and 15*staged==measured['metrics']['extra_device_bytes']
    rows=[]
    for top in (1,15):
        for depth in (1,2,3):
            colonies=top*f.Q**(depth-1);base=fixed+colonies*per;extra=colonies*staged
            rows.append(dict(top_cells=top,encoded_depth=depth,physical_colonies=colonies,physical_sites=colonies*f.Q,explicit_base_bytes=base,explicit_staging_bytes=extra,explicit_peak_bytes=base+extra,explicit_peak_GiB=(base+extra)/2**30,within_A100_80GiB=base+extra<=80*2**30,within_current_API_caps=colonies<=2**20 and base<=8*2**30 and extra<=8*2**30,physical_ticks_per_top_step=f.U**depth))
    return dict(passed=True,description_sha256=f.self_description().digest(),header_sha256=hashlib.sha256(header.encode()).hexdigest(),fixed_device_bytes=fixed,device_bytes_per_colony=per,staged_bytes_per_colony=staged,rows=rows,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),scope='Algebraic extrapolation only; no larger allocation/execution. CUDA overhead, other jobs and API guard limits are additional constraints. No runtime extrapolation is asserted.')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError(out)
    result=account();out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
