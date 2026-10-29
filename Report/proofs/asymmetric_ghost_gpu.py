"""Explicit asymmetric driven boundary; the interior SP4 rule is unchanged.

Rings0/1 evolve periodically. Rings>=2 use ring1 for inputs crossing the
left edge and ring0 for the right edge, at the same tick. Cooperative
grid mode is required. Driven rings are not periodic CA trajectories.
"""
from contextlib import contextmanager
import re
from gacsca import gpu


def source(candidate, order='dfs'):
    text = gpu._source(candidate, order)
    signature = 'const uint32_t* __restrict__ rom) {'
    assert text.count(signature) == 1
    text = text.replace(signature, 'const uint32_t* __restrict__ rom, const wd* R, const wd* L, bool driven) {')
    call = 'word_step(X, Y, NW, w, rom);'
    assert text.count(call) == 1
    text = text.replace(call, 'word_step(X, Y, NW, w, rom, X - (size_t)ring * W * NW, '
                             'X - (size_t)ring * W * NW + (size_t)W * NW, ring >= 2);')
    right = re.compile(r'X\[(\d+) \* NW \+ wr\]')
    left = re.compile(r'X\[(\d+) \* NW \+ wl\]')
    text, nr = right.subn(lambda m: '(driven && w + 1 == NW ? R['+m[1]+' * NW] : '+m[0]+')', text)
    text, nl = left.subn(lambda m: '(driven && w == 0 ? L['+m[1]+' * NW + NW - 1] : '+m[0]+')', text)
    assert nr and nl and 'grid.sync();' in text
    return text


@contextmanager
def loader():
    original = gpu._source
    def driven(candidate, order='dfs'):
        gpu._source = original
        try:
            return source(candidate, order)
        finally:
            gpu._source = driven
    gpu._source = driven
    try:
        yield
    finally:
        gpu._source = original


def sim(candidate, nrings, colonies):
    assert nrings >= 3
    with loader():
        return gpu.GpuSim(candidate, nrings, colonies, mode='grid')
