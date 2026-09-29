"""Full-descriptor head routing and zero inactive controllers, at all clocks.

Diagnostic only. Boolean abstraction treats unrelated word predicates and
arithmetic bits as independent: a successful identity proves the stronger
unconstrained formula, never assumes an unproved correlation between them.
"""
import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import resource
import time

from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c
from gacsca.fixed_rule import small_holder_program as p, small_holder_projected as r
from gacsca.fixed_rule.word_bdd import BDD
from gacsca.fixed_rule.wordcode import NAND, ADD, SHR, EQ, LT
from experiments.fixed_rule import certify_small_holder_raw_mail_factorization as raw_mail


class BooleanAbstraction:
    """Exact bitwise gates, opaque remaining arithmetic/predicate expressions."""
    def __init__(self, terms):
        self.t=terms;self.b=BDD(100000);self.atoms={}
        self.bit=lru_cache(None)(self._bit)
        self.boolean=lru_cache(None)(self._boolean)

    def atom(self, key):
        if key not in self.atoms:
            if len(self.atoms)>=self.b.variables:raise RuntimeError('Boolean atom budget')
            self.atoms[key]=self.b.variable(len(self.atoms))
        return self.atoms[key]

    def _boolean(self, x):
        n=self.t.nodes[x]
        if self.t.width(x)<=1:return True
        # A & B is Boolean if either operand is Boolean.
        if n[0]=='not':
            inner=self.t.nodes[n[1]]
            if inner[0]=='op' and inner[1]==NAND:
                return self.boolean(inner[2]) or self.boolean(inner[3])
        # ~ (~A & ~B) is Boolean when both operands A,B are Boolean.
        if n[0]=='op' and n[1]==NAND:
            return self.boolean(self.t.inv(n[2])) and self.boolean(self.t.inv(n[3]))
        return False

    def _bit(self, x, k):
        if not 0<=k<64:raise ValueError('word bit outside alphabet')
        if len(self.b.nodes)>200000:raise RuntimeError('BDD node budget')
        n=self.t.nodes[x];b=self.b
        if n[0]=='const':return (n[1]>>k)&1
        if n[0]=='variable':return 0 if k>=n[2] else self.atom((x,k))
        if n[0]=='not':return b.inv(self.bit(n[1],k))
        if n[0]=='modadd':
            if k>=n[3]:return 0
            if n[2]==0:return self.bit(n[1],k)
            inverse=self.t.inv(n[1])
            if n[2]==1 and self.boolean(inverse):return self.bit(inverse,0)
            if k==0:return b.xor(self.bit(n[1],0),n[2]&1)
            return self.atom((x,k))
        if n[0]!='op':return self.atom((x,k))
        op,a,d=n[1:]
        if op==NAND:return b.inv(b.and_(self.bit(a,k),self.bit(d,k)))
        if op in (EQ,LT):
            if k:return 0
            if self.boolean(a) and self.boolean(d):
                left,right=self.bit(a,0),self.bit(d,0)
                return b.inv(b.xor(left,right)) if op==EQ else b.and_(b.inv(left),right)
            return self.atom((x,0))
        if op==ADD:
            for left,right in ((a,d),(d,a)):
                inverse=self.t.inv(left)
                if self.t.value(right)==1 and self.boolean(inverse):
                    # Two's complement of a Boolean is the all-bit selector mask.
                    return self.bit(inverse,0)
        if op==SHR and self.t.value(d) is not None:
            offset=self.t.value(d)
            return self.bit(a,k+offset) if k+offset<64 else 0
        return self.atom((x,k))

    def close(self):
        self.bit.cache_clear();self.boolean.cache_clear();self.b.binary.cache_clear()


def routing(terms,raw,phase):
    t=terms;zero,one=t.const(0),t.const(1)
    def cell(site,name):
        field='p3_'+name if name in c.STATIC else name if name in ('age','address') else 's2_'+name
        return raw(site)[f.COL[field]]
    age=cell(0,'age');eq=lambda x,value:t.op(EQ,x,t.const(value))
    active=t.any(*(t.all(t.not_(t.op(LT,age,t.const(lo))),t.op(LT,age,t.const(hi)))
                   for lo,hi in zip(c.RESET_AGES,c.ACTIVE_ENDS)))
    reboot=t.any(*(eq(age,at) for at in (*c.RESET_AGES,c.VOTE_AGES[0])))
    move={site:zero for site in (-1,0,1)}
    halted=zero
    if phase is not None:
        direction=cell(0,'direction');right=t.not_(direction)
        matched=t.op(EQ,cell(0,'index'),cell(0,'pc'))
        third=t.all(t.not_(t.op(LT,age,t.const(c.RESET_AGES[2]))),t.op(LT,age,t.const(c.ACTIVE_ENDS[2])))
        halted=t.all(right,matched,t.const(int(phase==c.FETCH)),
                     t.any(eq(cell(0,'kind'),c.HALT),t.all(eq(cell(0,'kind'),c.IF_THIRD),t.not_(third))))
        wait=t.all(right,matched,t.const(int(phase==c.FETCH)),eq(cell(0,'kind'),c.WAIT),t.nonzero(cell(0,'rd')))
        alive=t.not_(halted)
        move[-1]=t.all(alive,direction,t.not_(cell(0,'first')))
        move[1]=t.all(alive,right,t.not_(cell(0,'last')),t.not_(wait))
        move[0]=t.all(alive,t.any(t.all(direction,cell(0,'first')),t.all(right,cell(0,'last')),wait))
    def expected(site):
        return t.select(reboot,cell(site,'first'),t.select(active,move.get(site,zero),cell(site,'head')))
    return expected,move,halted


def certify_case(phase, description=None):
    t,raw,_=raw_mail.prepare(phase);desc=f.self_description() if description is None else description
    expected,move,halted=routing(t,raw,phase);proof=BooleanAbstraction(t);b=proof.b
    heads=bits=0
    for holder in (range(-4,5) if phase is not None else (0,)):
        output=t.expression(desc,tuple(w for j in f.NEIGHBORHOOD for w in raw(holder+j)))
        assert output[f.COL['address']]==raw(holder)[f.COL['address']]
        assert output[f.COL['age']]==t.modular_add(raw(holder)[f.COL['age']],1,32)
        for delta in f.OFFSETS:
            prefix=f's{delta+2}_';head=proof.bit(output[f.COL[prefix+'head']],0)
            assert head==proof.bit(expected(holder+delta),0),('head routing',phase,holder,delta)
            heads+=1
            for name in c.CONTROL:
                for k in range(dict(c.SCHEMA)[name]):
                    value=proof.bit(output[f.COL[prefix+name]],k)
                    assert b.and_(b.inv(head),value)==0,('inactive controller',phase,holder,delta,name,k)
                    bits+=1
    routes=[proof.bit(move[site],0) for site in (-1,0,1)]
    for i,a in enumerate(routes):
        for d in routes[i+1:]:assert b.and_(a,d)==0,('head duplicated',phase)
    total=b.or_(b.or_(routes[0],routes[1]),routes[2])
    assert total==(0 if phase is None else b.inv(proof.bit(halted,0))),('head lost without halt',phase)
    result=dict(phase=phase,passed=True,all_clock_ages=f.U,head_routing_identities=heads,
                inactive_controller_bit_implications=bits,routing_destinations_disjoint=True,
                active_head_survives_iff_not_halted=True,BDD_nodes=len(b.nodes),opaque_atoms=len(proof.atoms))
    proof.close();return result


def geometry(record=r.record):
    """Finite actual-ROM endpoint check used with the symbolic routing lemma."""
    length=len(p.base_rom());first=[];last=[]
    for address in range(f.Q):
        row=record(address)
        if row['first']:first.append(address)
        if row['last']:last.append(address)
    assert first==[0] and last==[length-1],('ROM endpoint defect',first,last)
    checked=0
    for address in range(length):
        for direction in (c.RIGHT,c.LEFT):
            target=(address if record(address)['last'] else address+1) if direction==c.RIGHT else (address if record(address)['first'] else address-1)
            assert 0<=target<length,('head escaped',address,direction,target)
            checked+=1
    # A wait stays at its source, and HALT removes the head, both preserving confinement.
    # At every reset/first vote, only the unique first record can acquire a head.
    return dict(passed=True,core_cells=length,colony_cells=f.Q,first=first,last=last,
                directed_source_positions_checked=checked,minimum_gap_to_next_colony_core=f.Q-length,
                ROM_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest())


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--pilot',action='store_true');parser.add_argument('--output',required=True)
    args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    started=time.perf_counter();rows=[]
    for phase in ((None,c.FETCH) if args.pilot else (None,*range(8))):
        rows.append(certify_case(phase));print(json.dumps(rows[-1]),flush=True)
    geo=geometry();paths=[Path(__file__),Path(raw_mail.__file__),Path(raw_mail.clock.__file__),Path(raw_mail.clock.regular.__file__),Path('gacsca/fixed_rule/word_bdd.py')]
    result=dict(passed=True,pilot=args.pilot,cases=rows,geometry=geo,
                head_routing_identities=sum(row['head_routing_identities'] for row in rows),
                inactive_controller_bit_implications=sum(row['inactive_controller_bit_implications'] for row in rows),
                descriptor_sha256=f.self_description().digest(),source_sha256={str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},
                seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                limitation='Canonical geometry; coherent old static/Data/head/controller, zero or one head locally, zero inactive control. Arbitrary raw mail/flags/Signals/Wf. Combined with fixed-ROM endpoints and procedure-image coherence this proves at most one head per core, confinement and zero inactive controllers. Does not prove instruction schedule/Data/Signal/flag or full work-period/nested/noise correctness.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2),flush=True)


if __name__=='__main__':main()
