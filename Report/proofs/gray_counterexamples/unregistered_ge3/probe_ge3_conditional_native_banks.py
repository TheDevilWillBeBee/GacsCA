#!/usr/bin/env python3
"""UNREGISTERED exact conditional upper-bank calculation, not physical GE3.

The quiet lower width m_n=17+3n is an assumption for n>=2. GE2 proves
only the first two physical prefixes. No new rule or main checkpoint.
"""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
SOURCE=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(SOURCE))
import literal_maintenance as literal
import check_gray_global_first_flags as first

Q=8192;U=1048576


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def calculate():
    # These initial values are the previously proved native Z1 exterior too.
    old={g:dict(addr=g%Q,age=1,f1=int(g in first.FLAG1_SUPPORT),
        f2=0,wf1=0,wf2=0) for g in range(-180,181)}
    zero=dict(addr=0,age=0,f1=0,f2=0,wf1=0,wf2=0)
    rows=[];signature=hashlib.sha256()
    for n in range(1,16):
        # n is the current upper evaluation count, not a physical clock.
        assumed_width=17+3*n
        barriers=(-1,assumed_width-1)
        new={};banks={}
        for g in range(-180+5*n,181-5*n):
            bank={d:old[g+d] if d==0 or not any(
                min(g,g+d)<=b<=max(g,g+d) for b in barriers)
                else zero for d in range(-5,6)}
            output=literal.scalar(bank)
            new[g]={k:output[k] for k in ('addr','age','f1','f2')}
            # GE1 mirrors these native Workspace outputs as reset zero.
            new[g].update(wf1=0,wf2=0)
            banks[g]=bank
        assert all(v['addr']==g%Q for g,v in new.items())
        assert all(0<=v['age']<=n+1 for v in new.values())
        assert all(v['age']==n+1 for g,v in new.items() if g<=-2)
        assert new[-1]['age']==1
        if n<15:
            assert not any(v['f2'] for v in new.values())
        row=dict(evaluation=n+1,assumed_quiet_lower_width_Q=assumed_width,
            assumed_full_lower_Flag1_barrier_colonies=barriers,
            exact_retained_receiver_interval=[-180+5*n,181-5*n],
            native_outputs={str(g):v for g,v in new.items()},
            left_Ages={str(g):new[g]['age'] for g in range(-9,1)},
            Flag2_receivers=[g for g,v in new.items() if v['f2']],
            right_Flag2_banks={str(g):banks[g] for g,v in new.items()
                if v['f2'] and g>0})
        rows.append(row)
        signature.update(json.dumps(row,sort_keys=True).encode())
        old=new
    assert rows[-1]['Flag2_receivers']==[-3,-2,58,59,60]
    return dict(rows=rows,exact_conditional_trace_sha256=signature.hexdigest(),
        evaluation16_three_consecutive_right_Flag2_receivers=[58,59,60],
        evaluation16_right_full_barrier_colony=61,
        global_common_Age_used=False,
        later_physical_banks_or_pulses_proved=False,
        full_own_beta_layout_computed_SimBit_completion_proved=False,
        faithful_Gray_counterexample_iid_or_faster_U_proved=False)


def receipt():
    dependencies=('literal_maintenance.py','check_gray_global_first_flags.py',
        'GE1_NATIVE_WRITEBACK_SECOND_BANK.md','GE2_SECOND_NATIVE_PREFIX.md')
    return dict(Q=Q,U=U,lambda_original=24,c_original=104,
        probe_source_sha256=digest(__file__),
        proof_sha256=digest(Path(__file__).parent/'GE3_CONDITIONAL_NATIVE_BANK_PROBE.md'),
        source_dependencies_sha256={name:digest(SOURCE/name) for name in dependencies},
        GE2_receipt_sha256=digest(ROOT/'figs/gray_counterexamples/GE2_second_native_prefix_certificate.json'),
        initial_Z1_from_same_shared_row0_17Q_clock_history=True,
        assumed_later_lower_width_sequence='m_n=17+3n, n>=2; not a reachability result',
        assumed_actual_native_bank='inclusive-path null at barriers -1 and m_n-1; self retained',
        results=calculate())


if __name__=='__main__':
    result=receipt()
    path=ROOT/'figs/gray_counterexamples/unregistered_ge3/GE3_conditional_native_bank_probe.json'
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps(dict(receipt=str(path),sha256=digest(path),
        evaluation16_Flag2_receivers=result['results']['rows'][-1]['Flag2_receivers'],
        actual_later_physical_history_proved=False)))
