"""Reproducible small source/receipt probes cited by AUDIT2.md."""
from copy import deepcopy
from dataclasses import replace
import json
from pathlib import Path
import numpy as np

from gacsca.fixed_rule.design_optimization import candidates, codec
from experiments.fixed_rule.design_optimization.level1_campaign import prop4_check
from experiments.fixed_rule.design_optimization.three_level_g import wiped_level2_bits

ROOT = Path('figs/fixed_rule/design_optimization')
c = candidates.load('G15')
p = c.p

# Cache should not silently represent a modified recipe.
original = candidates.RECIPES['G15']
changed = deepcopy(original)
changed['params']['stage_wipe'] = False
try:
    candidates.RECIPES['G15'] = changed
    got = candidates.load('G15')
    print('recipe change accepted:', changed['params']['stage_wipe'], got.p.stage_wipe)
finally:
    candidates.RECIPES['G15'] = original

box = (32*p.Q+200,32*p.Q+299,1536,1635,p.Q,p.U,64)
print('Prop4 supplied bad event:', prop4_check([(1700,[40])],*box))
print('Prop4 same event omitted by sampling:', prop4_check([],*box))
d = json.loads((ROOT/'level1_campaign/G15_b91_full_wipe1.json').read_text())
print('b91 represented-vs-per-copy:',d['summary']['prop4_simbits'],d['summary']['prop4_info_slots'])

X = codec.encode(c, codec.random_upper(c,1,np.random.default_rng(3)))
for age in (p.E0-1,p.U-1):
    Y=X.copy();bits=p.age_code(age)
    for i in range(dict(c.schema)['age']):
        Y[c.row[('age',i)]]=bool((bits>>i)&1)
    for f in ('hold','h1','h2','mr','ml'):
        rows=[c.row[(f,i)] for i in range(dict(c.schema)[f])]
        Y[rows]=True
    Z=c.step_numpy(Y)
    print('wipe age',age,{f:int(Z[[c.row[(f,i)] for i in range(dict(c.schema)[f])]].sum())
                          for f in ('info','hold','h1','h2','mr','ml')})

offs=[off for _,off in p.fam().info_copies(p)]
L2=np.ones((c.W,1),dtype=bool)
enc=codec.encode(c,L2)
for k in (3,7,27,64,128):
    lo=p.Q//2-(k-1)//2
    cells=set(range(lo,lo+k))
    all5=sum(all((int(y)+off)%p.Q in cells for off in offs) for y in c.layout)
    A=enc.copy();A[:,list(cells)]=0
    flip=int((codec.decode(c,A)!=L2).sum())
    func=sum(map(len,wiped_level2_bits(c,L2,cells).values()))
    print('wiped bits',k,all5,func,'immediate majority flips',flip)

rng=np.random.default_rng(11)
full=codec.encode(c,codec.random_upper(c,1,rng))
idx=(np.arange(32)+p.Q//2-16)%p.Q
sl=full[:,idx].copy()
for k in range(1,7):
    full=c.step_numpy(full);sl=c.step_numpy(sl)
    diff=(sl!=full[:,idx]).any(axis=0)
    print('slice wrap step',k,'middle',bool(diff[16]),'diff cells',int(diff.sum()))

g14=candidates.load('G14')
print('sel_front gates',[(mode,len(replace(g14.p,sel_front=mode).check().fam().cached(
    replace(g14.p,sel_front=mode).check())[1].gates)) for mode in (0,1,2)])

bench=json.loads((ROOT/'gpu/G15_level2_bench.json').read_text())
print('U squared',p.U*p.U)
for row in bench['rows']:
    if row['threads']==256 and row['maxreg']==0 and row['rings']==1:
        print('GPU days',row['level2_cells_per_ring'],
              round(p.U*p.U*row['us_per_tick']*1e-6/86400,1))

for name in ('G15_b92_full_wipe2','G15_b93_full_wipe3'):
    d=json.loads((ROOT/f'level1_campaign/{name}.json').read_text())
    r=next(r for r in d['rings'] if r['kind']=='E1' and r['phase']=='gather1_mid'
           and r['place']==('left' if 'b92' in name else 'mid'))
    touched=list(range(r['extent']['x_lo']//p.Q,r['extent']['x_hi']//p.Q+1))
    print(name,'touched',touched,'wrong per step',
          [s['wrong_upper_cells'] for s in r['steps']])
