#   Copyright 2019 Joseph T. Iosue
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

"""``qubovert`` is a module for converting problems into QUBO/Ising form.

QUBO stands for Quadratic Unconstrained Binary Optimization. QUBO problems
have a one-to-one mapping to classical Ising problems, and most optimization
problems are formatted in QUBO form when the solver is a quantum computer.
See ``qubovert.__all__`` for useful functionality, ``qubovert.problems__all__``
for problems defined, and ``qubovert.utils.__all__`` for some utility
functions, and ``qubovert.sat.__all__`` for the satisfiability library. See
``qubovert.program`` for ``qubovert`` programming ability.

"""

from ._version import __version__

from . import utils

from ._qubo import *
from ._ising import *
from ._pubo import *
from ._hising import *
from ._hobo import *
from ._hoio import *

from ._qubo import __all__ as __all_qubo__
from ._ising import __all__ as __all_ising__
from ._pubo import __all__ as __all_pubo__
from ._hising import __all__ as __all_hising__
from ._hobo import __all__ as __all_hobo__
from ._hoio import __all__ as __all_hoio__

__all__ = (
    __all_qubo__ +
    __all_ising__ +
    __all_pubo__ +
    __all_hising__ +
    __all_hobo__ +
    __all_hoio__
)

from . import sat
from . import problems
from . import program

BINARY_MODELS = QUBO, PUBO, HOBO, utils.QUBOMatrix, utils.PUBOMatrix
SPIN_MODELS = Ising, HIsing, HOIO, utils.IsingMatrix, utils.HIsingMatrix

name = "qubovert"
