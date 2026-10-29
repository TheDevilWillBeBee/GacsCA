"""Explicit driven-boundary execution variant, never an active rule change.

In grid mode, ring0 follows the ordinary periodic candidate. Other rings
read ring0 whenever an input coordinate crosses either finite-domain edge.
Their interior transition is unchanged. This is NOT periodic CA evolution
of those noisy rings and does not by itself simulate an infinite hierarchy.
"""
from contextlib import contextmanager
import re
from gacsca import gpu


def source(candidate, order='dfs'):
    text = gpu._source(candidate, order)
    signature = 'const uint32_t* __restrict__ rom) {'
    assert text.count(signature) == 1
    text = text.replace(signature, 'const uint32_t* __restrict__ rom, const wd* R) {')
    call = 'word_step(X, Y, NW, w, rom);'
    assert text.count(call) == 1
    text = text.replace(call, 'word_step(X, Y, NW, w, rom, X - (size_t)ring * W * NW);')
    right = re.compile(r'X\[(\d+) \* NW \+ wr\]')
    left = re.compile(r'X\[(\d+) \* NW \+ wl\]')
    text, nr = right.subn(lambda m: '(w + 1 == NW ? R['+m[1]+' * NW] : '+m[0]+')', text)
    text, nl = left.subn(lambda m: '(w == 0 ? R['+m[1]+' * NW + NW - 1] : '+m[0]+')', text)
    assert nr and nl
    # Cooperative grid synchronization gives all reads the same input time.
    assert 'grid.sync();' in text
    return text


@contextmanager
def loader():
    original = gpu._source
    # Capture the original separately: source() must not recurse through
    # this temporary process-local replacement.
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
    with loader():
        return gpu.GpuSim(candidate, nrings, colonies, mode='grid')
