"""Reproducible independent Poisson noise on a discrete physical space-time box.

External fault generation only. No transition, filtering, recovery or resampling
is performed. Multiple marks at one site-time are retained in draw order.
"""
import math,random
import numpy as np
from . import retimed_holder_projected as r


def sample(*,sites,ticks,expected_marks,seed,max_marks=100000):
    if type(sites) is not int or not 1<=sites<1<<63 or type(ticks) is not int or not 1<=ticks<(1<<63)-1:raise ValueError('bounded positive space-time box required')
    if not isinstance(expected_marks,(int,float)) or not math.isfinite(expected_marks) or not 0<=expected_marks<=10000 or type(seed) is not int or seed<0:raise ValueError('bounded finite noise intensity and seed required')
    if type(max_marks) is not int or not 1<=max_marks<=100000:raise ValueError('bounded mark capacity required')
    rng=np.random.default_rng(seed);count=int(rng.poisson(expected_marks))
    if count>max_marks:raise MemoryError('sample exceeds capacity; no replacement sample drawn')
    times=rng.integers(1,ticks+1,size=count,dtype=np.uint64);positions=rng.integers(0,sites,size=count,dtype=np.uint64)
    values_rng=random.Random(seed^0x47414353504F4953)
    values=np.array([[values_rng.getrandbits(width) for _,width in r.SCHEMA] for _ in range(count)],dtype=np.uint64).reshape(count,len(r.SCHEMA))
    order=np.argsort(times,kind='stable');schedule=np.column_stack((times[order],positions[order],order.astype(np.uint64)))
    rate=float(expected_marks)/(sites*ticks)
    return dict(schedule=schedule,replacements=values[order],expected_marks=float(expected_marks),realized_marks=count,poisson_rate_per_site_time=rate,nonempty_probability_per_site_time=-math.expm1(-rate),space_time_volume=sites*ticks,seed=seed,noise_timing='after the physical transition into each integer time t in [1,H]',noise_model='Independent Poisson marks at each discrete physical site-time; any occupied coordinate receives a uniformly sampled complete projected G state. Repeated coordinates retain draw order, last replacement wins. No pattern rejection or conditioning.')
