"""GBD6 total period rule FAMILY R_beta; not an issued own beta.

Q8192/U128Q unchanged. Every beta<=Q is finite counted immutable code.
The new output scatter and early/late controllers are explicit departures.
The complete self-programme and whole-period refinement remain unproved.
"""
from pathlib import Path
import importlib.util,sys
BASE=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('gbd6_prefix',BASE/'unregistered_gbd5/prefix_rule.py')
r=importlib.util.module_from_spec(spec);sys.modules[spec.name]=r;spec.loader.exec_module(r)
c=r.c;p=r.p;Q=r.Q;U=r.U;K=r.K;P=r.P;S=r.S
EARLY_BIRTH=r.BIRTH;EARLY_END=80*Q;CSEED=78*Q
LRESET=112*Q;LBIRTH=LRESET+1;LEND=120*Q
OLOAD=LEND;ODONE=OLOAD+p.MAX_TRAVEL
EXPAND=ODONE+1;SPREAD_END=EXPAND+19;COMMIT=U-1
FLAG_SEED=P+1
assert SPREAD_END<COMMIT

def out_packet(a,t,own,left):
    """Literal one-site, clamped right transport. Total malformed tags."""
    if t==OLOAD:
        return p.Packet(own.data&c.MASK,a-P,1) if P<=a<P+p.CHUNKS else p.ZERO
    if OLOAD<t<=ODONE:
        inside=P<=a<P+K
        hold=bool(inside and own.valid and own.tag<p.CHUNKS and a==p.source(own.tag))
        incoming=bool(inside and left.valid and left.tag<p.CHUNKS
            and P<=a-1<P+K and a-1<p.source(left.tag))
        if hold and incoming:return p.ZERO
        if incoming:return p.Packet(left.data&c.MASK,left.tag,1)
        if hold:return p.Packet(own.data&c.MASK,own.tag,1)
        return p.ZERO
    return p.ZERO

def courier(a,t,own,left,right,outword):
    """Total clamped two-bit courier; source is OLD computed-voted Out.

    The 78Q seed is an explicit schedule choice. An earlier 75Q seed is
    not justified by the inherited universal native execution bound.
    """
    if t==CSEED:
        return (((outword>>13)&1)|(((outword>>14)&1)<<1)) if a==FLAG_SEED else 0
    if not CSEED<t<98*Q:return 0
    value=0
    if FLAG_SEED<=a<=Q-3:
        value=left&1
        if a==Q-3:value|=own&1
    if 3<=a<=FLAG_SEED:
        bit=(right>>1)&1
        if a==3:bit|=(own>>1)&1
        value|=bit<<1
    return value

def local(cells,x,beta,printed=False):
    """All-raw radius<=7 equations, including mandatory wipe and WF order.

    beta is a fixed construction parameter, never a future command.
    Only centre computed native fields control its five SF output roles.
    """
    assert len(beta)<=Q
    n=r.native(cells,x,printed);t=n['age_now']
    keep=n['addr']==(cells[x].addr&(Q-1));view=r.raw_view(cells,x,n)
    sf={name:[] for name in r.FIELD_WIDTHS}
    for q,s in enumerate(S):
        y=x+s;a=(n['addr']+s)%Q
        own={name:r.vote(cells,y,name) for name in r.FIELD_WIDTHS}
        info=own['Info'];mail=own['Mailbox']&3;hist=own['History']
        if t in r.STARTS:mail=0
        elif t in tuple(z+1 for z in r.STARTS):mail=info|(info<<1)
        elif any(z<t<z+r.ACTIVE for z in r.STARTS):
            mail=(r.vote(cells,y-1,'Mailbox')&1)|(((r.vote(cells,y+1,'Mailbox')>>1)&1)<<1)
        if n['f1']:mail=0
        for g in range(3):
            if t in r.STARTS[:g+1]:hist&=~(p.HISTORY_MASK<<(17*g))
            else:
                for lane,d in enumerate(r.LANES):
                    if t==r.capture(g,d):
                        bit=info if d==0 else ((own['Mailbox']>>(0 if d<0 else 1))&1)
                        hist=(hist&~(1<<(17*g+lane)))|(bit<<(17*g+lane))
        def in_packet(at):
            tag=r.vote(cells,at,'InputTag')
            return p.Packet(r.vote(cells,at,'Mem'),tag&8191,(tag>>13)&1)
        temporal=p.majority3(*[(hist_old>>17*g)&p.HISTORY_MASK
            for g in range(3) for hist_old in (own['History'],)])
        packed=p.stage_action(a,t,in_packet(y),in_packet(y-1),in_packet(y+1),temporal)
        if t in (EARLY_BIRTH,LBIRTH):
            head=c.pack_head(c.Head(1,0,c.RUN,0,0,0,(0,)*8) if a==P+2 else c.Head())
        elif EARLY_BIRTH<t<EARLY_END or LBIRTH<t<LEND:
            head=c.pack_head(c.actor(view,x,q,beta))
        else:head=0
        out=own['Out'];otag=0;scratch=0
        if t==LRESET:out=0
        elif EARLY_BIRTH<t<EARLY_END or LBIRTH<t<LEND:
            out=c.write_out(view,x,q,beta,-2,20)
        elif OLOAD<=t<=ODONE:
            def output_packet(at):
                tag=r.vote(cells,at,'OutputTag')
                return p.Packet(r.vote(cells,at,'Out'),tag&8191,(tag>>13)&1)
            o=out_packet(a,t,output_packet(y),output_packet(y-1))
            out=o.data;otag=o.tag|(o.valid<<13)
        elif t==EXPAND:
            h=(a-P)//20
            tag=own['OutputTag']
            if P<=a<P+K and a==p.source(h) and tag==h|(1<<13):scratch=out
            out=0
        elif EXPAND<t<=SPREAD_END:
            if P<=a<P+K:
                scratch=own['Scratch']
                if (a-P)//20==(a+1-P)//20 and a+1<P+K:
                    scratch|=r.vote(cells,y+1,'Scratch')
            out=0
        elif SPREAD_END<t<COMMIT:out=0;scratch=own['Scratch']
        couriers=courier(a,t,own['Couriers'],r.vote(cells,y-1,'Couriers'),
            r.vote(cells,y+1,'Couriers'),own['Out'])
        if CSEED<t<98*Q:
            if a==Q-3:info=own['Couriers']&1
            elif a==3:info=(own['Couriers']>>1)&1
        values=dict(Info=info,Mailbox=mail,History=hist,Mem=packed.data,
            InputTag=packed.tag|(packed.valid<<13),Out=out,OutputTag=otag,
            Scratch=scratch,Couriers=couriers,Head=head)
        if t==COMMIT:
            values={name:0 for name in r.FIELD_WIDTHS}
            values['Info']=((own['Scratch']>>((a-P)%20))&1) if P<=a<P+K else 0
        for name,value in values.items():
            sf[name].append((value&((1<<r.FIELD_WIDTHS[name])-1)) if keep else 0)
    # This consumes FINAL computed self Info, after every branch and wipe.
    pulse=96*Q<=t<98*Q;final_info=sf['Info'][0]
    wf1=int(pulse and n['addr']==Q-3 and final_info)
    wf2=int(pulse and n['addr']==3 and not n['f1'] and final_info)
    return r.Cell(n['addr'],n['age'],n['f1'],n['f2'],wf1,wf2,
        **{name:tuple(values) for name,values in sf.items()})
