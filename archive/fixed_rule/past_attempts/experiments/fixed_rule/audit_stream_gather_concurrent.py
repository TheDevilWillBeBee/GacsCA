"""Compare reconstructed concurrent streams to literal local CA steps.

The reconstruction uses the separately proved straight-line packet schedule
as a witness. At sampled ticks every site of a 15-colony ring is then
advanced by the radius-one transition, and all fields are compared against
the next witness state. This does not replay every tick or close self-reference.
"""
import argparse
import hashlib
import json
from pathlib import Path
import time

from gacsca.fixed_rule import stream_gather as s
from gacsca.fixed_rule import packed28_holder_rule as f
from gacsca.fixed_rule import packed28_holder_projected as r
from experiments.fixed_rule.run_packed28_holder_cpu_general_periods import parents


class Snapshot:
    def __init__(self,templates,rows,t):
        self.templates=templates;self.n=len(templates);self.size=self.n*s.Q;self.t=t
        self.right={};self.left={};self.hist={}
        for stage,number,offset,field,source,target,launch,arrival in rows:
            launch+=stage*s.FRAME;arrival+=stage*s.FRAME
            sign=s.direction(offset)
            for col in range(self.n):
                if t>=arrival:
                    at=((col-offset)%self.n)*s.Q+target
                    assert at not in self.hist
                    self.hist[at]=templates[col][source].info_value
                elif t>=launch:
                    distance=t-launch
                    at=(col*s.Q+source+sign*distance)%self.size
                    crossings=((source+distance)//s.Q if sign==1
                               else (distance+s.Q-1-source)//s.Q)
                    hops=max(0,abs(offset)-crossings)
                    packet=s.Packet(1,number,hops,stage,templates[col][source].info_value)
                    lane=self.right if sign==1 else self.left
                    assert at not in lane,('concurrent same-direction collision',t,at)
                    lane[at]=packet

    def cell(self,position):
        position%=self.size;col,address=divmod(position,s.Q)
        value=self.hist.get(position)
        return s.replace(self.templates[col][address],age=self.t,
                         right=self.right.get(position,s.EMPTY),
                         left=self.left.get(position,s.EMPTY),
                         history_valid=int(value is not None),
                         history_value=0 if value is None else value)


def check(ticks=None):
    started=time.perf_counter();certificate=s.schedule_certificate()
    upper=parents(15)
    words=tuple(f.encode_cell(r.lift(cell)) for cell in upper)
    templates=tuple(tuple(s.initial_cell(at,source) for at in range(s.Q))
                    for source in words)
    rows=certificate['rows']
    if ticks is None:
        last=certificate['last_delivery']
        ticks=(0,s.Q//2,s.Q-1,2*s.Q,last-1,last,s.FRAME-1,
               s.FRAME,s.FRAME+s.Q,s.FRAME+last-1,s.FRAME+last,
               2*s.FRAME-1,2*s.FRAME,2*s.FRAME+s.Q,
               2*s.FRAME+last-1,2*s.FRAME+last,3*s.FRAME-1)
    checked=[]
    for t in ticks:
        old=Snapshot(templates,rows,t);new=Snapshot(templates,rows,t+1)
        for position in range(old.size):
            actual=s.local_step(tuple(old.cell(position+j) for j in (-1,0,1)))
            expected=new.cell(position)
            if actual!=expected:
                fields=tuple(name for name in s.Cell.__dataclass_fields__
                             if getattr(actual,name)!=getattr(expected,name))
                raise AssertionError(('concurrent local transition mismatch',t,position,fields,
                                      actual,expected))
        checked.append(dict(old_tick=t,complete_sites=old.size,
                            live_right=len(old.right),live_left=len(old.left),
                            delivered_history_sites=len(old.hist)))
    final=Snapshot(templates,rows,3*s.FRAME)
    assert not final.right and not final.left
    histories_checked=0
    for stage,number,offset,field,source,target,launch,arrival in rows:
        for destination_col in range(len(templates)):
            source_col=(destination_col+offset)%len(templates)
            at=destination_col*s.Q+target
            assert final.hist[at]==words[source_col][field],(
                'complete raw gathered input mismatch',stage,destination_col,number)
            histories_checked+=1
    return dict(passed=True,colonies=len(templates),checked_ticks=checked,
                complete_local_site_steps=sum(row['complete_sites'] for row in checked),
                complete_raw_histories_checked=histories_checked,
                last_schedule_delivery=certificate['last_delivery'],
                seconds=time.perf_counter()-started,
                rule_source_sha256=hashlib.sha256(Path(s.__file__).read_bytes()).hexdigest(),
                limitation='Full 15-colony literal local transitions at sampled '
                           'ticks against an analytical concurrent trajectory; '
                           'not a full-stage literal replay or closed self-simulator.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',required=True,type=Path)
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError('preserve earlier evidence')
    result=check();args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__':main()
