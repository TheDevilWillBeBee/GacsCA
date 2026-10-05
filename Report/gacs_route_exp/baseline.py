import sys, time, json
sys.path.insert(0, '/tmp/claude-1000/-home-ivrl-Ehsan-Projects-GacsCA/48f9b863-47d2-4e83-bc59-bd69b341430f/scratchpad/gacs_study/exp')
from dataclasses import replace
from gacsca import candidates, compiler, rule_g, netlist
r = candidates.RECIPES['G15']
p = rule_g.ParamsG(**r['params']).check()
layout = compiler.default_layout(p, r['spread'])
layout = compiler.proportional_layout(p, layout)
skew, _ = compiler.choose_skew(p, layout, seed=r['skew_seed'])
p = replace(p, skew=skew).check()
print('Q', p.Q, 'U', p.U, 'PL', p.PL, 'nb', p.nb, 'E0b', p.E0b, 'E0', p.E0, 'NP', p.NP, 'lo,hi', p.lo, p.hi, 'H', p.H)
print('schema', rule_g.schema(p), 'width', rule_g.width(p), 'IW', p.IW, 'SB', p.SB, 'DB', p.DB, 'PK', p.PK, 'NPT', p.NPT)
# instrument maj5
stats = {'maj5_calls': 0, 'maj5_gates': 0, 'maj3_calls': 0, 'maj3_gates': 0}
orig5, orig3 = rule_g.maj5, rule_g.maj3
def m5(n, bits):
    a = len(n.kind); v = orig5(n, bits); stats['maj5_calls'] += 1; stats['maj5_gates'] += len(n.kind) - a; return v
def m3(n, a_, b_, c_):
    a = len(n.kind); v = orig3(n, a_, b_, c_); stats['maj3_calls'] += 1; stats['maj3_gates'] += len(n.kind) - a; return v
rule_g.maj5, rule_g.maj3 = m5, m3
t = time.time()
net = rule_g.build(p)
comp = netlist.Compiled(net)
print('built in', time.time() - t, 's; raw gates', sum(1 for k in net.kind if k == 'G'), 'live gates', len(comp.gates))
print(stats)
print('digest', comp.digest)
