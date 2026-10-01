"""Where the CUDA kernel's time goes (REPORT section 28).

Three measurements on a candidate's grid-mode kernel, all on one level-2 cell's worth of sites
(Q^2), for 1 ring and for 16 rings:
  bounds   the kernel compiled with different __launch_bounds__ (fewer registers per thread,
           more threads per SM) -- gpu.py hard-codes (256, 1), which also overrides
           -maxrregcount;
  idle     the netlist specialized to "no front arrives here": the five per-slot arrival signals
           (the leaves of the OR tree under the 'arrive' output) forced to 0 and the netlist
           re-simplified; the gates that remain, and the speed of a kernel built from them
           (a timing prototype of the fast path of a front-skipping kernel; it is not an exact
           simulator for words where a front does arrive);
  ptxas    registers and spills reported by ptxas for the kernel as generated.
The generated source is changed in memory only (gpu._source is wrapped); gpu.py is not edited.
Writes figs/gpu/<cand>_kernel_study.json.
Usage: gpu_kernel_study.py --candidate G15 [--parts bounds,idle,ptxas]
"""
import argparse
import copy
import json
import os
import re
import subprocess
import tempfile
import numpy as np
from gacsca import candidates, codec, gpu
from gacsca.netlist import Net, Compiled, OR

OUT = os.path.join(candidates.ROOT, 'figs', 'gpu')


def live(roots, gate_of):
    seen, stack = set(), list(roots)
    while stack:
        x = stack.pop()
        if x in seen or x < 2:
            continue
        seen.add(x)
        g = gate_of(x)
        if g is not None:
            stack += [g[1], g[2]]
    return {x for x in seen if gate_of(x) is not None}


def idle_netlist(cand):
    """The candidate's netlist with every per-slot arrival forced to 0, re-simplified."""
    comp = cand.comp
    n_in = 2 + len(comp.inputs)
    G = comp.gates
    gate_of = lambda x: G[x - n_in] if x >= n_in else None
    leaves, stack = [], [comp.outputs[('arrive', 0)]]
    while stack:
        x = stack.pop()
        g = gate_of(x)
        if g is not None and g[0] == OR:
            stack += [g[1], g[2]]
        else:
            leaves.append(x)
    net = Net()
    m = {0: 0, 1: 1}
    for i, name in enumerate(comp.inputs):
        m[2 + i] = net.input(name)
    forced = set(leaves)
    for g, (op, a, b) in enumerate(G):
        x = n_in + g
        m[x] = 0 if x in forced else net.op(op, m[a], m[b])
    for name, node in comp.outputs.items():
        net.set_output(name, m[node])
    out = Compiled(net)
    info = dict(gates=len(G), arrive_leaves=len(leaves), gates_deciding_arrival=len(live(leaves, gate_of)),
                gates_with_no_arrival=len(out.gates))
    return out, info


def timed(cand, patch, rings, threads, P):
    orig = gpu._source
    gpu._source = lambda c, order='dfs': patch(orig(c, order))
    try:
        sim = gpu.GpuSim(cand, rings, cand.p.Q, threads=threads, mode='grid')
        sim.set_state(P)
        sim.run(50)
        ts = []
        for _ in range(3):
            sim.run(500)
            ts.append(sim.last_ms * 1000 / 500)
        del sim
    finally:
        gpu._source = orig
    return round(min(ts), 1)


def bounds(lb):
    return lambda src: src.replace('extern "C" __global__ void __launch_bounds__(256, 1) k_run_grid',
                                   f'extern "C" __global__ void __launch_bounds__({lb[0]}, {lb[1]}) k_run_grid')


def ptxas(cand, patch=lambda s: s):
    with tempfile.TemporaryDirectory() as tmp:
        cu = os.path.join(tmp, 'k.cu')
        open(cu, 'w').write(patch(gpu._source(cand)))
        r = subprocess.run([gpu.NVCC, '-O3', '-arch=sm_80', '-cubin', '-Xptxas', '-v', cu, '-o',
                            os.path.join(tmp, 'k.cubin')], capture_output=True, text=True)
    txt = r.stderr
    i = txt.find("'k_run_grid'")
    seg = txt[i:i + 600]
    get = lambda pat: int(re.search(pat, seg).group(1)) if re.search(pat, seg) else None
    return dict(registers=get(r'Used (\d+) registers'), spill_stores=get(r'(\d+) bytes spill stores'),
                spill_loads=get(r'(\d+) bytes spill loads'))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--candidate', default='G15')
    ap.add_argument('--parts', default='bounds,idle,ptxas')
    args = ap.parse_args()
    parts = args.parts.split(',')
    cand = candidates.load(args.candidate)
    C = cand.c_backend()
    P = C.pack(codec.encode(cand, codec.encode(cand, codec.random_upper(cand, 1, np.random.default_rng(5)))))
    rec = dict(candidate=args.candidate)
    same = lambda s: s
    if 'ptxas' in parts:
        rec['ptxas'] = {f'{a},{b}': ptxas(cand, bounds((a, b))) for a, b in ((256, 1), (128, 4), (128, 8))}
        print('ptxas', json.dumps(rec['ptxas']), flush=True)
    if 'bounds' in parts:
        rec['bounds'] = []
        for lb in ((256, 1), (128, 4), (256, 2), (128, 8), (64, 8)):
            for nr in (16, 1):
                row = dict(launch_bounds=lb, rings=nr, us_per_tick=timed(cand, bounds(lb), nr, lb[0], P))
                row['us_per_ring'] = round(row['us_per_tick'] / nr, 1)
                rec['bounds'].append(row)
                print(json.dumps(row), flush=True)
    if 'idle' in parts:
        idle = copy.copy(cand)
        idle.comp, rec['idle_netlist'] = idle_netlist(cand)
        print('idle netlist', json.dumps(rec['idle_netlist']), flush=True)
        rec['idle'] = []
        for label, c in (('full', cand), ('no front within reach', idle)):
            for nr in (16, 1):
                row = dict(kernel=label, rings=nr, us_per_tick=timed(c, same, nr, 256, P))
                row['us_per_ring'] = round(row['us_per_tick'] / nr, 1)
                rec['idle'].append(row)
                print(json.dumps(row), flush=True)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, f'{args.candidate}_kernel_study.json'), 'w') as fh:
        json.dump(rec, fh, indent=1)


if __name__ == '__main__':
    main()
