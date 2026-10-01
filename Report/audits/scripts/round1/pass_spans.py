"""Read actual per-phase comb spans from cached instruction columns."""
import numpy as np
from gacsca.fixed_rule.design_optimization import candidates

for name in ('G13', 'G14'):
    c = candidates.load(name)
    p = c.p
    for label, lo, hi in (('early', 0, p.NPe - 1), ('a', p.NPe, p.MP),
                          ('final', p.MP + 1, p.NP)):
        pages = set()
        for j in range(p.fronts):
            base = j << p.logNP
            nz = np.nonzero(c.rom[:, base + lo:base + hi].any(axis=0))[0]
            pages.update((lo + nz).tolist())
        print(name, label, 'first', min(pages), 'last', max(pages),
              'span', max(pages) - lo + 1, 'used_pages', len(pages))
