"""Emit a new instance of the frozen proved GE0 event kernel.

Only the finite source set, initial aligned interval and target/time labels
are changed. This emits an analysis kernel, not a changed CA candidate.
The caller must derive the source set from the actual second early run.
"""
from pathlib import Path

COMMAND=(-4,-3,-2,-1,10,11,12,13,14,15,16,17,18,19,20,21,22)


def generated_source():
    text=(Path(__file__).parent/'ge0_first_workspace_native.c').read_text()
    edits=(
        ('conditional first GE0 pulse','conditional second GE2 pulse'),
        ('static const int command[]={-3,-2,-1,13,14,15,16,17,18,19};',
         'static const int command[]={'+','.join(map(str,COMMAND))+'};'),
        ('int lo=-2*Q-5,hi=20*Q; /* union of the ten immutable source strips */',
         'int lo=-3*Q-5,hi=23*Q; /* hull of the seventeen derived source strips */'),
        ('right==20*Q && width==20*Q','right==23*Q && width==23*Q'),
        ('s->s[1].hi==19*Q','s->s[1].hi==22*Q'),
        ('s->s[2].lo==19*Q && s->s[2].hi==20*Q','s->s[2].lo==22*Q && s->s[2].hi==23*Q'),
        ('append(&a,0,16*Q,1);append(&a,16*Q,17*Q,3);',
         'append(&a,0,19*Q,1);append(&a,19*Q,20*Q,3);'),
        ('physical_row','local_period_row'),
        ('first_exact_20Q_clock_row','first_exact_23Q_clock_row'),
        ('first_exact_quiet_20Q_native_row','first_exact_quiet_23Q_native_row'),
        ('final_matches_20Q_stationary_native_form','final_matches_23Q_stationary_native_form'),
    )
    for old,new in edits:
        assert text.count(old)==1,(old,text.count(old));text=text.replace(old,new)
    return text


if __name__=='__main__':
    (Path(__file__).parent/'ge2_second_workspace_native.c').write_text(generated_source())
