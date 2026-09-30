"""Closed lower ring with coherent fivefold data and projected own-rule ROM.

The short represented upper segment has a geometry seam at its periodic wrap.
Centers at least seven upper cells from that seam admit one clean local
macrostep; a center at least fourteen away admits two.
"""
from dataclasses import replace
import hashlib
import random

import numpy as np

from .. import spatial_codec8
from .. import stream28_compact_layout as layout_module
from .. import stream28_dual_holder_rom as rom
from .. import stream28_dual_holder_rule20 as holder
from .. import stream28_dual_pass20 as physical
from .. import stream28_dual_projected20 as projected
from experiments.fixed_rule.build_compact8_circuit import static_plan
from experiments.fixed_rule.compact8_address_rom import project_all_dual_static, template


def upper_segment(colonies=31, seed=20260929, age=0):
    """Valid typed, locally coherent upper cells with varied Data and ROM."""
    if not 15 <= colonies <= 63 or not 0 <= age < physical.U:
        raise ValueError('bounded upper segment and valid Age required')
    rng = random.Random(seed)
    data = [rng.getrandbits(64) for _ in range(colonies)]
    spatial = template(True, True)
    cells = []
    for col in range(colonies):
        copies = {f's{offset+2}_data': data[(col+offset)%colonies]
                  for offset in holder.OFFSETS}
        raw = holder.Cell(address=col, age=age,
                          **rom.holder_static_fields(col), **copies)
        # The spatial ROM itself is static. Dynamic workspace starts idle.
        cells.append(physical.Cell(raw, spatial[col]))
    return tuple(cells)


def initialize(colonies=31, seed=20260929, upper_age=0):
    """Return (raw lower ring, represented upper cells), with no transition.

    The lower ring has exactly colonies*Q sites. Every physical Address and
    static ROM word is canonical; all five procedure Data copies refer to the
    corresponding neighboring physical site, including the periodic wrap.
    Info and Hold initially contain the same 119-word represented state.
    """
    upper = upper_segment(colonies, seed, upper_age)
    layout = layout_module.build()
    static = set(layout.static_inputs)
    sources = static_plan(True, True)['raw_sources']
    spatial = template(True, True)
    q = physical.Q
    base = np.zeros((q, physical.FIELDS), dtype=np.uint64)
    for site in range(q):
        for name, value in rom.holder_static_fields(site).items():
            base[site, holder.COL[name]] = value
        base[site, holder.COL['address']] = site
        base[site, holder.FIELDS:] = spatial_codec8.encode_cell(spatial[site])
    raw = np.tile(base, (colonies, 1))
    data = np.zeros(colonies*q, dtype=np.uint64)
    for col, cell in enumerate(upper):
        encoded = projected.encode_cell(projected.project(cell))
        data[col*q+np.asarray(layout.info)] = encoded
        data[col*q+np.asarray(layout.hold)] = encoded
        neighborhood = tuple(upper[(col+offset)%colonies]
                             for offset in physical.NEIGHBORHOOD)
        words = tuple(word for neighbor in neighborhood
                      for word in physical.encode_cell(neighbor))
        addressed = project_all_dual_static(cell.holder.address, words, True)
        for site, wire in sources.items():
            if wire in static:
                data[col*q+site] = addressed[wire]
    for offset in holder.OFFSETS:
        raw[:, holder.COL[f's{offset+2}_data']] = np.roll(data, -offset)
    return raw, upper


def decode_info(raw):
    if raw.ndim != 2 or raw.shape[1] != physical.FIELDS or len(raw)%physical.Q:
        raise ValueError('complete raw lower ring required')
    sites = np.asarray(layout_module.build().info)
    return tuple(tuple(map(int, raw[col*physical.Q+sites,
                                    holder.COL['s2_data']]))
                 for col in range(len(raw)//physical.Q))


def expected_upper_step(upper):
    result = []
    for col in range(len(upper)):
        neighbors = tuple(upper[(col+offset)%len(upper)]
                          for offset in physical.NEIGHBORHOOD)
        result.append(physical.local_step(neighbors))
    return tuple(result)


def state_sha256(raw):
    return hashlib.sha256(memoryview(np.ascontiguousarray(raw))).hexdigest()
