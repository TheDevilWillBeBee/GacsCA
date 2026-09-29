"""Canonical controller/Signal quotient with its four flag outputs suppressed.

This expression is unchanged from the prefix body. For post-capture use it
represents only the controller component. The actual flags must be supplied by
the coupled flag engine. Mail-free execution is guarded dynamically, making the
computed-Flag1 mail-clearing coupling vacuous rather than silently omitting it.
"""
from .holder_prefix_description import build
