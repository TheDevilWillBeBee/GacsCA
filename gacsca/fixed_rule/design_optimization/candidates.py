"""Named fixed candidates: parameters, compile settings and saved artifacts.

A candidate is fully determined by (Params, layout, ROM). The ROM is the
compiled program for the rule's own netlist; it is regenerated
deterministically from the recipe below and cached under
figs/fixed_rule/design_optimization/candidates/. Loading checks that the
cached netlist digest, layout and ROM match the recipe.
"""
import hashlib
import json
import os
from dataclasses import asdict, replace
import numpy as np
from . import rule, rule_g, compiler, machine

FAMILIES = {'R': rule.Params, 'G': rule_g.ParamsG}

ROOT = machine.ROOT
CACHE = os.path.join(ROOT, 'figs', 'fixed_rule', 'design_optimization', 'candidates')

# Each recipe: rule parameters (without skew), layout choice, skew seed,
# compile settings. Different recipes are different fixed candidates.
RECIPES = {
    # Q=128, U=2^15: first closed candidate (reduced: no fivefold/3-gather).
    'R0': dict(params=dict(k=7, m=15, L=32, S=4, NP=240, MP=7), spread=False,
               skew_seed=0, compile=dict(lookahead=200, ooo=16)),
    # Q=128, U=2^14: same rule family with 64 registers.
    'R1': dict(params=dict(k=7, m=14, L=64, S=4, NP=121, MP=5), spread=False,
               skew_seed=1, compile=dict(lookahead=300, ooo=128)),
    # Q=256, U=2^16: Gray fivefold storage, three gathers with vote, early
    # Flag program, special SimBit procedure and Workspace-flag trickle-down.
    'G1': dict(family='G', params=dict(k=8, m=17, L=64, S=4, NP=300, NPe=56, MP=61),
               spread=False, skew_seed=0, compile=dict(lookahead=400, ooo=32)),
    # G1 plus gated pending writes (a spurious pend bit away from the front is ignored).
    'G2': dict(family='G', params=dict(k=8, m=17, L=64, S=4, NP=300, NPe=56, MP=61,
                                       gate_pend=True),
               spread=False, skew_seed=0, compile=dict(lookahead=400, ooo=32)),
    # G2 plus triple-modular evaluation: phase A, match pass and final program
    # run three times (identical ROM columns shifted by run_len) into Hold
    # copies A/B/C; the commit takes their majority.
    'G3': dict(family='G', params=dict(k=8, m=18, L=64, S=4, NP=980, NPe=70, MP=77,
                                       gate_pend=True, tmr=True, run_len=300),
               spread=False, skew_seed=0, compile=dict(lookahead=400, ooo=32)),
    # G3 with the front clock, the ROM lookup key and the match comparison taken
    # from the computed (majority-voted) Age/Address instead of stored fields.
    # (Its fetch key needs the upper maintenance before every match pass, so it
    # needs U=2^19.)
    'G4': dict(family='G', params=dict(k=8, m=19, L=64, S=4, NP=1270, NPe=70, MP=161,
                                       gate_pend=True, tmr=True, run_len=400,
                                       computed_front=True),
               spread=False, skew_seed=0, compile=dict(lookahead=400, ooo=32)),
    # Fivefold front: the register file and pending-write buffer are fivefold
    # like all other simulation structure, so every bit is majority-corrected
    # every tick. The five holders of the front's logical cell each do their
    # own lookup, keyed by holder-local computed geometry. No triple
    # evaluation is needed.
    'G5': dict(family='G', params=dict(k=9, m=19, L=32, S=4, NP=999, NPe=100, MP=321,
                                       computed_front=True, five_front=True),
               spread=False, skew_seed=0, compile=dict(lookahead=400, ooo=32)),
    # G5 with the three gathers 12Q apart (Ages 0, 12Q, 24Q; evaluation from
    # 32Q). Each gather is active for about 6Q ticks, so the rest between
    # gathers (about 6Q) exceeds Gray's level-1 recovery time 2Q + 900 (about
    # 3.8Q at Q=512): one level-1 error can then disturb at most one gather.
    # In G5 the rest was about 2Q. (The G5 compile settings leave 1,708
    # gates unscheduled on this netlist; lookahead 300 fits in 955 passes.)
    'G6': dict(family='G', params=dict(k=9, m=19, L=32, S=4, NP=991, NPe=100, MP=321,
                                       E0q=32, gathers_q=(0, 12, 24),
                                       computed_front=True, five_front=True),
               spread=False, skew_seed=0, compile=dict(lookahead=300, ooo=32)),
    # G6 at Q=1024, U=2^20 with Gray's colony margin (p. 33, Q >= 2K): the
    # represented SimBits and every instruction slot (hence all workspace:
    # Hold and scratch) lie in cells [128, 896). A burst up to 256 cells wide
    # at a colony boundary then reaches the live simulation data of at most
    # one colony (the one whose front it may hit). Only the special-procedure
    # cells 3 and Q-3 in the margins are written, by the early Flag program.
    'G7': dict(family='G', params=dict(k=10, m=20, L=32, S=4, NP=991, NPe=100, MP=321,
                                       E0q=32, gathers_q=(0, 12, 24), margin=128,
                                       computed_front=True, five_front=True),
               spread=False, skew_seed=0, compile=dict(lookahead=300, ooo=32)),
    # G7 + Gray's Workspace clearing (p. 34): scratch is set to 0 at the period
    # boundary. Without it, scratch slots that the program never writes keep
    # whatever a burst left there (dead but persistent differences).
    'G8': dict(family='G', params=dict(k=10, m=20, L=32, S=4, NP=991, NPe=100, MP=321,
                                       E0q=32, gathers_q=(0, 12, 24), margin=128, clear_ws=True,
                                       computed_front=True, five_front=True),
               spread=False, skew_seed=0, compile=dict(lookahead=300, ooo=32)),
    # G8's mechanisms with an exact (non-power-of-two) colony size: Q = 576 =
    # K + two margins of >= 100 cells, Addresses mod Q, Age packed as (tick mod
    # Q, tick // Q), U = nb * Q = 1236 * 576 = 711,936. NPe/MP/NP are the
    # tightest fit found by sweep_front.py (r3_q576_ooo16). QU = 2^28.6
    # versus G8's 2^30.
    'G9': dict(family='G', params=dict(k=10, m=21, L=32, S=4, NP=1203, NPe=134, MP=453,
                                       E0q=32, gathers_q=(0, 12, 24), margin=100, clear_ws=True,
                                       q=576, nb=1236, computed_front=True, five_front=True),
               spread=False, skew_seed=0, compile=dict(lookahead=300, ooo=16)),
    # G9 with the front confined to the working cells [104, 472): a pass takes
    # W = 368 ticks instead of Q = 576, and Age is packed with radix W. The new
    # upper Flag1/Flag2 are stored at the working-area ends and carried by the
    # fivefold right/left mail tracks to Gray's cells Q-3 and 3, arriving at
    # T_sig (courier). U = nb * W = 1256 * 368 = 462,208; QU = 2^28.0.
    'G10': dict(family='G', params=dict(k=10, m=20, L=32, S=4, NP=1204, NPe=132, MP=421,
                                        E0q=32, gathers_q=(0, 12, 24), margin=104, clear_ws=True,
                                        q=576, nb=1256, confined=True,
                                        computed_front=True, five_front=True),
                spread=False, skew_seed=0, compile=dict(lookahead=300, ooo=32)),
    # G10 with a compact fivefold front: one L-bit register slot per cell (the
    # copy of the unique front within two cells; its value is the majority of
    # the five slots around the front) instead of 5*L bits. This frees 4L bits
    # per cell, spent on more registers (L = 64) and a smaller colony: Q = 512,
    # margins of 120, W = 272, U = 326,400; QU = 2^27.32.
    'G11': dict(family='G', params=dict(k=9, m=20, L=64, S=4, NP=1138, NPe=97, MP=315,
                                        E0q=32, gathers_q=(0, 12, 24), margin=120, clear_ws=True,
                                        q=512, nb=1200, confined=True, compact_front=True,
                                        computed_front=True, five_front=True),
                spread=False, skew_seed=0,
                compile=dict(lookahead=600, ooo=32, order_kind=('interleave', 4))),
    # G11 compiled with structure awareness. (1) The rule's compact front step
    # is evaluated once on the arriving slot's inputs (mux_front: the five
    # candidate slots have distinct Addresses, so at most one arrives; same
    # function, 16% fewer gates). (2) Every field is spread evenly over the
    # working cells (proportional layout), so the data a computation needs
    # is within reach throughout each pass instead of in one region.
    # U = 799 * 272 = 217,328; QU = 2^26.73.
    'G12': dict(family='G', params=dict(k=9, m=19, L=64, S=4, NP=737, NPe=47, MP=165,
                                        E0q=32, gathers_q=(0, 12, 24), margin=120, clear_ws=True,
                                        q=512, nb=799, confined=True, compact_front=True, mux_front=True,
                                        computed_front=True, five_front=True),
                spread=False, layout='proportional', skew_seed=0,
                compile=dict(lookahead=1500, ooo=32, order_kind=('interleave', 4))),
    # G12 with a comb of five fronts five cells apart (multifront.py): each
    # front runs its own share of the program with its own register file
    'G13': dict(family='G', params=dict(k=9, m=18, L=64, S=4, NP=379, NPe=33, MP=111,
                                        E0q=32, gathers_q=(0, 12, 24), margin=122, clear_ws=True,
                                        q=512, nb=437, confined=True, compact_front=True, mux_front=True,
                                        computed_front=True, five_front=True, fronts=5, delta=5),
                spread=False, layout='proportional', skew_seed=0,
                compile=dict(lookahead=300, ooo=32,
                             multifront=dict(reassoc=True, cut=False, combine='spread', ctrl_fields=[]))),
    # G13 re-sized by the seeded schedule search (search_comb.py, best of 12
    # seeds: seed 10); same rule mechanisms, shorter program
    'G14': dict(family='G', params=dict(k=9, m=18, L=64, S=4, NP=327, NPe=32, MP=99,
                                        E0q=32, gathers_q=(0, 12, 24), margin=122, clear_ws=True,
                                        q=512, nb=385, confined=True, compact_front=True, mux_front=True,
                                        computed_front=True, five_front=True, fronts=5, delta=5),
                spread=False, layout='proportional', skew_seed=0,
                compile=dict(lookahead=300, ooo=32,
                             multifront=dict(reassoc=True, cut=False, combine='spread', ctrl_fields=[],
                                             order_seed=10, owner_seed=10))),
}


def build(name):
    r = RECIPES[name]
    p = FAMILIES[r.get('family', 'R')](**r['params']).check()
    layout = compiler.default_layout(p, r['spread'])
    if r.get('layout') == 'proportional':
        layout = compiler.proportional_layout(p, layout)
    skew, _ = compiler.choose_skew(p, layout, seed=r['skew_seed'])
    p = replace(p, skew=skew).check()
    prog = compiler.compile_candidate(p, layout, **r['compile'])
    return p, layout, prog


def load(name, rebuild=False):
    os.makedirs(CACHE, exist_ok=True)
    path = os.path.join(CACHE, f'{name}.npz')
    r = RECIPES[name]
    if os.path.exists(path) and not rebuild:
        z = np.load(path, allow_pickle=False)
        params = json.loads(str(z['params']))
        for key in ('skew', 'gathers_q'):
            if key in params:
                params[key] = tuple(params[key])
        p = FAMILIES[r.get('family', 'R')](**params).check()
        cand = machine.Candidate(p, z['rom'], z['layout'])
        if str(z['netlist_sha256']) != cand.comp.digest:
            raise RuntimeError(f'{name}: cached ROM was compiled for a different netlist')
        return cand
    p, layout, prog = build(name)
    cand = machine.Candidate(p, prog.rom, layout)
    cols = [x[0] for x in prog.listing]
    if getattr(p, 'fronts', 1) > 1:
        cols = [c & ((1 << p.logNP) - 1) for c in cols]     # psel = page + (front << logNP)
    passes = int(max(cols)) + 1
    np.savez(path, rom=prog.rom, layout=np.asarray(layout),
             params=json.dumps(asdict(p)), netlist_sha256=cand.comp.digest,
             passes=passes, instructions=len(prog.listing))
    return cand


def summary(cand):
    p = cand.p
    d = cand.identity()
    d.update(recipe_passes_used=int(np.max(np.nonzero(cand.rom.any(axis=0))[0]) + 1)
             if cand.rom.any() else 0,
             rom_bits=int(p.Q * p.NPT * p.IW),
             instruction_bits=p.IW)
    return d
