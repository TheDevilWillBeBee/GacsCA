"""Tables for ERROR_LEVELS.md from the sizing sweeps and the CPU experiments."""
import glob
import json
import math
import os
import statistics
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))


def sweeps():
    print('## sizing sweeps (errlevels/repo/figs/sweep/*.json)')
    print('| tag | Q | margin | gathers | blocks before E0 | settings fit | NP best / median / worst | U best | U median | U worst | QU best (log2) |')
    print('|---|---:|---:|---|---:|---:|---|---:|---:|---:|---:|')
    for f in sorted(glob.glob(os.path.join(HERE, 'repo', 'figs', 'sweep', '*.json'))):
        d = json.load(open(f))
        ok = [r for r in d['records'] if 'U' in r]
        if not ok:
            print('|', os.path.basename(f)[:-5], '| no fit |')
            continue
        us = sorted(r['U'] for r in ok)
        nps = sorted(r['params']['NP'] for r in ok)
        b = d['best']
        prm = b['params']
        e0b = prm['nb'] - prm['NP'] - 1
        print(f"| {os.path.basename(f)[:-5]} | {b['Q']} | {prm['margin']} | {tuple(prm['gathers_q'])} | {e0b} | "
              f"{len(ok)}/{len(d['records'])} | {nps[0]} / {statistics.median(nps):g} / {nps[-1]} | {us[0]:,} | "
              f"{int(statistics.median(us)):,} | {us[-1]:,} | {math.log2(b['Q'] * us[0]):.2f} |")


def bursts():
    for f in sorted(glob.glob(os.path.join(HERE, 'results', 'burst_*.json'))):
        d = json.load(open(f))
        n = d['colonies']
        jL, jR = n // 2 - 1, n // 2
        print(f"\n## {os.path.basename(f)}: Q {d['Q']}, U {d['U']}, margin {d['margin']}, gathers {d['gathers_q']}, "
              f"mode {d.get('mode')}, closure {d['closure']['period1']}/{d['closure']['period2']}, {d['seconds']} s")
        groups = defaultdict(list)
        for r in d['results']:
            groups[(r['w'], r['place'])].append(r)
        print('| width | place | runs | wrong upper cells at U: none / one / two adjacent / other | max recovery, Address/Age/flags (ticks) | '
              'max recovery, Address/Age only | max Address/Age island (sites) | Address/Age beyond box: left, right (sites) | wrong at 2U | identical at 2U |')
        print('|---:|---|---:|---|---:|---:|---:|---|---:|---:|')
        for (w, place), rs in sorted(groups.items()):
            kinds = [0, 0, 0, 0]
            for r in rs:
                wu = r['wrong_upper_U']
                if not wu:
                    kinds[0] += 1
                elif len(wu) == 1:
                    kinds[1] += 1
                elif len(wu) == 2 and wu[1] - wu[0] == 1:
                    kinds[2] += 1
                else:
                    kinds[3] += 1
            rec = max(r['structure_recovery_ticks'] for r in rs)
            exh = any(r['structure_window_exhausted'] for r in rs)
            isl = max(r['addr_age_island_max'] for r in rs)
            raa = max(r['addr_age_recovery_ticks'] for r in rs)
            sp = [r['addr_age_span_rel_box'] for r in rs if r['addr_age_span_rel_box']]
            left = min((s[0] for s in sp), default=0)
            right = max((s[1] for s in sp), default=0)
            w2 = sum(1 for r in rs if r['wrong_upper_2U'])
            ident = sum(1 for r in rs if r['identical_2U'])
            print(f"| {w} | {place} | {len(rs)} | {kinds[0]} / {kinds[1]} / {kinds[2]} / {kinds[3]} | {rec}{'+' if exh else ''} | {raa} | {isl} | "
                  f"{left}, {right} | {w2} | {ident} |")
        bad = [r for r in d['results'] if len(r['wrong_upper_U']) > 2 or
               (len(r['wrong_upper_U']) == 2 and r['wrong_upper_U'][1] - r['wrong_upper_U'][0] != 1) or r['wrong_upper_2U']]
        for r in bad:
            print('  note:', {k: r[k] for k in ('phase', 'place', 'w', 't', 'wrong_upper_U', 'wrong_upper_2U', 'colonies_work_info_U',
                                               'structure_recovery_ticks', 'sites_differ_2U')})
        by_phase = defaultdict(list)
        for r in d['results']:
            by_phase[r['phase']].append(r)
        print('  per phase: max structure recovery, runs with a wrong upper cell at U, at 2U')
        for ph, rs in by_phase.items():
            print(f"    {ph:14s} t={rs[0]['t']:6d}  rec {max(r['structure_recovery_ticks'] for r in rs):5d}  "
                  f"wrongU {sum(1 for r in rs if r['wrong_upper_U']):2d}/{len(rs)}  wrong2U {sum(1 for r in rs if r['wrong_upper_2U'])}  "
                  f"not identical at 2U {sum(1 for r in rs if not r['identical_2U'])}")


def pairs():
    for f in sorted(glob.glob(os.path.join(HERE, 'results', 'pair_*.json'))):
        d = json.load(open(f))
        print(f"\n## {os.path.basename(f)}: {d['candidate']}, sites per error {d['width'] or '1 or 2'}, K {d['K']}, {d['seconds']} s")
        res = d['results']
        gaps = sorted({int(k.split(',')[0]) for k in res})
        dts = sorted({int(k.split(',')[1]) for k in res})
        print('| clean sites between the two errors | ' + ' | '.join(f'dt = {dt}: identical after 1 / 2 / {d["K"]} ticks (of n)' for dt in dts) + ' |')
        print('|---:|' + '---|' * len(dts))
        for g in gaps:
            cells = []
            for dt in dts:
                r = res[f'{g},{dt}']
                cells.append(f"{r['clean'][0]} / {r['clean'][1]} / {r['clean'][-1]} ({r['trials']})")
            print(f'| {g} | ' + ' | '.join(cells) + ' |')


if __name__ == '__main__':
    what = sys.argv[1:] or ['sweeps', 'bursts', 'pairs']
    for w in what:
        globals()[w]()
