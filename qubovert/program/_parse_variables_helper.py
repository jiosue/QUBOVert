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

"""_parse_variables_helper.py.

Helpers for ``variables`` compilation in the ``compile_program`` function.

"""

from qubovert import binary_var, integer_var
from ._parse_helper import next_block


__all__ = 'parse_variables_code',


def parse_variables_code(code):
    """parse_variables_code.

    Parse the code from the ``variables`` part of a ``qubovert`` code.

    Parameters
    ----------
    code : str.
        The ``variables`` part of a ``qubovert`` code.

    Return
    ------
    res : tuple (str, dict).
        The first element of the tuple is the compiled code. The second element
        is a dictionary mapping the variable names to their HOBO
        representations.

    """
    qubovert_vars = {}
    for line in code.split(';'):
        line = line.strip()
        # TODO: accept lists, ie binary[], integer(b)[]
        if 'binary' in line:
            line = line[6:].strip()
            for name in line.split(','):
                name = name.strip()
                qubovert_vars[name] = binary_var(name)
        elif 'integer' in line:
            # arguments for integer is either number of bits,
            # or number of bits and log_trick
            b, i = next_block(line, '(', ')')
            args = eval(b.replace('\n', ''))
            if not isinstance(args, tuple):
                args = args,
            line = line[i:].strip()
            for name in line.split(','):
                name = name.strip()
                qubovert_vars[name] = integer_var(name, *args)
        else:
            if line.strip():
                raise ValueError("Unknown variable type")

    res = "# create variables\n"
    for var, d in qubovert_vars.items():
        res += var + ' = ' + str(d) + '\n'
    return res, qubovert_vars
