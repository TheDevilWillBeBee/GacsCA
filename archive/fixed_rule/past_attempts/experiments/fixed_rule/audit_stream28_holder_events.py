"""Sample complete integrated F steps against a concurrent stream witness.

The witness is reconstructed from the certified straight-line packet paths.
Only sampled physical sites are stepped; this is not a complete work period.
"""
import hashlib
import json
from pathlib import Path
import random
import time

from gacsca.fixed_rule import stream28_holder_core as c
from gacsca.fixed_rule import stream28_holder_initial as initial
from gacsca.fixed_rule import stream28_holder_program as p
from gacsca.fixed_rule import stream28_holder_projected as r
from gacsca.fixed_rule import stream28_holder_rule as f


class Snapshot:
    def __init__(self,source,t,rows):
        self.source=source;self.n=len(source);self.size=self.n*f.Q;self.t=t
        self.history={};self.right={};self.left={}
        for stage,wire,offset,field,a,target,launch,arrival in rows:
            start=c.RESET_AGES[stage];launch+=start;arrival+=start
            if t<launch:continue
            direction=1 if offset<0 else -1
            for col in range(self.n):
                value=source[col][field]
                if t>=arrival:
                    at=((col-offset)%self.n)*f.Q+target
                    assert at not in self.history
                    self.history[at]=value
                    continue
                distance=t-launch
                at=(col*f.Q+a+direction*distance)%self.size
                crossings=((a+distance)//f.Q if direction==1 else
                           (distance+f.Q-1-a)//f.Q)
                hops=abs(offset)-crossings
                assert 0<=hops<=7
                lane=self.right if direction==1 else self.left
                assert at not in lane
                lane[at]=(wire,value,hops)

    def logical(self,position):
        position%=self.size;col,address=divmod(position,f.Q)
        info=POSITION_TO_FIELD.get(address)
        data=(self.source[col][info] if info is not None else
              self.history.get(position,0))
        values=dict(r.record(address),address=address,age=self.t,data=data)
        for prefix,lane in (('rp',self.right),('lp',self.left)):
            packet=lane.get(position)
            if packet is not None:
                wire,value,hops=packet
                values.update({prefix+'_target':wire,prefix+'_data':value,
                               prefix+'_remaining':hops,prefix+'_valid':1})
        return c.Cell(**values)

    def projected(self,position):
        return initial.coherent_cell(self.logical,position)


POSITION_TO_FIELD={address:field for field,address in enumerate(p.layout().info)}


def routes():
    g=p.layout();rows=[]
    for wire in g.gathered_inputs:
        neighbor,field=divmod(wire,f.FIELDS);offset=neighbor-7
        source=g.info[field];direction=1 if offset<0 else -1
        launch=2+(((source-wire) if direction==1 else (wire-source))%f.Q)
        for stage in range(3):
            target=g.history(stage,offset,field)
            distance=abs(offset)*f.Q+(target-source if direction==1 else source-target)
            rows.append((stage,wire,offset,field,source,target,launch,launch+distance))
    return tuple(rows)


def check():
    started=time.perf_counter();rng=random.Random(2026092821)
    upper=tuple(r.Cell(**{name:rng.getrandbits(width) for name,width in r.SCHEMA})
                for _ in range(15))
    source=tuple(f.encode_cell(r.lift(cell)) for cell in upper)
    rows=routes();chosen={offset:next(row for row in rows if row[0]==0 and row[2]==offset)
                         for offset in (-1,0,1)}
    ticks={0}
    for stage in range(3):
        start=c.RESET_AGES[stage]
        ticks.add(start)
        for offset,row in chosen.items():
            stage_row=next(x for x in rows if x[0]==stage and x[1]==row[1])
            ticks.update((start+stage_row[6]-1,start+stage_row[6],
                          start+stage_row[7]-1,start+stage_row[7]))
    samples=0;checked=[]
    for t in sorted(ticks):
        old,new=Snapshot(source,t,rows),Snapshot(source,t+1,rows)
        positions={rng.randrange(old.size) for _ in range(5)}
        for row in chosen.values():
            _,_,offset,field,a,target,_,_=row
            for colony in (0,7,14):
                positions.update((colony*f.Q+a,
                                  ((colony-offset)%15)*f.Q+target))
        positions.update(tuple(old.right)[:2]);positions.update(tuple(old.left)[:2])
        positions.update(tuple(new.right)[:2]);positions.update(tuple(new.left)[:2])
        for position in positions:
            neighborhood=tuple(r.lift(old.projected(position+j))
                               for j in f.NEIGHBORHOOD)
            got=r.project(f.local_step(neighborhood))
            want=new.projected(position)
            if got!=want:
                fields=[name for name,_ in r.SCHEMA if getattr(got,name)!=getattr(want,name)]
                raise AssertionError(('integrated stream local mismatch',t,position,fields[:12]))
            samples+=1
        checked.append(dict(tick=t,positions=len(positions),
                            live_packets=len(old.left)+len(old.right),
                            delivered=len(old.history)))
    endpoints=0
    for stage,wire,offset,field,a,target,launch,arrival in rows:
        start=c.RESET_AGES[stage];source_col=7
        value=source[source_col][field]
        source_pos=source_col*f.Q+a
        destination_col=(source_col-offset)%15
        target_pos=destination_col*f.Q+target
        prefix='rp' if offset<0 else 'lp'
        def core_neighborhood(position,age,packet_position=None):
            cells=[]
            for delta in range(-5,6):
                at=(position+delta)%(15*f.Q);col,address=divmod(at,f.Q)
                info=POSITION_TO_FIELD.get(address)
                datum=source[col][info] if info is not None else 0
                values=dict(r.record(address),address=address,age=age,data=datum)
                if packet_position is not None and at==packet_position:
                    values.update({prefix+'_target':wire,prefix+'_data':value,
                                   prefix+'_remaining':0,prefix+'_valid':1})
                cells.append(c.Cell(**values))
            return tuple(cells)
        emitted=c._clock_step(core_neighborhood(source_pos,start+launch-1))
        if (getattr(emitted,prefix+'_valid')!=1 or
            getattr(emitted,prefix+'_target')!=wire or
            getattr(emitted,prefix+'_remaining')!=abs(offset) or
            getattr(emitted,prefix+'_data')!=value):
            raise AssertionError(('stream emission endpoint',stage,wire))
        prior=(target_pos+(-1 if offset<0 else 1))%(15*f.Q)
        accepted=c._clock_step(core_neighborhood(target_pos,start+arrival-1,prior))
        if accepted.data!=value or getattr(accepted,prefix+'_valid'):
            raise AssertionError(('stream acceptance endpoint',stage,wire))
        endpoints+=2
    return dict(passed=True,Q=f.Q,U=f.U,colonies=len(source),routes=len(rows),
                sampled_full_F_site_steps=samples,
                exhaustive_core_endpoint_events=endpoints,ticks=checked,
                seconds=time.perf_counter()-started,
                full_rule_sha256=hashlib.sha256(Path(f.__file__).read_bytes()).hexdigest(),
                limitation='Sampled full projected F site steps against an analytical '
                           'concurrent stream witness; no full-stage or full-period replay.')


if __name__=='__main__':
    result=check();path=Path('figs/fixed_rule/stream28_holder_events_v2.json')
    if path.exists():raise FileExistsError(path)
    path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='ticks'},indent=2))
