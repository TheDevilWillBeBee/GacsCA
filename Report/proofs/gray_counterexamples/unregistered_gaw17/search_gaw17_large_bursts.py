"""Actual chronological original-c104 large bursts in frozen GAW2R.

Only a diagnostic support/operand generalization; no CA equation is edited.
Discovery receipts classify the executed history, not an unexecuted suffix.
"""
from pathlib import Path
from dataclasses import replace
import hashlib,json,sys,time
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw17'
sys.path.insert(0,str(S.parent/'unregistered_gaw16'))
import search_gaw16_word_bursts as inherited
previous=inherited.previous;k=inherited.k;own=inherited.own;base=inherited.base;prior=inherited.prior
P=inherited.P;T=inherited.T;STORE_PC=inherited.STORE_PC;MASK1700=inherited.MASK1700

def recipes():
    return [
      dict(tag='native_program104',start=P-2,width=104,rows=104,sparse_ends=False,
          profile='canonical',clocks='actual',flags='zero',heads='programme-read',banks='retained',Out=0,Info=None,Programme=k.MASK),
      dict(tag='cycle_control104',start=P-52,width=104,rows=104,sparse_ends=False,
          profile='alternating',clocks='cycle',flags='checker',heads='fork-eval',banks='SF-independent',Out=k.MASK,Info=k.MASK,Programme=(1<<99)|1),
      dict(tag='source_flags104',start=k.Q-52,width=104,rows=104,sparse_ends=False,
          profile='boundary-fork',clocks='source',flags='all',heads='fork-eval',banks='full-independent',Out=k.MASK,Info=k.MASK,Programme=k.MASK),
      dict(tag='interacting104',start=k.Q-52,width=104,rows=104,sparse_ends=False,
          profile='wide-fork',clocks='active-fork',flags='zero',heads='fork-eval',banks='full-independent',Out=1,Info=None,Programme=(1<<99)|0x15555),
      dict(tag='sparse_span150',start=k.Q-52,width=104,rows=104,sparse_ends=True,
          profile='wide-fork',clocks='source-active',flags='zero',heads='fork-eval',banks='full-independent',Out=k.MASK,Info=k.MASK,Programme=k.MASK)]

def sites(recipe,t):
    xs=list(range(recipe['start'],recipe['start']+recipe['width']))
    if recipe['sparse_ends'] and t==0:xs=[recipe['start']-23,*xs,recipe['start']+recipe['width']+22]
    return xs

def shift(recipe,x,t):
    side=x<recipe['start']+recipe['width']//2;p=recipe['profile']
    if p=='canonical':return 0
    if p=='alternating':return 1 if (x+t)%2==0 else -1
    if p=='boundary-fork':return 1 if side else -1
    if p=='wide-fork':return 1 if side else k.Q//2-1
    raise AssertionError(p)

def age(recipe,x,t):
    p=recipe['clocks'];side=x<recipe['start']+recipe['width']//2
    if p=='actual':return T+t
    if p=='cycle':return (k.U-1,72*k.Q+1,72*k.Q+2,102*k.Q+1)[t%4]
    if p=='source':return 96*k.Q+t
    if p=='active-fork':return T+t+(4*k.Q if not side else 0)
    if p=='source-active':return 96*k.Q+t if side else 102*k.Q+t+1
    raise AssertionError(p)

def replacement(recipe,x,t,old):
    heads=[]
    for h,slot in enumerate(k.SLOTS):
        y=x+slot;regs=[0]*16
        if recipe['heads']=='programme-read':
            regs[11]=(y%k.Q-P)%k.FRAME_WORDS
            head=k.Packet(p=1,mode=k.SEEK,pc=STORE_PC,target=y%k.Q,
                args=k.descriptor(0,dst=0,source=3),regs=tuple(regs))
        else:
            regs[0]=1
            head=k.Packet(p=1,mode=k.RUN,pc=0 if y%2==0 else own.ROM.early_pc,
                move=1 if y<k.Q else 2,regs=tuple(regs))
        heads.append(k.pack(head))
    flags=0 if recipe['flags']=='zero' else 15 if recipe['flags']=='all' else (x+t)&15
    data=dict(addr=(x+shift(recipe,x,t))%k.Q,age=age(recipe,x,t),
        f1=flags&1,f2=(flags>>1)&1,wf1=(flags>>2)&1,wf2=(flags>>3)&1,
        heads=tuple(heads),out=(recipe['Out'],)*5,scratch=(k.MASK,)*5,program=(recipe['Programme'],)*5)
    if recipe['Info'] is not None:data['info']=(recipe['Info'],)*5
    if recipe['banks']!='retained':
        banks={n:[] for n in ('mem','history1','history2','history3')}
        alternating=sum(((k.MASK//3) if j%2 else (2*k.MASK//3))<<(100*j) for j in range(17))
        for h,slot in enumerate(k.SLOTS):
            y=x+slot;native=P<=y%k.Q<P+6
            for name,value in zip(banks,(alternating,MASK1700,0,alternating)):
                banks[name].append(getattr(old,name)[h] if recipe['banks']=='SF-independent' and native else value)
        data.update({n:tuple(v) for n,v in banks.items()})
    return replace(old,**data)

class Phase(inherited.Phase):
    def __init__(self,recipe):
        self.words={};self.support=set();self.burst_recipe=recipe
        bootstrap=dict(tag=recipe['tag'],start=recipe['start'],width=recipe['width'],rows=1,
            gf_shift=0,age=T,flags=0,packet_kind='stationary-store',Out=1,Scratch=k.MASK)
        previous.Phase.__init__(self,bootstrap)
        originals={v['x']:k.cell_from_words([int(q,16) for q in v['old_complete_words']]) for v in self.payload}
        for x in sites(recipe,0):
            if x not in originals:originals[x]=self.raw(x)
        self.recipe=recipe;self.payload=[];self.fault(0,originals)

    def fault(self,t,originals=None):
        assert self.age==T+t
        for x in sites(self.recipe,t):
            old=originals[x] if originals is not None else self.raw(x)
            z=replacement(self.recipe,x,t,old);assert z!=old
            assert all(v in (0,1) for v in old.program) and all(v>1 for v in z.program)
            self.a[x-self.offset]=previous.Site(z.addr,z.age,z.f1,z.f2,z.wf1,z.wf2,0)
            self.words[x]=z.program
            self.pb[x-self.offset]=sum((v&1)<<h for h,v in enumerate(z.program))
            for h,slot in enumerate(k.SLOTS):
                y=x+slot;row=self.diff.setdefault(y,{})
                for name in previous.FIELDS:
                    values=list(row.get(name,(self.clean(name,y),)*5));values[h]=getattr(z,name)[h];row[name]=tuple(values)
            self.payload.append(dict(x=x,t=T+t,old_complete_words=[hex(v) for v in k.cell_words(old)],
                replacement_complete_words=[hex(v) for v in k.cell_words(z)]));self.support.add((x,T+t))
        self.normalize()

def classify(support):
    raw=base.gray_errors.classify(support,support,Q=k.Q,U=k.U,sep=104,exact_limit=1)
    # The original module can return NumPy integers in a rejection witness.
    # Serialize their exact integer values, without changing classification.
    return json.loads(json.dumps(raw,default=lambda v:v.item()))

def support_audit():
    result=[]
    for recipe in recipes():
        support={(x,T+t) for t in range(recipe['rows']) for x in sites(recipe,t)}
        c=classify(support)
        assert c['level1'] and not c['level0'] and c['points']==104*104+(2 if recipe['sparse_ends'] else 0)
        assert tuple(c['extent'])==((150,104) if recipe['sparse_ends'] else (104,104))
        result.append(dict(recipe=recipe,planned_complete_support_classification=c))
    dense150={(x,T+t) for t in range(104) for x in range(150)}
    rejected=classify(dense150);assert not rejected['level1'] and rejected['candidate_level1']
    return dict(Q=k.Q,U=k.U,error_lambda=24,error_separation=104,plans=result,
        dense150_by104_not_one_original_real1=rejected,actual_plans_not_yet_executed=True)

def run(recipe,limit=32):
    started=time.monotonic();state=Phase(recipe);rows=[];digest=hashlib.sha256();closure=None
    for t in range(limit):
        if t and t<recipe['rows']:state.fault(t)
        row=state.step(check=t in (0,1,3,7,15,31,63,103) or (t+1)%512==0);rows.append(row)
        digest.update(json.dumps([row,state.snapshot()],separators=(',',':')).encode()+b'\n')
        if t+1>=recipe['rows'] and state.quiet_coherent(row):closure=state.snapshot();break
    c=classify(state.support);assert c['level1'] and not c['level0']
    return dict(recipe=recipe,Q=k.Q,U=k.U,error_lambda=24,error_separation=104,
        actual_chronological_fault_clock=T,original_c104_classification=c,
        complete_chronological_error_payload=state.payload,actual_same_intact_H=True,
        actual_rows=rows,actual_prefix_trace_sha256=digest.hexdigest(),actual_quiet_coherent_closure=closure,
        full_planned_error_burst_executed=len(rows)>=recipe['rows'],
        new_CA_or_chosen_future_controller=False,operational_or_Gray_or_iid_conclusion=False,
        elapsed_seconds=time.monotonic()-started),state

def main():
    D.mkdir(parents=True,exist_ok=True)
    audit=support_audit();(D/'GAW17_support_classification.json').write_text(json.dumps(audit,indent=2)+'\n')
    print(json.dumps(dict(stage='original_c104_planned_supports_verified',plans=len(audit['plans']))),flush=True)
    for recipe in recipes():
        r,_=run(recipe);(D/(recipe['tag']+'_discovery.json')).write_text(json.dumps(r,indent=2)+'\n')
        print(json.dumps(dict(tag=recipe['tag'],rows=len(r['actual_rows']),last=r['actual_rows'][-1],
            closure=r['actual_quiet_coherent_closure'] is not None,seconds=r['elapsed_seconds'])),flush=True)

if __name__=='__main__':main()
