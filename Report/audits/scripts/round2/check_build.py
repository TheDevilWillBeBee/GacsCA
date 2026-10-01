"""Fresh G15 build, manifest, geometry and cost check without touching caches."""
from gacsca.fixed_rule.design_optimization import candidates, machine

p, layout, prog = candidates.build('G15')
fresh = machine.Candidate(p, prog.rom, layout)
cached = candidates.load('G15')
print('fresh identity', {k:v for k,v in fresh.identity().items() if k not in ('schema','params')})
print('fresh summary', {k:v for k,v in candidates.summary(fresh).items() if k not in ('schema','params')})
print('fresh=cache digests', candidates.digests(fresh) == candidates.digests(cached))
print('fresh=manifest digests', candidates.digests(fresh) == candidates.manifest()['G15'])
print('Q,U,QU,width,gates,passes', p.Q,p.U,p.Q*p.U,fresh.W,len(fresh.comp.gates),candidates.passes_used(fresh))
print('radius', max(abs(i[1]) for i in fresh.comp.inputs if isinstance(i,tuple) and len(i)>1 and i[0]=='x'))
print('stage_wipe,sel_front',p.stage_wipe,p.sel_front)
