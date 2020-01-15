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

"""_parse_program_helper.py.

Helpers for ``program`` compilation in the ``compile_program`` function.

"""

from qubovert import HOBO
from ._parse_helper import next_block
import re


__all__ = 'parse_program_code',


def parse_program_code(code, qubovert_vars):
    """parse_program_code.

    Parse the code from the ``program`` part of a ``qubovert`` code.

    Parameters
    ----------
    code : str.
        The ``program`` part of a ``qubovert`` code.
    qubovert_vars : dict.
        Dictionary mapping variable names to their HOBO representations.
        The variables are defined in the ``variables`` section of the
        ``qubovert`` program.

    Return
    ------
    res : str
        The compiled code.

    """
    parser = _Parser(qubovert_vars)
    _parse_program_code(code, parser)
    return "# create program\nprogram = " + str(parser.program) + '\n'


def _parse_program_code(code, parser, conditions=()):
    """_parse_program_code.

    Parse the code from the ``program`` part of a ``qubovert`` code.

    Parameters
    ----------
    code : str.
        The ``program`` part of a ``qubovert`` code.
    parser : _Parser object.
        Parser that has all of the variables defined.
    condition: tuple (optional, defaults to ()).
        DO NOT supply this argument from externally! This is an internal
        argument.

    Return
    ------
    res : None.
        Updates the Parser in place.

    """
    while ';' in code:
        i = code.index(';')
        line = code[:i].strip()
        code = code[i+1:].strip()
        if 'if' in line:
            c, _ = next_block(line, '(', ')')
            c = parser.evaluate_condition(c),
            block, i = next_block(code)
            code = code[i:]
            parse_program_code(block, parser, conditions + c)
        else:
            parser.parse_line(line, conditions)


class _Parser:
    """_Parser.

    Internal class to parse a program.

    """

    def __init__(self, qubovert_vars):
        """__init__.

        Stuff.

        Parameters
        ----------
        qubovert_vars : dict.
            Dictionary that maps variable names (defined in the ``variables``
            section of the ``qubovert`` program) to their HOBO values.

        """
        self._variables = qubovert_vars.copy()
        self._program = HOBO()

    @property
    def program(self):
        """program.

        Property to return the program.

        Return
        ------
        program : dict.

        """
        return dict(self._program)

    def _evaluate_expression(self, expression):
        """_evaluate_expression.

        Evaluate an arbitrary expression.

        Parameters
        ----------
        expression : str.
            Code of the expression.

        Return
        ------
        res : HOBO.
            The evaluated expression.

        """
        pass

    def _enforce(self, expression, lam=1, log_trick=True, bounds=None):
        """_enforce.

        Enforce the contraint represented by the expression.

        Parameters
        ----------
        expression : str.
            The code representing the expression.
        lam : HOBO (optional, defaults to 1).
            The penalty to the constraint.
        log_trick : bool (optional, defaults to True).
            See the HOBO.add_constraint methods for a description of this
            argument.
        bounds : tuple (optional, default to None).
            See the HOBO.add_constraint methods for a description of this
            argument.

        Return
        ------
        res : None.
            Updates the program in place.

        """
        pass

    def evaluate_condition(self, condition):
        """evaluate_condition.

        Evaluate the conditional inside an 'if' statement. Ie
        if (condition); {do;}

        Parameters
        ----------
        condition : str.
            The code representing a condition.

        Return
        ------
        res : HOBO object.
            The HOBO condition such that a multiplication by ``res`` will
            represent applying the condition.

        """
        pass

    def parse_line(self, line, conditions=()):
        """parse_line.

        Stuff.

        Parameters
        ----------
        line : str.
            The line of code.
        conditions : tuple of HOBOs.
            Evaluate the line of code subject to the conditions.

        Return
        ------
        None.

        """
        condition = 1
        for c in conditions:
            condition *= c

        if "minimize" in line:
            b, _ = next_block(line, '(', ')')
            self.program += self._evaluate_expression(b.strip()) * condition
        elif "maximize" in line:
            b, _ = next_block(line, '(', ')')
            self.program -= self._evaluate_expression(b.strip()) * condition
        elif "enforce" in line:
            b, _ = next_block(line, '(', ')')
            args = [x.strip() for x in b.split(',')]
            exp, kwargs = args[0], {'lam': 1}
            for a in args[1:]:
                k, v = [x.strip() for x in a.split('=')]
                kwargs[k] = eval(v)
            kwargs['lam'] *= condition
            self._enforce(exp, **kwargs)
        else:
            # assignments
            k, v = [x.strip() for x in line.split('=')]
            self._variables[k] = self._evaluate_expression(v)
