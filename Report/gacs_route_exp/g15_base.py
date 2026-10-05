import sys, os, json, time
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from gacsca import candidates, machine
import numpy as np
t = time.time()
p, layout, prog = candidates.build('G15')
cand = machine.Candidate(p, prog.rom, layout)
print('built', round(time.time() - t), 's')
print('manifest ok:', candidates.verify('G15', cand))
st = prog.stats
print(json.dumps(dict(Q=p.Q, U=p.U, PL=p.PL, nb=p.nb, E0b=p.E0b, NPe=p.NPe, MP=p.MP, NP=p.NP,
      used={ph: st[ph]['passes'] for ph in ('early', 'a', 'final')},
      instr={ph: st[ph].get('instr') for ph in ('early', 'a', 'final')},
      instructions=len(prog.listing), rom_entries=int(p.Q * p.NPT), rom_bits=int(p.Q * p.NPT * p.IW),
      nonzero_rom=int((prog.rom != 0).sum()))))
# classify instructions by kind/source
from collections import Counter
from gacsca import rule
names = p.fam().source_names(p)
kinds = Counter(); loads = 0
for (page, cell, op, kind, a, b, d, note) in prog.listing:
    kinds[kind] += 1
print('dest kinds (REG,HOLD,SCR,NONE):', dict(kinds))
