"""Bit-level fixed-rule successor candidates (design-optimization agent).

Every physical rule in this package is defined once as a Boolean netlist.
The same netlist is executed by the physical ring simulator and compiled
into the program that colonies use to simulate the upper cell. Nothing in
this package takes a hierarchy depth argument.
"""
