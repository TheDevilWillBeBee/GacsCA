"""Full raw local reset identity, for arbitrary coherent Data and static records.

Diagnostic only. This proves the final reset step under explicit clean boundary
hypotheses, not retrieval/computation correctness for an entire work period.
"""
import argparse,hashlib,json,resource,time
from pathlib import Path
from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c
from gacsca.fixed_rule.word_bdd import BDD
from gacsca.fixed_rule.wordcode import EQ
from experiments.fixed_rule.prove_small_holder_boundary import validate


def prove(description=None):
    desc=f.self_description() if description is None else description;validate(desc)
    # Free local Address, six stationary colony Signals, nine logical Data words,
    # and every word of each local static record. No ROM metadata word is
    # fixed to zero in the center, including index, b, d and last.
    static_widths={name:dict(c.SCHEMA)[name] for name in c.STATIC}
    widths=[15,6]+[64]*9+[static_widths[name] for _ in range(7) for name in c.STATIC]
    b=BDD(sum(widths));cursor=0
    def variable(width):
        nonlocal cursor
        word=tuple(b.variable(cursor+i) for i in range(width))+(0,)*(64-width);cursor+=width;return word
    address=variable(15);signals=variable(6)
    data={i:variable(64) for i in range(-4,5)}
    metadata={i:{name:variable(static_widths[name]) for name in c.STATIC} for i in f.STATIC_OFFSETS}
    assert cursor==b.variables
    zero=b.const(0);one=b.const(1)
    def at(d):return b.add(address,b.const(d&((1<<64)-1)))[:15]+(0,)*49
    def eq(a,v):return b.arithmetic(EQ,a,b.const(v))[0]
    def colony_bit(d,side):
        same=signals[side*3+1]
        if d<0:return b.ite(b.less(address,b.const(-d)),signals[side*3],same)
        if d>0:return b.ite(b.inv(b.less(address,b.const(f.Q-d))),signals[side*3+2],same)
        return same
    def signal(d):
        a=at(d)
        return tuple(b.or_(b.and_(eq(a,5-k),colony_bit(d,0)),b.and_(eq(a,f.Q-1-k),colony_bit(d,1))) for k in range(5))+(0,)*59
    words=[];center=None
    for j in f.NEIGHBORHOOD:
        row={name:zero for name,_ in f.SCHEMA};row['address']=at(j);row['signal']=signal(j)
        for d in f.OFFSETS:row[f's{d+2}_data']=data.get(j+d,zero)
        # Only the center's raw static records enter its procedure calculation.
        if j==0:
            for d,values in metadata.items():
                for name,value in values.items():row[f'p{d+3}_{name}']=value
            center=row.copy()
        words.extend(row[name] for name,_ in f.SCHEMA)
    expected=dict(center);expected['age']=one
    for d in f.OFFSETS:
        record=metadata[d];first=record['first'][0]
        erase=b.or_(first,b.and_(eq(record['kind'],c.MEM),record['a'][0]))
        expected[f's{d+2}_data']=tuple(b.ite(erase,0,bit) for bit in data[d])
        expected[f's{d+2}_head']=record['first']
        expected[f's{d+2}_pc']=tuple(b.and_(first,bit) for bit in record['a'][:32])+(0,)*32
    actual=b.evaluate(desc,tuple(words))
    for (name,_),got in zip(f.SCHEMA,actual):
        for bit,(a,wanted) in enumerate(zip(got,expected[name])):
            if a!=wanted:
                witness=b.witness(b.xor(a,wanted));b.binary.cache_clear()
                raise AssertionError((name,bit,witness))
    # All static outputs are literal center-input aliases in the full descriptor;
    # independently confirming that no projection or omitted static output is hidden.
    for name,_ in f.STATIC:
        assert desc.outputs[f.COL[name]]==7*f.FIELDS+f.COL[name],name
    result=dict(passed=True,independent_bits=b.variables,BDD_nodes=len(b.nodes),complete_raw_outputs=f.FIELDS,
        all_addresses=f.Q,arbitrary_logical_data_words=9,arbitrary_complete_static_records=7,arbitrary_colony_signal_bits=6,
        descriptor_sha256=desc.digest(),hypotheses='Age 0; canonical Addresses; all physical flags, Wf, heads, other controllers and mail zero; coherent Data; stationary five-holder colony Signal pattern. Every static field of all seven center records is arbitrary; other holders static fields are unused by the center update.',
        conclusion='Age 1; geometry and Signals retained; each procedure Data cleared iff local first or MEM with a bit0; head=first; pc=first times low32(a); all other controller/mail/Wf fields zero; all static words retained.',
        limitation='Only one local reset transition. No all-input complete-work-period theorem or nested trajectory shortcut is claimed.')
    b.binary.cache_clear();return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();result=prove();result.update(seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
