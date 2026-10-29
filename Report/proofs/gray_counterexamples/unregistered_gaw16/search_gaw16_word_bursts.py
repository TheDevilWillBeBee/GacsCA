"""Actual chronological 16x16 bursts; full Word100 Programme operands.

Diagnostic only: same frozen CA/native batch as GAW15. Every replacement
is installed on its genuine current row; no future controller is supplied.
"""
from pathlib import Path
from dataclasses import replace
import hashlib,json,sys,time
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw16'
sys.path.insert(0,str(S.parent/'unregistered_gaw15'))
import search_gaw15_phase_packets as previous
import continue_gaw15_phase_packets as continuation
k=previous.k;own=previous.own;base=previous.base;prior=previous.prior
P=previous.P;T=previous.T;MASK1700=(1<<1700)-1
STORE_PC=3566
assert k.decode(k.beta_word(own.ROM,STORE_PC))==('STX',(0,P,11,0))
assert k.decode(k.beta_word(own.ROM,STORE_PC+1))==('ALUI',(11,k.ALU['ADD'],11,1))

def recipes():
    return [
      dict(tag='word_program16',start=P+k.FIELD['info'],width=16,rows=16,
          profile='canonical',clocks='actual',heads='programme-read',banks='retained',Out=0,Info=None,Programme=k.MASK),
      dict(tag='cycle_commit_capture16',start=P-7,width=16,rows=16,
          profile='alternating',clocks='cycle',heads='fork-eval',banks='SF-independent',Out=1,Info=1,Programme=(1<<99)|1),
      dict(tag='word_source16',start=k.Q-8,width=16,rows=16,
          profile='boundary-fork',clocks='source',heads='fork-eval',banks='full-independent',Out=1,Info=1,Programme=k.MASK),
      dict(tag='interacting_eval16',start=k.Q-8,width=16,rows=16,
          profile='wide-fork',clocks='active-fork',heads='fork-eval',banks='retained',Out=1,Info=None,Programme=(1<<99)|0x15555)]

def shift(recipe,x,t):
    profile=recipe['profile'];side=x<recipe['start']+8
    if profile=='canonical':return 0
    if profile=='alternating':return 1 if (x+t)%2==0 else -1
    if profile=='boundary-fork':return 1 if side else -1
    if profile=='wide-fork':return 1 if side else k.Q//2-1
    raise AssertionError(profile)

def age(recipe,x,t):
    clocks=recipe['clocks']
    if clocks=='actual':return T+t
    if clocks=='cycle':return (k.U-1,72*k.Q+1,72*k.Q+2,102*k.Q+1)[t%4]
    if clocks=='source':return 96*k.Q+t
    if clocks=='active-fork':return T+t+(4*k.Q if x>=recipe['start']+8 else 0)
    raise AssertionError(clocks)

def replacement(recipe,x,t,old):
    delta=shift(recipe,x,t);heads=[]
    for slot in k.SLOTS:
        y=x+slot;regs=[0]*16
        if recipe['heads']=='programme-read':
            regs[11]=y%k.Q-P
            assert 6<=regs[11]<k.FRAME_WORDS
            p=k.Packet(p=1,mode=k.SEEK,pc=STORE_PC,target=y%k.Q,
                args=k.descriptor(0,dst=0,source=3),regs=tuple(regs))
        else:
            regs[0]=1;regs[11]=0;regs[13]=0
            p=k.Packet(p=1,mode=k.RUN,pc=0 if y%2==0 else own.ROM.early_pc,
                move=1 if y<k.Q else 2,regs=tuple(regs))
        heads.append(k.pack(p))
    data=dict(addr=(x+delta)%k.Q,age=age(recipe,x,t),f1=0,f2=0,wf1=0,wf2=0,
        heads=tuple(heads),out=(recipe['Out'],)*5,scratch=(k.MASK,)*5,program=(recipe['Programme'],)*5)
    if recipe['Info'] is not None:data['info']=(recipe['Info'],)*5
    if recipe['banks']!='retained':
        banks={n:[] for n in ('mem','history1','history2','history3')}
        alternating=sum(((k.MASK//3) if j%2 else (2*k.MASK//3))<<(100*j) for j in range(17))
        for h,slot in enumerate(k.SLOTS):
            y=x+slot;native=P<=y%k.Q<P+6
            if recipe['banks']=='SF-independent' and native:
                for name in banks:banks[name].append(getattr(old,name)[h])
            else:
                for name,value in zip(banks,(alternating,MASK1700,0,alternating)):banks[name].append(value)
        data.update({n:tuple(v) for n,v in banks.items()})
    return replace(old,**data)

class Phase(previous.Phase):
    def __init__(self,recipe):
        self.words={};self.support=set();self.burst_recipe=recipe
        bootstrap=dict(tag=recipe['tag'],start=recipe['start'],width=16,rows=1,gf_shift=0,
            age=T,flags=0,packet_kind='stationary-store',Out=1,Scratch=k.MASK)
        super().__init__(bootstrap)
        originals={v['x']:k.cell_from_words([int(q,16) for q in v['old_complete_words']]) for v in self.payload}
        self.recipe=recipe;self.payload=[];self.fault(0,originals)

    def raw(self,x):
        z=super().raw(x)
        return replace(z,program=self.words[x]) if x in self.words else z

    def logical(self,name,y):
        if name!='program':return super().logical(name,y)
        values=[]
        for h,slot in enumerate(k.SLOTS):
            x=y-slot
            values.append(self.words[x][h] if x in self.words else (self.pb[x-self.offset]>>h)&1)
        return k.vote(values)

    def fault(self,t,originals=None):
        assert self.age==T+t
        for x in range(self.recipe['start'],self.recipe['start']+16):
            old=originals[x] if originals is not None else self.raw(x)
            z=replacement(self.recipe,x,t,old);assert z!=old
            self.a[x-self.offset]=previous.Site(z.addr,z.age,z.f1,z.f2,z.wf1,z.wf2,0)
            self.words[x]=z.program
            # C never consumes old Programme; this bit byte is merely the
            # fallback for sites without a full-word replacement.
            self.pb[x-self.offset]=sum((v&1)<<h for h,v in enumerate(z.program))
            for h,slot in enumerate(k.SLOTS):
                y=x+slot;row=self.diff.setdefault(y,{})
                for name in previous.FIELDS:
                    values=list(row.get(name,(self.clean(name,y),)*5));values[h]=getattr(z,name)[h];row[name]=tuple(values)
            self.payload.append(dict(x=x,t=T+t,old_complete_words=[hex(v) for v in k.cell_words(old)],
                replacement_complete_words=[hex(v) for v in k.cell_words(z)]));self.support.add((x,T+t))
        self.normalize()

    def step(self,check=False):
        old_nonboolean=len(self.words);row=super().step(check=check)
        # Every new Programme word is filled by the genuine hardwirer/wipe
        # in the old frozen rule. Full words can persist in derived Head
        # registers; they are never truncated there.
        self.words={};row['actual_old_nonboolean_Programme_sites']=old_nonboolean
        return row

    def snapshot(self):
        r=super().snapshot();r['actual_nonboolean_Programme']=[[x,[hex(v) for v in ws]] for x,ws in sorted(self.words.items())]
        return r

def run(recipe,limit=64):
    started=time.monotonic();s=Phase(recipe);rows=[];digest=hashlib.sha256();closure=None
    for t in range(limit):
        if t and t<recipe['rows']:s.fault(t)
        row=s.step(check=t<16 or t in (31,63) or (t+1)%512==0);rows.append(row)
        digest.update(json.dumps([row,s.snapshot()],separators=(',',':')).encode()+b'\n')
        if t+1>=recipe['rows'] and s.quiet_coherent(row):closure=s.snapshot();break
    classification=base.gray_errors.classify(s.support,s.support,Q=k.Q,U=k.U,sep=104,exact_limit=1)
    assert classification['points']==256 and classification['extent']==(16,16)
    assert classification['level1'] and not classification['level0']
    r=dict(recipe=recipe,Q=k.Q,U=k.U,error_lambda=24,error_separation=104,actual_chronological_fault_clock=T,
        original_c104_classification=classification,complete_chronological_error_payload=s.payload,
        actual_same_intact_H=True,actual_rows=rows,actual_prefix_trace_sha256=digest.hexdigest(),
        actual_quiet_coherent_closure=closure,new_CA_or_chosen_future_controller=False,
        operational_or_Gray_or_iid_conclusion=False,elapsed_seconds=time.monotonic()-started)
    return r,s

def main():
    D.mkdir(parents=True,exist_ok=True)
    for recipe in recipes():
        r,s=run(recipe);(D/(recipe['tag']+'_discovery.json')).write_text(json.dumps(r,indent=2)+'\n')
        print(json.dumps(dict(tag=recipe['tag'],rows=len(r['actual_rows']),last=r['actual_rows'][-1],
            closure=r['actual_quiet_coherent_closure'] is not None,seconds=r['elapsed_seconds'])),flush=True)

if __name__=='__main__':main()
