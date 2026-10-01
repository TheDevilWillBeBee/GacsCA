"""GacsCA: a fixed-rule, self-simulating cellular automaton in the style of Gács and Gray.

Every physical rule here is defined once as a Boolean netlist (`rule.py` for the R
family, `rule_g.py` for the G family up to the current candidate G15). The same
netlist is executed by the physical ring simulators (NumPy, C, CUDA) and compiled
into the program that each colony runs to simulate one cell of the level above.
Nothing in this package takes a hierarchy depth argument.
"""
