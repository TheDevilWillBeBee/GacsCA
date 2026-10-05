"""Build one sized variant (recipe V_<tag> from figs/sweep/<tag>.json) in the private copy:
compile its ROM with the job scheduler and compile its C kernel (about 10 minutes of gcc).
The physical check of the result is closure, done by burst_cpu.py and run_g_period.py. Run from errlevels/repo with GACS_BURST=0 PYTHONPATH=."""
import json
import sys
import time
from gacsca import candidates

name = sys.argv[1]
t = time.time()
cand = candidates.load(name, check_manifest=False)
p = cand.p
print(json.dumps(dict(name=name, Q=p.Q, U=p.U, margin=p.margin, lo=p.lo, hi=p.hi, PL=p.PL, nb=p.nb, E0=p.E0, T_sig=p.T_sig,
                      NPe=p.NPe, MP=p.MP, NP=p.NP, gathers_q=p.gathers_q, width=cand.W, gates=len(cand.comp.gates),
                      exposure=2 * p.margin - 2 * p.H - 3, digest=cand.digest()[:16], seconds=round(time.time() - t))), flush=True)
t = time.time()
C = cand.c_backend()
print(json.dumps(dict(name=name, kernel=C.so_path.split('/')[-1], seconds=round(time.time() - t))), flush=True)
