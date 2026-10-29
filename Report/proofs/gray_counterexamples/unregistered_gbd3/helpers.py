"""Issued GBD3 generic FGET/FPUT software, one counted binary stream.

These helpers are actual instruction sequences, not new ISA primitives.
They assume a coherent prepared lower bank and canonical computed ports;
they do not supply packing, beta self-emission or an autonomous period.
"""
import controller as k
import layout as l


def field_get_rows():
    # R0: raw field-bit base, R1: count, R2: lane centre.
    # R4/R6/R7 are preserved. No nested CALL or virtual work bank.
    return [('LIT',3,5,20),('ALU',10,3,0,3),
            ('LIT',5,5,20),('ALU',9,0,0,5),
            ('LIT',5,12,l.P+2),('ALU',0,0,0,5),
            ('MOVE',0),('READQ',0,2,3,1,1),('RET',)]


def field_put_rows():
    # R0: data, R1: count, R2: raw output-bit base, including copy slot.
    # R0/R1/R4/R6/R7 are preserved. WRITE uses base-2/cap20.
    return [('LIT',3,5,20),('ALU',10,3,2,3),
            ('LIT',5,5,20),('ALU',9,2,2,5),
            ('LIT',5,12,l.P+2),('ALU',0,2,2,5),
            ('MOVE',2),('WRITE',0,3,1,1),('RET',)]


def bits(rows):
    return tuple(b for row in rows for b in k.encode(*row))


def caller(raw_base,count,slot,lane=8):
    assert 0<=raw_base<4096 and 0<=count<=20
    assert 0<=slot<5 and 2<=lane<=14
    get=field_get_rows();put=field_put_rows()
    # CALLs have fixed width17, so label addresses have no circular
    # variable-length assembly dependency.
    driver=[('LIT',0,12,raw_base),('LIT',1,5,count),
            ('LIT',2,4,lane),('CALL',0),
            ('LIT',2,12,raw_base+slot),('CALL',0),('HALT',)]
    g=len(bits(driver));p=g+len(bits(get))
    driver[3]=('CALL',g);driver[5]=('CALL',p)
    beta=bits(driver+get+put)
    assert (len(bits(get)),len(bits(put)))==(140,137)
    assert (g,p,len(beta))==(119,259,396)
    return driver+get+put,beta,dict(FGET=g,FPUT=p)


def contracts(raw_base,count,slot):
    """Exact travel/update accounting for the issued single-head caller.

    Entry is P+2. MOVE consumes an instruction update; if its target
    already equals its location, it still takes one settling update.
    Arrival from another site settles on that travel update.
    """
    assert 0<=raw_base<l.K and 0<=slot<5 and 0<=count<=20
    assert raw_base+5*max(0,count-1)+4<l.K
    entry=l.P+2;source=l.P+raw_base//20+2
    destination=l.P+(raw_base+slot)//20+2
    instructions=7+9+9
    travel_get=max(1,source-entry)
    travel_put=max(1,abs(destination-source))
    # slot<=4, hence destination-source is0 or1.
    assert 0<=destination-source<=1 and travel_put==1
    return dict(entry=entry,source=source,destination=destination,
                instructions=instructions,FGET_travel=travel_get,
                FPUT_travel=travel_put,updates=instructions+travel_get+travel_put,
                FGET_preserved_registers=[1,2,4,6,7],
                FPUT_preserved_registers=[0,1,4,6,7],
                beta_bits=396,FGET_bits=140,FPUT_bits=137,
                real_single_link=True,nested_calls=False)
