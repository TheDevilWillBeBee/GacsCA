"""All-clock quiet procedure transitions: reset entries, votes and commit.

Old Data/static replicas are coherent; old heads/controllers/mail are zero.
Physical flags, Signals and Wf are arbitrary under canonical geometry.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time

from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c
from gacsca.fixed_rule.wordcode import ADD, EQ, LT, SHR
from experiments.fixed_rule import certify_small_holder_clock_mail_factorization as clock
from experiments.fixed_rule.certify_small_holder_head_invariant import BooleanAbstraction


def prepare():
    t,base,_=clock.prepare(None);raw=lambda pos:base(pos,mail=False)
    zero,one=t.const(0),t.const(1)
    def cell(site,name):
        field='p3_'+name if name in c.STATIC else name if name in ('age','address') else 's2_'+name
        return raw(site)[f.COL[field]]
    age=cell(0,'age');eq=lambda x,value:t.op(EQ,x,t.const(value))
    resets=[eq(age,at) for at in c.RESET_AGES];reset=t.any(*resets)
    extra=eq(age,c.VOTE_AGES[0]);vote_age=t.any(*(eq(age,at) for at in c.VOTE_AGES))
    def expected(site):
        first=cell(site,'first');kind=cell(site,'kind');a=cell(site,'a');entry=zero
        for stage,predicate in enumerate(resets):
            value=t.mask(t.op(SHR,cell(site,'a' if stage<2 else 'b'),t.const(32*(stage if stage<2 else stage-2))),32) if stage<4 else cell(site,'d')
            entry=t.select(predicate,value,entry)
        head=t.band(first,t.any(reset,extra))
        pc=t.select(extra,t.select(first,cell(site,'d'),zero),t.select(t.all(first,reset),entry,zero))
        marked=t.any(*(t.all(predicate,t.band(t.op(SHR,a,t.const(stage)),one)) for stage,predicate in enumerate(resets)))
        clear=t.all(reset,t.any(first,t.all(eq(kind,c.MEM),marked)))
        data=t.select(clear,zero,cell(site,'data'))
        voting=t.all(eq(kind,c.MEM),t.not_(first),t.nonzero(t.band(a,t.const(c.VOTE))),vote_age)
        x,y,z=(cell(site+j,'data') for j in (-1,1,2))
        majority=t.bor(t.bor(t.band(x,y),t.band(x,z)),t.band(y,z))
        data=t.select(voting,majority,data)
        commit=t.all(eq(kind,c.MEM),t.not_(first),t.nonzero(t.band(a,t.const(c.INFO))),eq(age,f.U-1))
        data=t.select(commit,cell(site+1,'data'),data)
        result={name:zero for name,_ in f.PROCEDURE}
        result.update(data=data,head=head,pc=pc)
        return result
    return t,raw,expected


def certify(description=None):
    t,raw,expected=prepare();desc=f.self_description() if description is None else description
    actual=t.expression(desc,tuple(w for j in f.NEIGHBORHOOD for w in raw(j)))
    count=bits=0;boolean=BooleanAbstraction(t)
    for delta in f.OFFSETS:
        for name,value in expected(delta).items():
            got=actual[f.COL[f's{delta+2}_{name}']]
            if got!=value:
                for bit in range(dict(c.SCHEMA)[name]):
                    assert boolean.bit(got,bit)==boolean.bit(value,bit),('quiet barrier',delta,name,bit)
                    bits+=1
            count+=1
    assert actual[f.COL['address']]==raw(0)[f.COL['address']]
    assert actual[f.COL['age']]==t.modular_add(raw(0)[f.COL['age']],1,32)
    for name,_ in f.STATIC:assert actual[f.COL[name]]==raw(0)[f.COL[name]]
    nodes=len(boolean.b.nodes);boolean.close()
    return dict(passed=True,BDD_nodes=nodes,BDD_bit_identities=bits,all_clock_ages=f.U,all_addresses=f.Q,procedure_word_identities=count,
                unchanged_static_words=len(f.STATIC),geometry_words=2,symbolic_terms=len(t.nodes),
                reset_entry_stages=5,additional_vote_entry_age=c.VOTE_AGES[0],
                simultaneous_reset_vote_age=c.RESET_AGES[4],commit_old_age=f.U-1,
                domain='Canonical geometry; coherent arbitrary static/Data; zero heads/controllers/mail; arbitrary physical flags/Signals/Wf.',
                relation='Resets clear marked Data and bootstrap the selected entry; votes read old Data and override resets; commit copies right-neighbor Data into Info. Other quiet Data persists; mail stays zero.')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();result=certify()
    paths=[Path(__file__),Path(clock.__file__),Path(clock.regular.__file__),Path('experiments/fixed_rule/certify_small_holder_head_invariant.py')]
    result.update(descriptor_sha256=f.self_description().digest(),source_sha256={str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},
                  seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  limitation='Quiet local barrier relation only; producing the quiet state and intended Data at each barrier still requires the instruction/packet semantic induction. Context outputs are supplied by the separate all-clock boundary certificate.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
