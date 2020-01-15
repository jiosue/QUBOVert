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

"""_parse_main_helper.py.

Helpers for ``main`` compilation in the ``compile_program`` function.

"""

from numpy import inf
from ._parse_helper import next_block


__all__ = 'parse_main_code',


def parse_main_code(code, qubovert_vars):
    """parse_main_code.

    Parse the code from the ``main`` part of a ``qubovert`` code.

    Parameters
    ----------
    code : str.
        The ``main`` part of a ``qubovert`` code.
    qubovert_vars : dict.
        Dictionary mapping variable names to their HOBO representations.
        The variables are defined in the ``variables`` section of the
        ``qubovert`` program.

    Return
    ------
    res : str.
        The compiled code.

    """
    res = "# run main\n"
    for line in code.split(";"):
        res += _parse_main_line(line, qubovert_vars) + "\n"
    res += (
        "\nprint('='*30)"
        "\nprint('System exited with program value', "
        "qubovert.utils.pubo_value(program, __solution__))"
        "\nprint('='*30)\n"
    )
    return res


def _parse_main_line(line, qubovert_vars):
    """_parse_main_line.

    Parse a line from the ``main`` part of a ``qubovert`` code.

    Parameters
    ----------
    line : str.
        A single line from the ``main`` part of a ``qubovert`` code.
    qubovert_vars : dict.
        Dictionary mapping variable names to their HOBO representations.
        The variables are defined in the ``variables`` section of the
        ``qubovert`` program.

    Return
    ------
    res : str.
        The compiled line.

    """
    line = line.strip()
    if "disp" in line:
        return _parse_disp(line, qubovert_vars)

    return ''


def _parse_disp(line, qubovert_vars):
    """_parse_disp.

    Parse a ``disp`` line from the ``main`` part of a ``qubovert`` code.

    Parameters
    ----------
    line : str.
        A single line from the ``main`` part of a ``qubovert`` code using
        the ``disp`` statement.
    qubovert_vars : dict.
        Dictionary mapping variable names to their HOBO representations.
        The variables are defined in the ``variables`` section of the
        ``qubovert`` program.

    Return
    ------
    res : str.
        The compiled line.

    Example
    -------
    >>> line = "disp('i: %g, x: %d, z: %w', i, x, z)"
    >>> _parse_disp(line, {'x', 'i'})
    "print(
        'i: %g, x: %d, z: %w' % (
            qubovert.utils.value(i, __solution__),
            qubovert.utils.value(x, __solution__),
            z
        )
    )"

    """
    res = 'print('
    line = next_block(line, '(', ')')[0]
    single = line.index("'") if "'" in line else inf
    double = line.index('"') if '"' in line else inf
    quote = "'" if single < double else '"'
    res += quote
    i = line.index(quote) + 1
    line = line[i:]
    i = line.index(quote) + 1
    res += line[:i] + ' % ('
    line = line[i:]
    for s in line.split(','):
        s = s.strip()
        if s in qubovert_vars:
            res += 'qubovert.utils.value(%s, __solution__), ' % s
        elif s:
            res += '%s, ' % s
    return res[:-2] + '))'
