"""Complete raw WordCode for the alphabet-extended physical lookup successor."""
from functools import lru_cache

from ..wordcode_and import Builder,LIT,Program
from ..word_prune import prune
from .. import stream28_dual_holder_rule20 as holder
from . import description as corrected
from . import successor as rule
from .lookup_bus import ADDRESS_SOURCE


@lru_cache(maxsize=1)
def build():
    old=corrected.build()
    b=Builder(15*rule.FIELDS)
    zero,one=b.const(0),b.const(1)
    base=[]
    for i in range(old.inputs):
        neighbor,field=divmod(i,rule.base_rule.FIELDS)
        base.append(neighbor*rule.FIELDS+field)
    for op,a,d in old.operations:
        base.append(b.const(a) if op==LIT else b.op(op,base[a],base[d]))
    out=[base[i] for i in old.outputs]
    bus_names=[name for name,_ in rule.BUS_SCHEMA]
    bus_out={name:(7*rule.FIELDS+rule.base_rule.FIELDS+i)
             for i,name in enumerate(bus_names)}
    def at(j,name):
        if isinstance(name,int):return (j+7)*rule.FIELDS+name
        return (j+7)*rule.FIELDS+rule.base_rule.FIELDS+bus_names.index(name)
    def eq(x,value):return b.eq(x,b.const(value))
    c_age=at(0,holder.COL['age'])
    c_address=at(0,holder.COL['address'])
    first=eq(c_age,0)
    broadcast=b.all(b.lt(zero,c_age),b.lt(c_age,b.const(rule.Q)))
    request=eq(c_age,rule.Q)
    flight=b.all(b.lt(b.const(rule.Q),c_age),
                 b.lt(c_age,b.const(2*rule.Q+1)))
    commit=eq(c_age,2*rule.Q+1)
    launch=b.all(first,eq(c_address,ADDRESS_SOURCE))
    value=b.mask(at(0,holder.COL['s2_data']),13)
    bus_out['broadcast_valid']=b.select(first,launch,
                               b.select(broadcast,at(-1,'broadcast_valid'),
                                        b.select(request,zero,at(0,'broadcast_valid'))))
    bus_out['broadcast_value']=b.select(launch,value,
                               b.select(broadcast,at(-1,'broadcast_value'),
                                        at(0,'broadcast_value')))
    bus_out['lookup_address']=b.select(launch,value,
                              b.select(b.all(broadcast,at(-1,'broadcast_valid')),
                                       at(-1,'broadcast_value'),at(0,'lookup_address')))

    def packet(j):
        own_age=at(j,holder.COL['age'])
        own_address=at(j,holder.COL['address'])
        phase_first=eq(own_age,0)
        phase_request=eq(own_age,rule.Q)
        phase_flight=b.all(b.lt(b.const(rule.Q),own_age),
                           b.lt(own_age,b.const(2*rule.Q+1)))
        left={name:at(j-1,name) for name in
              ('packet_valid','packet_source','packet_target',
               'packet_field','packet_fetched','packet_value')}
        target=b.mask(b.add(at(j,'lookup_address'),
                    b.add(at(j,'lookup_neighbor'),b.const(-7))),13)
        match=b.all(phase_flight,left['packet_valid'],
                    b.not_(left['packet_fetched']),
                    b.eq(left['packet_target'],own_address))
        # A fixed 9-bit binary mux avoids routing the raw packet_field word
        # to every one of the 433 leaves. Out-of-range selectors read zero,
        # matching the literal rule on its entire typed 0..511 field domain.
        leaves=[at(j,field) if field<rule.FIELDS else zero
                for field in range(1<<9)]
        for bit in range(9):
            choose_high=b.nonzero(b.band(left['packet_field'],
                                         b.const(1<<bit)))
            leaves=[b.select(choose_high,leaves[i+1],leaves[i])
                    for i in range(0,len(leaves),2)]
        selected=leaves[0]
        updated_value=b.select(match,selected,left['packet_value'])
        updated_fetched=b.select(match,one,left['packet_fetched'])
        def phase(name,request_value,flight_value):
            return b.select(phase_request,request_value,
                            b.select(phase_flight,flight_value,at(j,name)))
        return dict(packet_valid=b.select(phase_first,zero,
                    phase('packet_valid',at(j,'lookup_enable'),left['packet_valid'])),
                    packet_source=phase('packet_source',own_address,left['packet_source']),
                    packet_target=phase('packet_target',target,left['packet_target']),
                    packet_field=phase('packet_field',at(j,'lookup_field'),left['packet_field']),
                    packet_fetched=phase('packet_fetched',zero,updated_fetched),
                    packet_value=phase('packet_value',zero,updated_value))

    current_packet=packet(0)
    for d in holder.OFFSETS:
        destination=b.mask(b.add(c_address,b.const(d)),13)
        write=b.all(commit,at(d,'packet_valid'),at(d,'packet_fetched'),
                    b.eq(at(d,'packet_source'),destination))
        index=holder.COL[f's{d+2}_data']
        out[index]=b.select(write,at(d,'packet_value'),out[index])
    bus_out.update(current_packet)
    bus_out['packet_valid']=b.select(commit,zero,bus_out['packet_valid'])
    compact=prune(b.finish(tuple(out)+tuple(bus_out[name] for name in bus_names)))
    return Program(compact.inputs,compact.operations,compact.outputs)
