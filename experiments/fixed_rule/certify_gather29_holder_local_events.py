"""Full-raw symbolic local events for the branch and phase-marked gather.

Each event has one coherent right-moving head at its actual own-ROM location,
canonical holder geometry, a regular active Age and arbitrary surrounding
MEM data. This proves one physical step only, not a head scan or period.
"""
import json
from types import FunctionType

from gacsca.fixed_rule import gather29_holder_rule as f
from gacsca.fixed_rule import gather29_holder_core as c
from gacsca.fixed_rule import gather29_holder_program as p
from gacsca.fixed_rule.wordcode_and import ADD, AND, AND_ALU
from experiments.fixed_rule import certify_compact16_holder_position_events as prior


class Modular(prior.Modular):
    def op(self,kind,a,b):
        if kind in (AND,AND_ALU):return self.band(a,b)
        return super().op(kind,a,b)


def bind(function):
    namespace=dict(function.__globals__)
    namespace.update(f=f,c=c,p=p,Modular=Modular)
    result=FunctionType(function.__code__,namespace,function.__name__,
                        function.__defaults__,function.__closure__)
    result.__kwdefaults__=function.__kwdefaults__
    return result


quiet_prepare=bind(prior.prepare)


def cases():
    g=p.layout()
    result=[('branch_early',g.branch_instruction,c.VOTE_AGES[0]+100,None),
            ('branch_late',g.branch_instruction,c.RESET_AGES[4]+100,None)]
    for kind in (ADD,c.SEND):
        pc=next(pc for pc,op in enumerate(g.instructions)
                if op.kind==kind and
                ((op.d if kind==ADD else op.b)&c.PHASE_MARK))
        result.extend((f'{"add" if kind==ADD else "send"}_gather_{stage}',
                       pc,c.RESET_AGES[stage]+100,stage)
                      for stage in range(3))
    return tuple(result)


def certify_case(case):
    name,pc,age,stage=case
    op=p.layout().instructions[pc]
    terms,quiet=quiet_prepare(dict(name='quiet',role='quiet'))
    zero,one=terms.const(0),terms.const(1)
    old={field:terms.variable('old_'+field,dict(c.SCHEMA)[field])
         for field in c.CONTROL}
    old.update(phase=zero,direction=zero,pc=terms.const(pc))
    new=dict(old)
    if op.kind==c.BRANCH_THIRD:
        assert stage is None
        target=p.layout().signal_entry if name=='branch_early' else pc+1
        new['pc']=terms.const(target)
    elif op.kind==ADD:
        assert stage in range(3) and op.d&c.PHASE_MARK
        target=(op.d&~c.PHASE_MARK)+c.GATHER_OFFSETS[stage]
        new.update(phase=terms.const(c.READ_A),ra=terms.const(op.a&0xffffffff),
                   rb=terms.const(op.b),rd=terms.const(target),alu=terms.const(ADD))
    elif op.kind==c.SEND:
        assert stage in range(3) and op.b&c.PHASE_MARK
        target=(op.b&~c.PHASE_MARK)+c.GATHER_OFFSETS[stage]
        new.update(phase=terms.const(c.TRANSMIT),ra=terms.const(op.a&0xffffffff),
                   rb=terms.const(target),rd=terms.const(op.d))
    else:raise ValueError(case)
    static=dict(kind=op.kind,index=pc,a=op.a,b=op.b,d=op.d,first=0,last=0)

    def raw(position,after=False):
        values=list(quiet(position,after=after))
        values[f.COL['age']]=terms.const(age+int(after))
        for offset in f.STATIC_OFFSETS:
            if position+offset==0:
                for field,value in static.items():
                    values[f.COL[f'p{offset+3}_{field}']]=terms.const(value)
        for offset in f.OFFSETS:
            site=position+offset
            ctrl=new if after and site==1 else old if not after and site==0 else None
            if ctrl is None:continue
            prefix=f's{offset+2}_'
            values[f.COL[prefix+'head']]=one
            for field,value in ctrl.items():
                values[f.COL[prefix+field]]=value
        return tuple(values)

    description=f.self_description()
    for position in range(-4,5):
        actual=terms.expression(description,tuple(
            word for delta in f.NEIGHBORHOOD
            for word in raw(position+delta)))
        expected=raw(position,after=True)
        for (field,_),got,want in zip(f.SCHEMA,actual,expected):
            assert got==want,(name,position,field,terms.nodes[got],terms.nodes[want])
    return dict(name=name,age=age,opcode=op.kind,pc=pc,
                full_raw_output_words=9*f.FIELDS,symbolic_terms=len(terms.nodes))


def check():
    rows=tuple(certify_case(case) for case in cases())
    return dict(passed=True,cases=rows,case_count=len(rows),
                full_raw_output_words=sum(row['full_raw_output_words'] for row in rows),
                descriptor_sha256=f.self_description().digest(),
                scope='One full-raw physical local step per coherent event; '
                      'canonical holder geometry, regular active clock, '
                      'arbitrary surrounding MEM data, zero flags/mail.',
                limitation='Does not compose scans, packets, a period or macrostep.')


if __name__=='__main__':print(json.dumps(check(),indent=2))
