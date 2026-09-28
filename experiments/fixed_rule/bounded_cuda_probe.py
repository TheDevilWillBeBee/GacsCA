"""Watch a single owned probe: bounded wall time and measured physical host RSS.

CUDA reserves a large virtual address space, so RLIMIT_AS is inappropriate here.
The monitor samples every 20 ms; its RSS threshold is not an instantaneous OS cap.
No process other than the direct child launched here is signaled.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import time


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True)
    parser.add_argument('--seconds',type=float,default=60);parser.add_argument('--rss-mib',type=int,default=512)
    parser.add_argument('command',nargs=argparse.REMAINDER);args=parser.parse_args()
    output=Path(args.output)
    if output.exists():raise FileExistsError(output)
    command=args.command
    if command and command[0]=='--':command=command[1:]
    if not command:raise ValueError('probe command required')
    started=time.monotonic();child=subprocess.Popen(command,env={**os.environ,'OPENBLAS_NUM_THREADS':'1'})
    peak=0;reason=None
    try:
        while child.poll() is None:
            try:
                status=Path(f'/proc/{child.pid}/status').read_text()
                rss=next((int(line.split()[1]) for line in status.splitlines() if line.startswith('VmRSS:')),0)
                peak=max(peak,rss)
            except FileNotFoundError:pass
            if peak>args.rss_mib*1024:reason='RSS threshold exceeded'
            elif time.monotonic()-started>args.seconds:reason='wall-time limit exceeded'
            if reason:child.kill();break
            time.sleep(.02)
        code=child.wait()
    finally:
        if child.poll() is None:child.kill();child.wait()
        result=dict(command=command,pid=child.pid,returncode=child.returncode,termination_reason=reason,seconds=time.monotonic()-started,peak_sampled_rss_kib=peak,rss_limit_kib=args.rss_mib*1024,wall_limit_seconds=args.seconds,sample_interval_seconds=.02)
        output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)
    raise SystemExit(code if code>=0 else 1)

if __name__=='__main__':main()
