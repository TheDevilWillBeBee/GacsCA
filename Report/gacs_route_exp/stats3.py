import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import numpy as np
from gacsca import rule_g, netlist, rule
z = np.load(os.path.join(HERE, 'cand_c3_q448_s5.npz'), allow_pickle=False)
params = json.loads(str(z['params']))
for key in ('skew', 'gathers_q'): params[key] = tuple(params[key])
p = rule_g.ParamsG(**params).check()
stats = {'maj_calls': 0, 'maj_gates': 0}
orig = rule_g.maj5
def m5(n, bits):
    a = len(n.kind); v = orig(n, bits); stats['maj_calls'] += 1; stats['maj_gates'] += len(n.kind) - a; return v
rule_g.maj5 = m5
net = rule_g.build(p); comp = netlist.Compiled(net)
print('schema', rule_g.schema(p), 'width', rule_g.width(p))
print('gates', len(comp.gates), stats)
print({k: params[k] for k in ('q','k','m','nb','NPe','MP','NP','margin','L','S','fronts','delta','E0q','skew')})
print('U', p.U, 'PL', p.PL, 'E0b', p.E0b, 'E0', p.E0, 'T_sig', p.T_sig, 'IW', p.IW, 'NPT', p.NPT, 'rom bits', p.Q*p.NPT*p.IW, 'nonzero', int((z['rom']!=0).sum()))
rom = z['rom']
cols = np.nonzero(rom.any(axis=0))[0] & ((1 << p.logNP) - 1)
print('last page used', cols.max())
