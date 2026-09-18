"""Depth-2 tower acid test on the GPU: level-0 colonies (Q0=256) simulate level-1 cells running the
full level-1 rule (tracks, mail, Tr_local for level-2, trickle, update; Q1=64, U1=4096).  The decoded
level-1 trajectory must equal the direct level-1 trajectory (NumPy engine of the level-1 system),
starting from level-1 ages just before each phase of the level-1 work period."""
import sys, time, numpy as np, torch
from gacsca.build import make_tower
from gacsca.hierarchy import encode_info
from gacsca.engine_np import repair, redistribute

ncol0 = 64
sys0, sys1 = make_tower(ncol0=ncol0)
p0, T, L0, sched0 = sys0.p, sys0.T, sys0.L, sys0.sched
p1, L1, sched1 = sys1.p, sys1.L, sys1.sched
U0, Q0, U1, Q1 = p0.U, p0.Q, p1.U, p1.Q
eng0 = sys0.np_engine(); g0 = sys0.gpu_engine()
eng1 = sys1.np_engine()


def level1_initial(rng, age1, ncell=ncol0):
    """level-1 ring: ground state of the level-1 local structure (addresses mod Q1), level-2 states
    encoded in the level-1 Info tracks (local-only level-2 cells, addresses mod Q2)."""
    level2 = [dict(addr=i % L1.Qs, age=0, f1=0, f2=0) for i in range(ncell // Q1 + 1)]
    S1 = eng1.initial(1)
    S1["age"][:] = age1
    info1 = np.zeros(ncell, np.uint8)
    for i in range(0, ncell, Q1):
        n = min(Q1, ncell - i)
        bits = L1.encode(level2[i // Q1]["addr"], 0, 0, 0, None)
        seg = np.zeros(Q1, np.uint8); seg[L1.b0:L1.b0 + L1.K] = bits
        info1[i:i + n] = seg[:n]
    S1["trk"] = redistribute(np.repeat(info1[None, :, None], T.NT, axis=2) * 0, T.R)
    prim = repair(S1["trk"]); prim[0, :, T["INFO"]] = info1
    S1["trk"] = redistribute(prim, T.R)
    return S1


def encode_level1_into_level0(S1):
    """level-1 state (NumPy engine state of sys1) -> level-0 Info bits of each colony."""
    prim = repair(S1["trk"])[0]
    cells = []
    for i in range(S1["addr"].shape[1]):
        cells.append(dict(addr=int(S1["addr"][0, i]), age=int(S1["age"][0, i]), f1=int(S1["f1"][0, i]), f2=int(S1["f2"][0, i]),
                          wf1=int(S1["wf1"][0, i]), wf2=int(S1["wf2"][0, i]), simage=int(S1["simage"][0, i]),
                          simaddr=int(S1["simaddr"][0, i]), tracks=S1["trk"][0, i]))
    return encode_info(cells, L0, Q0)


def decode_level0(st):
    info = g0.info_bits(st).cpu().numpy()[0]
    out = []
    for i in range(ncol0):
        out.append(L0.decode(info[i * Q0 + L0.b0:i * Q0 + L0.b0 + L0.K]))
    return out


def compare(dec, S1):
    prim = repair(S1["trk"])[0]
    bad = []
    for i, d in enumerate(dec):
        loc = (d["ADDR"], d["AGE"], d["F1"], d["F2"], d["WF1"], d["WF2"], d["SIMAGE"], d["SIMADDR"])
        ref = (int(S1["addr"][0, i]), int(S1["age"][0, i]), int(S1["f1"][0, i]), int(S1["f2"][0, i]), int(S1["wf1"][0, i]),
               int(S1["wf2"][0, i]), int(S1["simage"][0, i]), int(S1["simaddr"][0, i]))
        if loc != ref: bad.append((i, "local", loc, ref)); continue
        if not (d["tracks"] == S1["trk"][0, i]).all():
            tb = np.where((d["tracks"] != S1["trk"][0, i]).any(1))[0]
            bad.append((i, "tracks", [T.names[t] for t in tb[:6]]))
    return bad


def run(age1_start, nper, tag):
    rng = np.random.default_rng(0)
    S1 = level1_initial(rng, age1_start)
    S0 = eng0.initial(1, info_bits=encode_level1_into_level0(S1)[None, :])
    S0["simage"][:] = age1_start; S0["simaddr"][:] = (np.arange(p0.L) // Q0) % Q1
    st = g0.to_gpu(S0)
    t = 0; t0 = time.time()
    for per in range(1, nper + 1):
        st = g0.run(st, U0, 0.0, t0=t); t += U0
        S1 = eng1.step(S1)
        dec = decode_level0(st)
        bad = compare(dec, S1)
        N = g0.to_np(st)
        l0ok = (N["addr"][0] == np.arange(p0.L) % Q0).all() and (N["age"][0] == t % U0).all()
        print(f"{tag} age1={age1_start + per - 1}->{age1_start + per}: mismatching level-1 cells: {len(bad)} {bad[:3]}  level-0 ok={l0ok} ({time.time()-t0:.0f}s)", flush=True)
        if bad: return False
    return True


if __name__ == "__main__":
    ok = True
    s1 = sched1
    for age1, tag in [(0, "period-start"), (s1.gather_starts[1] - 2, "gather2"), (s1.compute_start - 2, "compute-start"),
                      (s1.compute_start + 400, "compute-mid"), (s1.compute_end - 60, "signalling"), (s1.trickle[0] - 2, "trickle"),
                      (s1.update_age - 2, "update")]:
        ok &= run(age1, 4, tag)
    print("ALL OK" if ok else "MISMATCH")
