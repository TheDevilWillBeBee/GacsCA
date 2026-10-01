"""Rebuild late comb candidates without changing their caches."""
import hashlib
import time
import numpy as np
from gacsca.fixed_rule.design_optimization import candidates

for name in ('G13', 'G14'):
    t = time.monotonic()
    cached = candidates.load(name)
    p, layout, prog = candidates.build(name)
    print(name, 'same_params', p == cached.p,
          'same_layout', bool(np.array_equal(layout, cached.layout)),
          'same_rom', bool(np.array_equal(prog.rom, cached.rom)),
          'fresh_rom_sha256', hashlib.sha256(prog.rom.tobytes()).hexdigest(),
          'cached_rom_sha256', hashlib.sha256(cached.rom.tobytes()).hexdigest(),
          'elapsed_s', round(time.monotonic() - t, 2), flush=True)
