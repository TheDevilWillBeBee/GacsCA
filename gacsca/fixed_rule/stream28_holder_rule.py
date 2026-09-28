"""Fixed radius-seven candidate with fivefold simulation-state protection.

Primary Gray/candidate-B maintenance remains radius five. Radius seven allows
backup Wf to use the actual computed Flag1/Address/Age at its logical primary.
Data/head/controller/mail procedures use corrected words and holder-local raw
geometry, not one damaged primary geometry broadcast into every backup.
This is a new fixed construction, never a depth-selected rule.
"""
from dataclasses import make_dataclass,field,replace
from functools import lru_cache
from . import stream28_holder_core as core

Q,U=core.Q,core.U
T,RESET_AGES,ACTIVE_ENDS,VOTE_AGES,CAPTURE_AGE,WF_START,WF_END=(getattr(core,n) for n in ('T','RESET_AGES','ACTIVE_ENDS','VOTE_AGES','CAPTURE_AGE','WF_START','WF_END'))
NEIGHBORHOOD=tuple(range(-7,8))
OFFSETS=tuple(range(-2,3))
STATIC_OFFSETS=tuple(range(-3,4))
PROCEDURE=tuple((n,w) for n,w in core.SCHEMA if n in ('data','head',*core.CONTROL) or n.startswith(('lp_','rp_')))
GEOMETRY=tuple((n,w) for n,w in core.SCHEMA if n in ('address','age','f1','f2','signal'))
STATIC=tuple((f'p{k+3}_{n}',dict(core.SCHEMA)[n]) for k in STATIC_OFFSETS for n in core.STATIC)
SCHEMA=STATIC+tuple((f's{k+2}_{n}',w) for k in OFFSETS for n,w in PROCEDURE)+tuple((f'w{k+2}_{n}',1) for k in OFFSETS for n in ('wf1','wf2'))+GEOMETRY
FIELDS=len(SCHEMA);WIDTH=sum(w for _,w in SCHEMA);COL={n:i for i,(n,_) in enumerate(SCHEMA)}


def validate(self):
    for name,width in SCHEMA:
        value=getattr(self,name)
        if not isinstance(value,int) or not 0<=value<1<<width:raise ValueError(f'{name} outside fixed holder alphabet')


Cell=make_dataclass('Cell',[(n,int,field(default=0)) for n,_ in SCHEMA],frozen=True,namespace={'__post_init__':validate,'__module__':__name__})


def encode_cell(cell):return tuple(getattr(cell,n) for n,_ in SCHEMA)
def decode_cell(words):
    if len(words)!=FIELDS:raise ValueError('every raw replica/controller/metadata word required')
    return Cell(**dict(zip((n for n,_ in SCHEMA),map(int,words))))


def majority5(values):
    a,b,c,d,e=values
    return (a&b&c)|(((a&b)|(a&c)|(b&c))&(d|e))|((a|b|c)&d&e)


def corrected(cells,target,name):
    if not -4<=target<=4:raise ValueError('procedure operand outside fixed halo')
    return majority5(tuple(getattr(cells[7+target+e],f's{2-e}_{name}') for e in OFFSETS))


def primary(cell):
    return core.Cell(address=cell.address,age=cell.age,f1=cell.f1,f2=cell.f2,wf1=cell.w2_wf1,wf2=cell.w2_wf2,signal=cell.signal)


def maintained(cells,target):return core.maintenance(tuple(primary(cells[7+target+j]) for j in range(-5,6)))


def vote_signal(cells,target):
    if not -5<=target<=5:raise ValueError('Signal vote exceeds radius seven')
    return int(sum((cells[7+target+e].signal>>(2-e))&1 for e in OFFSETS)>=3)


def local_step(cells):
    if len(cells)!=15:raise ValueError('exact radius-seven neighborhood required')
    center=cells[7];geometry={d:maintained(cells,d) for d in OFFSETS}
    values={j:{n:corrected(cells,j,n) for n,_ in PROCEDURE} for j in range(-4,5)};changes=dict(geometry[0])
    for d in OFFSETS:
        virtual=[]
        for j in range(-5,6):
            local=dict(address=(center.address+d+j)%Q,age=center.age)
            if -1<=j<=1:
                local.update(values[d+j]);local.update({n:getattr(center,f'p{d+j+3}_{n}') for n in core.STATIC})
            elif j==2:local['data']=values[d+j]['data']
            virtual.append(core.Cell(**local))
        result=core._clock_step(tuple(virtual))
        changes.update({f's{d+2}_{n}':getattr(result,n) for n,_ in PROCEDURE})
    signal=0
    for d in OFFSETS:
        value=vote_signal(cells,d)
        if geometry[0]['age']==core.CAPTURE_AGE and geometry[0]['address']+d in (3,Q-3):value=values[0]['data']&1
        signal|=value<<(d+2)
    changes['signal']=signal
    for d in OFFSETS:
        g=geometry[d];wf1=wf2=0
        if WF_START<=g['age']<WF_END:
            if g['address']>=Q-5:wf1=vote_signal(cells,d+Q-3-g['address'])
            if g['address']<=4 and not g['f1']:wf2=vote_signal(cells,d+3-g['address'])
        changes[f'w{d+2}_wf1']=wf1;changes[f'w{d+2}_wf2']=wf2
    # Gray's clearing priorities apply at the physical holder, to every copy.
    if geometry[0]['f1']:
        for d in OFFSETS:
            for n,_ in PROCEDURE:
                if n.startswith(('lp_','rp_')):changes[f's{d+2}_{n}']=0
        if geometry[0]['address']!=center.address:
            for d in OFFSETS:
                for n,_ in PROCEDURE:changes[f's{d+2}_{n}']=0
                for n in ('wf1','wf2'):changes[f'w{d+2}_{n}']=0
            changes['signal']=0
    return replace(center,**changes)


def step_ring(cells):return tuple(local_step(tuple(cells[(i+j)%len(cells)] for j in NEIGHBORHOOD)) for i in range(len(cells)))


@lru_cache(maxsize=1)
def self_description():
    from .stream28_holder_description import build
    return build()


def identity():return dict(schema=SCHEMA,width=WIDTH,words=FIELDS,neighborhood=NEIGHBORHOOD,Q=Q,U=U,description_sha256=self_description().digest(),procedure_geometry='physical-holder-local',wf='fivefold-derived-from-logical-primary-computed-maintenance',maintenance='candidate-B-raw-primary-Wf',third_evaluation_old_age=core.VOTE_AGES[0],temporal_vote='parallel corrected radius-two procedure')
