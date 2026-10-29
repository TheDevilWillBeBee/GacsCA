"""GH0: an isolated interior-layout version of Gray's p31 hardwirer.

Q8192/U128Q/lambda24/c104 stay fixed. This is a concrete finite courier,
not an own-programme compiler or a completed Gray rule. Native computed
controls and GT0's ordinary SimBit output remain explicit integration
inputs. Programme access is to five physical raw-holder ProgrammeBits;
in the projected version those bits are functions of that holder's RAW GF.
No large instruction ROM, head-centre lookup or whole-rule Apply is used.
"""
from dataclasses import dataclass
from gacsca.netlist import Net,Compiled,at_least,const_word,w_eq,w_eq_const,w_mux,w_add_const,w_in_range
import gray_raw_gather as gt

Q=8192;U=128*Q;LAMBDA=24;C=104;SLOTS=gt.SLOTS
ADDR_START=3958;ADDR_END=3970;ACTIVE_END=16*Q;BIRTH=2
COLLECT=0;HOME=1;SCAN=2;BACK=3;DONE=4;ERROR=5
HEAD_BITS=18;FRAME_BITS=gt.FRAME_BITS+5*HEAD_BITS
MODE_SHIFT=1;ADDRESS_SHIFT=4;VALUE_SHIFT=17
RESETS=tuple(s[0] for s in gt.STAGES)


@dataclass(frozen=True)
class Packet:
    present:int=0;mode:int=COLLECT;address:int=0;value:int=0


def pack(p):
    return (p.present&1)|((p.mode&7)<<MODE_SHIFT)|((p.address&8191)<<ADDRESS_SHIFT)|((p.value&1)<<VALUE_SHIFT)


def unpack(word):
    return Packet(word&1,(word>>MODE_SHIFT)&7,(word>>ADDRESS_SHIFT)&8191,(word>>VALUE_SHIFT)&1)


def majority(words):
    a,b,c,d,e=words
    # Bitwise 3/5, for an entire finite word or a one-bit field.
    return (a&b&c)|(a&b&d)|(a&b&e)|(a&c&d)|(a&c&e)|(a&d&e)|(b&c&d)|(b&c&e)|(b&d&e)|(c&d&e)


def direction(p):
    if not p.present:return 0
    return 1 if p.mode in (COLLECT,SCAN) else -1 if p.mode in (HOME,BACK) else 0


def head_step(p,address,simbit,programmebit):
    """Total finite controller. Returns next packet and one-time aux write."""
    if not p.present:return Packet(),False,0
    mode=p.mode;data=p.address;value=p.value
    if mode==COLLECT:
        bit=address-ADDR_START
        if not 0<=bit<13:return Packet(1,ERROR,data,value),False,0
        data=(data&~(1<<bit))|((simbit&1)<<bit)
        return Packet(1,HOME if bit==12 else COLLECT,data,value),False,0
    if mode==HOME:
        if address:return p,False,0
        if data:return Packet(1,SCAN,data,value),False,0
        return Packet(1,DONE,data,programmebit&1),True,programmebit&1
    if mode==SCAN:
        if address>data:return Packet(1,ERROR,data,value),False,0
        if address<data:return p,False,0
        if not address:return Packet(1,DONE,data,programmebit&1),True,programmebit&1
        return Packet(1,BACK,data,programmebit&1),False,0
    if mode==BACK:
        if address:return p,False,0
        return Packet(1,DONE,data,value),True,value
    if mode==DONE:return p,False,0
    return Packet(1,ERROR,data,value),False,0


def projected_programme(raw_gf,slot,beta):
    assert len(beta)==Q
    return beta[((raw_gf&8191)+slot)%Q]&1


def incoming(packets):
    # Source offsets0,-1,+1, with the first candidate retained on collision.
    candidates=[p for delta,p in zip((0,-1,1),packets)
        if p.present and direction(p)==-delta]
    if not candidates:return Packet()
    first=candidates[0]
    return Packet(1,ERROR,first.address,first.value) if len(candidates)>1 else first


def scalar(cells,computed_address,computed_age,wipe,beta,base_simbit=None):
    """Actual raw-holder accesses. cells[j]=(rawGF, SimBit[5], Head[5]).

    base_simbit is the already computed GT0 output at this same holder;
    its producer is not an upper-state callback. If omitted, use the
    five-holder current SimBit vote, as on the certified early prefix.
    """
    assert set(cells)==set(range(-5,6)) and len(beta)==Q
    age=computed_age&((1<<20)-1);phase=computed_address&8191
    def voted(field,y):return majority([cells[y-t][field][i] for i,t in enumerate(SLOTS)])
    def programme(y):return majority([projected_programme(cells[y-t][0],t,beta) for t in SLOTS])
    heads=[];sim=[];enable=[];values=[]
    for q,s in enumerate(SLOTS):
        address=(phase+s)%Q;we=False;value=0
        if age in RESETS:p=Packet()
        elif age==BIRTH:p=Packet(1,COLLECT,voted(1,s)&1,0) if address==ADDR_START else Packet()
        elif BIRTH<age<ACTIVE_END:
            p=incoming([unpack(voted(2,s+d)) for d in (0,-1,1)])
            p,we,value=head_step(p,address,voted(1,s),programme(s))
        else:p=unpack(voted(2,s))
        old=voted(1,s)&1 if base_simbit is None else base_simbit[q]&1
        heads.append(0 if wipe else pack(p));enable.append(int(we and not wipe));values.append(value&1 if we and not wipe else 0)
        sim.append(0 if wipe else value&1 if we else old)
    return dict(head=tuple(heads),simbit=tuple(sim),write_enable=tuple(enable),write_value=tuple(values))


def less(n,a,b):
    prefix=1;answer=0
    for x,y in zip(reversed(a),reversed(b)):
        answer=n.OR(answer,n.AND(prefix,n.AND(n.NOT(x),y)))
        prefix=n.AND(prefix,n.NOT(n.XOR(x,y)))
    return answer


def build(n,cells,address,age,wipe,base):
    """Emitted Boolean map with physical ProgrammeBit inputs.

    cells[j]['programme'][q] means PB of the ACTUAL holder j, copy q.
    The projected wrapper computes it from that holder's raw GF; it
    never substitutes the repaired logical/head-centre Address.
    """
    cache={}
    def vote(f,y,b=0):
        key=f,y,b
        if key not in cache:
            cache[key]=at_least(n,[cells[y-t][f][i*HEAD_BITS+b if f=='head' else i]
                for i,t in enumerate(SLOTS)],3)
        return cache[key]
    def word(y):return [vote('head',y,b) for b in range(HEAD_BITS)]
    reset=n.any(w_eq_const(n,age,v) for v in RESETS)
    birth=w_eq_const(n,age,BIRTH);active=w_in_range(n,age,BIRTH+1,ACTIVE_END)
    result={}
    for q,s in enumerate(SLOTS):
        g=w_add_const(n,address,s%Q)
        candidates=[];conditions=[]
        for d in (0,-1,1):
            h=word(s+d);m=h[1:4]
            modes=(DONE,ERROR,6,7) if d==0 else (COLLECT,SCAN) if d==-1 else (HOME,BACK)
            conditions.append(n.AND(h[0],n.any(w_eq_const(n,m,z) for z in modes)))
            candidates.append(h)
        selected=[0]*HEAD_BITS
        for condition,h in reversed(list(zip(conditions,candidates))):selected=w_mux(n,condition,h,selected)
        multiple=n.any(n.AND(conditions[i],conditions[j]) for i in range(3) for j in range(i+1,3))
        p=selected[0];m=selected[1:4];a=selected[4:17];v=selected[17]
        eq={z:w_eq_const(n,m,z) for z in range(8)}
        zero=w_eq_const(n,g,0);same=w_eq(n,g,a);below=less(n,g,a);a0=w_eq_const(n,a,0)
        collecting=n.AND(eq[COLLECT],w_in_range(n,g,ADDR_START,ADDR_END+1))
        next_a=[n.MUX(n.AND(collecting,w_eq_const(n,g,ADDR_START+b)),vote('simbit',s),a[b]) for b in range(13)]
        collect_last=n.AND(collecting,w_eq_const(n,g,ADDR_END))
        home_done=n.AND(eq[HOME],n.AND(zero,a0))
        scan_match=n.AND(eq[SCAN],same)
        scan_done=n.AND(scan_match,zero)
        back_done=n.AND(eq[BACK],zero)
        done=n.any((home_done,scan_done,back_done,eq[DONE]))
        scan=n.OR(n.AND(eq[HOME],n.AND(zero,n.NOT(a0))),n.AND(eq[SCAN],below))
        home=n.OR(collect_last,n.AND(eq[HOME],n.NOT(zero)))
        back=n.OR(n.AND(scan_match,n.NOT(zero)),n.AND(eq[BACK],n.NOT(zero)))
        collect=n.AND(collecting,n.NOT(collect_last))
        next_m=const_word(ERROR,3)
        for cond,mode in ((collect,COLLECT),(home,HOME),(scan,SCAN),(back,BACK),(done,DONE)):
            next_m=w_mux(n,cond,const_word(mode,3),next_m)
        # A collision must not perform a write or consume collected bits.
        next_a=w_mux(n,multiple,a,next_a)
        next_m=w_mux(n,multiple,const_word(ERROR,3),next_m)
        fetch=n.OR(home_done,scan_match)
        next_v=n.MUX(multiple,v,n.MUX(fetch,vote('programme',s),v))
        changed=[p]+next_m+next_a+[next_v]
        changed=[n.AND(p,b) for b in changed]
        born=[1]+const_word(COLLECT,3)+[vote('simbit',s)]+[0]*12+[0]
        born=[n.AND(w_eq_const(n,g,ADDR_START),b) for b in born]
        output=w_mux(n,reset,[0]*HEAD_BITS,w_mux(n,birth,born,w_mux(n,active,changed,word(s))))
        we=n.AND(active,n.AND(p,n.AND(n.NOT(multiple),n.any((home_done,scan_done,back_done)))))
        we=n.AND(we,n.NOT(wipe))
        val=n.MUX(back_done,v,vote('programme',s))
        for b,bit in enumerate(output):result['head',s,b]=n.AND(bit,n.NOT(wipe))
        result['write_enable',s,0]=we
        result['write_value',s,0]=n.AND(we,val)
        result['simbit',s,0]=n.AND(n.MUX(we,val,base[q]),n.NOT(wipe))
    return result


def netlist():
    n=Net();cells={j:{f:[n.input(('x',j,f,b)) for b in range(5*(HEAD_BITS if f=='head' else 1))]
        for f in ('head','simbit','programme')} for j in range(-5,6)}
    address=[n.input(('computed_address',b)) for b in range(13)]
    age=[n.input(('computed_age',b)) for b in range(20)]
    wipe=n.input(('native_wipe',))
    base=[n.input(('base_simbit',s)) for s in SLOTS]
    outputs=build(n,cells,address,age,wipe,base)
    for name,node in outputs.items():n.set_output(('y',)+name,node)
    return n


def compiled():return Compiled(netlist())


def layout():
    old=gt.preliminary_layout();assert min(old.values())==ADDR_START
    tags=list(old)+[('hardwire_head',b) for b in range(5*HEAD_BITS)]
    answer={tag:ADDR_START+i for i,tag in enumerate(tags)}
    assert all(answer[tag]==place for tag,place in old.items())
    assert len(answer)==FRAME_BITS==367 and max(answer.values())==4324
    return answer


def completion_age(address):return BIRTH+12+ADDR_END+2*(address&8191)


def logical_run(address,beta,changed_simbit=None):
    """Exact quiet reference execution for one colony; real raw accesses
    are checked independently by the physical checker and projection map.
    """
    p=Packet(1,COLLECT,address&1,0);position=ADDR_START;age=BIRTH;history=[]
    while p.mode!=DONE:
        old=p;position+=direction(p);age+=1
        b=position-ADDR_START
        sim=((address>>b)&1) if 0<=b<13 else 0
        if changed_simbit is not None and position==changed_simbit:sim=1
        p,we,value=head_step(p,position,sim,beta[position])
        history.append((age,position,pack(old),pack(p),int(we),value))
        assert p.mode!=ERROR and 0<=position<Q and age<ACTIVE_END
    assert age==completion_age(address) and p.address==address and p.value==beta[address]
    assert history[-1][4:]==(1,beta[address])
    return history
