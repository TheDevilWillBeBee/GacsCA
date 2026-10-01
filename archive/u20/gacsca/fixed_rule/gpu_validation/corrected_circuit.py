"""Build the corrected own-rule circuit using the established placement code.

The shared circuit builder has no program argument. This process-local context
supplies the corrected same-F WordCode only while initial data are built,
then clears and restores its caches. It never participates in physical ticks.
"""
from contextlib import contextmanager

from experiments.fixed_rule import build_compact8_circuit as circuit
from experiments.fixed_rule import compact8_address_rom as address_rom
from experiments.fixed_rule import measure_stream28_spatial_capacity as capacity
from experiments.fixed_rule import place_stream28_compact_gates as placement
from experiments.fixed_rule import stream28_compact_routes as routes
from . import description


@contextmanager
def corrected_initial_data():
    prior_capacity = capacity.dual_optimized20
    prior_placement = placement.dual_optimized20
    try:
        capacity.dual_optimized20 = description
        placement.dual_optimized20 = description
        routes.build.cache_clear()
        circuit.static_plan.cache_clear()
        address_rom.template.cache_clear()
        plan = circuit.static_plan(True,True)
        if plan['routes'].program.digest() != description.build().digest():
            raise AssertionError('corrected own-rule circuit not selected')
        yield plan
    finally:
        capacity.dual_optimized20 = prior_capacity
        placement.dual_optimized20 = prior_placement
        routes.build.cache_clear()
        circuit.static_plan.cache_clear()
        address_rom.template.cache_clear()
