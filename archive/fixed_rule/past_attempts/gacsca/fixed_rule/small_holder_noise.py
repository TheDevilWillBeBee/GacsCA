"""Bounded sparse realization of independent whole-cell replacement noise.

At each of sites*ticks cell updates, independently with probability 2**(-k),
replace the complete projected cell by a uniform 2704-bit state AFTER the local
transition. Sample the Binomial count, then a uniform subset using O(count)
Floyd sampling. A resource rejection is retained, never resampled. This module
constructs external noise only; it does not evolve simulated transitions.
"""
from dataclasses import dataclass
import random
import sys
import numpy as np
from . import small_holder_projected as r


class EventLimit(ValueError):
    def __init__(self,count,limit):
        self.count=count;self.limit=limit
        super().__init__(f'noise draw has {count} events, exceeds limit {limit}; do not resample')


def sample_indices(size,count,rng):
    if type(size) is not int or type(count) is not int or not 0<=count<=size:raise ValueError('valid finite subset size required')
    chosen=set()
    for j in range(size-count,size):
        value=rng.randrange(j+1)
        chosen.add(j if value in chosen else value)
    return tuple(sorted(chosen))


@dataclass(frozen=True)
class Schedule:
    sites:int
    ticks:int
    seed:int
    rate_exponent:int|None
    times:np.ndarray
    positions:np.ndarray
    replacements:np.ndarray
    def metadata(self):
        volume=self.sites*self.ticks;p=0. if self.rate_exponent is None else 2.**(-self.rate_exponent)
        return dict(sites=self.sites,ticks=self.ticks,space_time_volume=volume,seed=self.seed,rate_exponent=self.rate_exponent,cell_replacement_probability=p,expected_events=volume*p,realized_events=len(self.times),realized_rate=len(self.times)/volume,alphabet_bits=r.WIDTH,alphabet_words=len(r.SCHEMA),noise_order='local transition, then simultaneous whole-cell replacements, then observations',count_sampler='numpy.random.Generator(PCG64).binomial',subset_sampler='Floyd uniform subset without replacement; O(event count) storage',replacement_sampler='independent getrandbits(width) for every projected field',numpy_version=np.__version__,python_version=sys.version.split()[0])


def generate(sites,ticks,seed,rate_exponent=44,*,max_events=2048):
    if any(type(x) is not int for x in (sites,ticks,seed,max_events)) or sites<1 or ticks<1 or seed<0 or max_events<0 or sites*ticks>=1<<63:raise ValueError('bounded positive space-time volume and seed required')
    if rate_exponent is not None and (type(rate_exponent) is not int or not 0<=rate_exponent<=63):raise ValueError('dyadic exponent 0..63 or zero-noise None required')
    streams=np.random.SeedSequence(seed).spawn(3)
    rng=np.random.Generator(np.random.PCG64(streams[0]));p=0. if rate_exponent is None else 2.**(-rate_exponent)
    count=int(rng.binomial(sites*ticks,p))
    if count>max_events:raise EventLimit(count,max_events)
    position_rng=random.Random(streams[1].generate_state(4).tobytes())
    state_rng=random.Random(streams[2].generate_state(4).tobytes())
    indices=sample_indices(sites*ticks,count,position_rng)
    times=np.array([i//sites+1 for i in indices],dtype=np.uint64)
    positions=np.array([i%sites for i in indices],dtype=np.uint64)
    words=np.array([[state_rng.getrandbits(width) for _,width in r.SCHEMA] for _ in indices],dtype=np.uint64).reshape(count,len(r.SCHEMA))
    for array in (times,positions,words):array.flags.writeable=False
    return Schedule(sites,ticks,seed,rate_exponent,times,positions,words)
