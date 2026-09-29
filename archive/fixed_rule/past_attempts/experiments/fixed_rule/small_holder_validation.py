"""Run bounded reference executions and independent audits sequentially.

This harness never evolves simulated state itself. Each physical execution and
its audit runs in a fresh subprocess, keeping host memory use bounded.
"""
import argparse,json,os,resource,subprocess,sys,time
from pathlib import Path


def execute(prefix):
    prefix=Path(prefix);progress=prefix.with_name(prefix.name+'_validation_v1.json')
    if progress.exists():raise FileExistsError('preserve validation evidence')
    def stem(kind):return str(prefix.with_name(prefix.name+'_'+kind+'_v1'))
    def audit_path(kind):return stem(kind+'_audit')+'.json'
    stages=[
        ('execution','small_holder_execution',['--output',stem('execution')]),
        ('execution_audit','audit_small_holder_execution',['--input',stem('execution'),'--output',audit_path('execution')]),
        ('macrostep','small_holder_macrostep',['--prefix',stem('execution'),'--output',stem('macrostep')]),
        ('macrostep_audit','audit_small_holder_macrostep',['--input',stem('macrostep'),'--output',audit_path('macrostep')]),
        ('recurrent_execution','small_holder_recurrent_execution',['--previous',stem('macrostep'),'--output',stem('recurrent_execution')]),
        ('recurrent_execution_audit','audit_small_holder_recurrent_execution',['--input',stem('recurrent_execution'),'--output',audit_path('recurrent_execution')]),
        ('second_macrostep','small_holder_macrostep',['--prefix',stem('recurrent_execution'),'--output',stem('second_macrostep')]),
        ('second_macrostep_audit','audit_small_holder_macrostep',['--input',stem('second_macrostep'),'--output',audit_path('second_macrostep')]),
        ('two_periods_audit','audit_small_holder_two_periods',['--first',stem('macrostep'),'--second-prefix',stem('recurrent_execution'),'--second',stem('second_macrostep'),'--output',audit_path('two_periods')]),
    ]
    # Check the entire intended namespace before launching any process.
    for kind,_,_ in stages:
        for ext in ('.log','.json','.npz','.tar.gz','.progress.json'):
            if Path(stem(kind)+ext).exists():raise FileExistsError(stem(kind)+ext)
    result=dict(status='running',stages=[],largest_child_rss_kib=0)
    started=time.monotonic();env=dict(os.environ,OPENBLAS_NUM_THREADS='1')
    for kind,module,args in stages:
        command=[sys.executable,'-m','experiments.fixed_rule.'+module,*args]
        result['active_stage']=kind;progress.write_text(json.dumps(result,indent=2)+'\n')
        t=time.monotonic()
        with Path(stem(kind)+'.log').open('x') as log:
            child=subprocess.run(command,stdout=log,stderr=subprocess.STDOUT,env=env)
        row=dict(stage=kind,command=command,returncode=child.returncode,seconds=time.monotonic()-t)
        result['stages'].append(row);result['largest_child_rss_kib']=resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss
        print(json.dumps(row),flush=True)
        if child.returncode:
            result['status']='failed';progress.write_text(json.dumps(result,indent=2)+'\n')
            raise RuntimeError('failed stage: '+kind)
    result.update(status='complete',active_stage=None,seconds=time.monotonic()-started)
    progress.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--prefix',required=True,type=Path)
    execute(parser.parse_args().prefix)
