"""
qubovert is a module for converting common problems into QUBO and Ising 
form, where QUBO stands for Quadratic Unconstrained Binary Optimization. QUBO 
problems have a one-to-one mapping to classical Ising problems, and most 
optimization problems are formatted in QUBO form when the solver is a quantum 
computer. See qubovert.__all__ for all the problems defined, and 
qubovert.utils.__all__ for some utilities used.
"""


name = __str__ = "qubovert"
from ._version import __version__
from . import utils
from .karp import *

from .karp import __all__ as __karp__

# if someone does `from qubovert import *`, import all of the problem, but
# not utils.
__all__ = __karp__