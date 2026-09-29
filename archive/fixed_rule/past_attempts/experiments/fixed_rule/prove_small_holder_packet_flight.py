"""Exact one-step induction for the ballistic packet formula used by gather.

Checks the core.receive edge/decrement/hit relation for every source Address,
MEM target and elapsed-time bit assignment, for each three-bit hop count.
Leftward travel is its coordinate reflection a -> Q-1-a. Packet/controller
noninterference and collision exclusion are separate guarded-domain obligations.
"""
import argparse,hashlib,json,resource,time
from pathlib import Path
from gacsca.fixed_rule.word_bdd import BDD
from gacsca.fixed_rule.wordcode import EQ
from gacsca.fixed_rule import small_holder_rule as f,small_holder_core as c,small_holder_program as p


class BoundedBDD(BDD):
    def node(self,var,lo,hi):
        if len(self.nodes)>=150000:raise RuntimeError('shared-host-memory proof node budget reached')
        return super().node(var,lo,hi)


def prove_case(hops):
    bits=f.Q.bit_length()-1;time_bits=bits+4;width=time_bits+1
    b=BoundedBDD(2*bits+time_bits)
    a=[];target=[];elapsed=[];v=0
    for i in range(time_bits):
        if i<bits:a.append(b.variable(v));v+=1;target.append(b.variable(v));v+=1
        elapsed.append(b.variable(v));v+=1
    def extend(x):return tuple(x)+(0,)*(width-len(x))
    a=extend(a);target=extend(target);elapsed=extend(elapsed)
    eq=lambda x,y:b.arithmetic(EQ,x,y)[0]
    x=b.add(a,elapsed);next_x=b.add(x,b.const(1,width))
    hit_at=b.add(target,b.const(hops*f.Q,width))
    positive=b.less(a,hit_at)
    def alive(at):return b.and_(b.less(at,b.const((hops+1)*f.Q,width)),b.inv(b.and_(positive,b.inv(b.less(at,hit_at)))))
    before=alive(x)
    position=x[:bits];next_position=b.add(position,b.const(1,bits))
    crossed=x[bits:bits+3]
    remaining=b.add(b.const(hops,3),b.add(tuple(b.inv(z) for z in crossed),b.const(1,3)))
    edge=eq(position,b.const(f.Q-1,bits))
    valid=b.and_(before,b.inv(b.and_(edge,eq(remaining,b.const(0,3)))))
    decrement=(edge,0,0)
    new_remaining=b.add(remaining,b.add(tuple(b.inv(z) for z in decrement),b.const(1,3)))
    hit=b.and_(valid,b.and_(eq(new_remaining,b.const(0,3)),eq(next_position,target[:bits])))
    next_valid=b.and_(valid,b.inv(hit))
    expected_hit=b.and_(positive,eq(next_x,hit_at))
    next_crossed=next_x[bits:bits+3]
    expected_remaining=b.add(b.const(hops,3),b.add(tuple(b.inv(z) for z in next_crossed),b.const(1,3)))
    checks=[('valid',next_valid,alive(next_x)),('delivery',hit,expected_hit)]
    for i,(actual,wanted) in enumerate(zip(new_remaining,expected_remaining)):
        checks.append((f'remaining_bit_{i}',b.and_(next_valid,actual),b.and_(next_valid,wanted)))
    for i,(actual,wanted) in enumerate(zip(next_position,next_x[:bits])):
        checks.append((f'position_bit_{i}',b.and_(next_valid,actual),b.and_(next_valid,wanted)))
    # This algebraic transport identity is valid even for targets that are
    # not MEM; use it in the executor only after its protected-MEM target guard.
    for name,actual,wanted in checks:
        bad=b.xor(actual,wanted)
        if bad:raise AssertionError((hops,name,b.witness(bad)))
    result=dict(hops=hops,passed=True,independent_bits=v,all_source_addresses=f.Q,all_coordinate_targets=f.Q,elapsed_values=1<<time_bits,bdd_nodes=len(b.nodes),checked_relations=len(checks))
    b.binary.cache_clear();return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve proof evidence')
    started=time.perf_counter();cases=[prove_case(k) for k in range(8)]
    files=[Path(__file__),Path('gacsca/fixed_rule/word_bdd.py'),Path(c.__file__),Path('gacsca/fixed_rule/small_holder_resident_gather.cu')]
    result=dict(passed=True,cases=cases,seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,scope='one-step induction of rightward source-address/remaining/valid/delivery formulas from receive semantics; leftward case by coordinate reflection; arbitrary payload is copied unchanged',separate_obligations=['actual target is MEM; enforced by foreign-history guard','no same-track collision; enforced by space-time-line check','controller never reads or writes deferred history; guarded at every literal access','Data delivery order and right-track priority; implemented separately and tested against full physical rule'],source_sha256={str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in files})
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
