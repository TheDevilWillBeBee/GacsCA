"""Finite cofactors accompanying the universal generic WORDOUT contract.

The written algebra, not sampled payloads, quantifies all Word20 data.
This checker exhausts descriptor widths/control boundaries, verifies
arbitrary unused-packet preservation, and checks actual physical holders.
No whole own-beta, universal complete emitter or period theorem follows.
"""
from dataclasses import asdict,replace
from hashlib import sha256
from pathlib import Path
import argparse,json,time
import compact_completion_rule as b


def reference_pending(p,address):
    stride=1+4*p.kind
    if p.kind>=2 or p.index>=20 or p.start+p.index*stride>=b.Q:
        return b.fail(p),None
    if address!=p.start:return b.move_to(p,address,p.start),None
    new=replace(p,b=p.b>>1)
    if p.index==0:return b.continue_pc(new,p.ret),p.b&1
    return replace(new,start=p.start+stride,index=p.index-1,move=1),p.b&1


def run(output):
    t0=time.monotonic();mem={d:0 for d in range(-4,5)}
    empty=(0,)*b.Q;counts={'encode_decode':0,'pending':0,'entry':0,'physical_holder':0}
    digest=sha256()
    seed=b.Packet(p=1,mode=b.WORDOUT,pc=17,ret=77,a=b.MASK-37,
                  buf=3,lane=31,fn=13,work=(1<<407)-63,nc=(1<<35)-11)
    values=(0,1,2,3,1<<19,b.MASK,b.MASK//3)
    for width in range(32):
        for wide in (0,1):
            bits=b.encode('PUTWORD',width,wide)
            beta=bits+(0,)*(b.Q-len(bits))
            assert len(bits)==17 and b.decode(beta,0)==('PUTWORD',(width,wide),17)
            counts['encode_decode']+=1
    for kind in range(4):
        for index in (0,1,18,19,20,8191):
            stride=1+4*kind
            edge=b.Q-1-index*stride
            starts=sorted({0,1,100,b.Q-1,*(x for x in (edge-1,edge,edge+1) if 0<=x<b.Q)})
            for start in starts:
                for address in sorted({0,start,min(b.Q-1,start+1),max(0,start-1),b.Q-1}):
                    for value in values:
                        p=replace(seed,kind=kind,index=index,start=start,b=value)
                        got=b.cpu(p,address,mem,empty)
                        want=reference_pending(p,address)
                        assert got==want,(asdict(p),address,got,want)
                        counts['pending']+=1
                        digest.update(repr((p,address,got)).encode())
    for width in range(32):
        for wide in (0,1):
            bits=b.encode('PUTWORD',width,wide);beta=bits+(0,)*(b.Q-len(bits))
            ntests=range(32) if width==0 else (width,)
            for n in ntests:
                stride=1+4*wide
                edge=b.Q-1-(n-1)*stride
                starts=sorted({0,100,b.Q-1,b.Q,b.MASK,
                               *(x for x in (edge-1,edge,edge+1) if 0<=x<=b.MASK)})
                for start in starts:
                    descriptors=(start,)
                    if width==0:
                        descriptors=tuple((start&8191)|(n<<13)|(pad<<18) for pad in range(4))
                    for descriptor in descriptors:
                        p=replace(seed,mode=b.RUN,pc=0,a=b.MASK//3,b=descriptor)
                        got,write=b.cpu(p,100,mem,beta)
                        effective=(descriptor>>13)&31 if width==0 else width
                        at=descriptor&8191 if width==0 else descriptor
                        valid=(width!=0 or descriptor<1<<18) and 1<=effective<=20 and at<b.Q and at+(effective-1)*stride<b.Q
                        want=b.move_to(replace(p,mode=b.WORDOUT,start=at,index=effective-1,
                                              kind=wide,b=p.a,ret=17),100,at) if valid else b.fail(p)
                        assert got==want and write is None,(width,wide,descriptor,got,want)
                        counts['entry']+=1
                        digest.update(repr((width,wide,p,got)).encode())
    # Raw holder reads: source logical c lies in[-3,3], each stored Head
    # copy is at x+c-SLOTS[q]. All possible coordinates have abs<=5.
    # Each output bit's selected five-copy vote is checked on every 5bit
    # payload. WORDOUT itself never reads History or new neighbouring CPU.
    radius=set()
    for centre in (-3,-2,-1,0,1,2,3):
        for bit in (0,3,32,45,69,91,110,552):
            for payload in range(32):
                cells={j:b.Cell(addr=(100+j)%b.Q,age=112*b.Q+1) for j in b.LANES}
                for q,s in enumerate(b.SLOTS):
                    x=centre-s;radius.add(x)
                    z=list(cells[x].head);z[q]=((payload>>q)&1)<<bit
                    cells[x]=replace(cells[x],head=tuple(z))
                actual=b.voted(cells,centre,'head')>>bit&1
                assert actual==int(payload.bit_count()>=3)
                counts['physical_holder']+=1
    assert max(map(abs,radius))==5
    out={'passed':True,'Q':b.Q,'U':b.U,'lambda':24,'c':104,
         'scope':'generic WORDOUT finite cofactors; universal data algebra in proof',
         'counts':counts,'cofactor_sha256':digest.hexdigest(),
         'head_bits':b.HEAD_BITS,'frame_bits':b.FRAME_BITS,
         'new_head_holder_radius':5,'new_data_reads':0,
         'source_sha256':{str(p):sha256(p.read_bytes()).hexdigest() for p in
                          (Path(__file__),Path(b.__file__))},
         'universal_complete_emitter_equivalence':False,'whole_own_beta':False,
         'physical_period':False,'gray_refutation':False,'iid_failure':False,
         'elapsed_seconds':time.monotonic()-t0}
    output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    run(p.parse_args().output)
