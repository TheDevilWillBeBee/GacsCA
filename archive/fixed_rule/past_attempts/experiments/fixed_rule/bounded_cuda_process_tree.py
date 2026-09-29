"""Bound one owned CUDA sanitizer process family by wall time and sampled RSS."""
import argparse,json,os,signal,subprocess,time
from pathlib import Path


def family_rss(pid):
    pending=[pid];seen=set();total=0
    while pending:
        current=pending.pop()
        if current in seen:continue
        seen.add(current)
        try:
            status=Path(f'/proc/{current}/status').read_text()
            total+=next((int(line.split()[1]) for line in status.splitlines() if line.startswith('VmRSS:')),0)
            pending.extend(map(int,Path(f'/proc/{current}/task/{current}/children').read_text().split()))
        except (FileNotFoundError,ProcessLookupError):pass
    return total


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);parser.add_argument('--seconds',type=float,default=60)
    parser.add_argument('--rss-mib',type=int,default=512);parser.add_argument('command',nargs=argparse.REMAINDER);args=parser.parse_args()
    out=Path(args.output)
    if out.exists():raise FileExistsError(out)
    command=args.command[1:] if args.command and args.command[0]=='--' else args.command
    if not command:raise ValueError('owned command required')
    start=time.monotonic();child=subprocess.Popen(command,start_new_session=True,env={**os.environ,'OPENBLAS_NUM_THREADS':'1'})
    peak=0;reason=None
    try:
        while child.poll() is None:
            peak=max(peak,family_rss(child.pid))
            if peak>args.rss_mib*1024:reason='aggregate sampled RSS threshold exceeded'
            elif time.monotonic()-start>args.seconds:reason='wall-time limit exceeded'
            if reason:os.killpg(child.pid,signal.SIGKILL);break
            time.sleep(.02)
        code=child.wait()
    finally:
        if child.poll() is None:os.killpg(child.pid,signal.SIGKILL);child.wait()
        result=dict(command=command,pid=child.pid,returncode=child.returncode,termination_reason=reason,seconds=time.monotonic()-start,peak_sampled_family_rss_kib=peak,rss_limit_kib=args.rss_mib*1024,wall_limit_seconds=args.seconds,sample_interval_seconds=.02)
        out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
    raise SystemExit(code if code>=0 else 1)
if __name__=='__main__':main()
