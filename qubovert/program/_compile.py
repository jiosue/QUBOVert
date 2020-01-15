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

"""_compile.py.

Contains the ``compile_program`` function. See
``help(qubovert.program.compile_program)``.

"""

from ._parse_variables_helper import parse_variables_code
from ._parse_program_helper import parse_program_code
from ._parse_main_helper import parse_main_code
from ._parse_helper import next_block


__all__ = "compile_program",


def compile_program(program):
    """compile_program.

    Compile the program to a PUBO.

    Parameters
    ----------
    program : str.
        Etc.

    Return
    ------
    res : str.
        Running ``exec(res)`` will run the compiled program.

    Example
    -------
    >>> program = '''
    >>>     variables {
    >>>         binary x, y;
    >>>         integer(3) i;
    >>> }
    >>>     program {
    >>>         if(x); {
    >>>             enforce(y, lam=4);
    >>>         }
    >>>         if (i <= 2); {
    >>>             enforce(not y, lam=2);
    >>>         }
    >>>         minimize((i - 2) ** 2);
    >>>     }
    >>>     main {
    >>>         // main is run after program is run.
    >>>         disp("i: %g, x: %d, y: %g", i, x, y);
    >>>     }
    >>> '''
    >>> compiled_program = compile_program(program)
    >>> print(compiled_program)
    import qubovert
    # create program
    i = {}
    x = {}
    y = {}
    program = {}
    # run program
    __solution__ = qubovert.utils.solve_pubo_bruteforce(program)[1]
    # run main
    print(
        'i: %g, x: %d, y: %g' % (
            qubovert.utils.pubo_value(i, __solution__),
            qubovert.utils.pubo_value(x, __solution__),
            qubovert.utils.pubo_value(y, __solution__),
        )
    )
    >>> exec(compiled_program)

    """
    res = "import qubovert\n\n"

    # add varaibles to res
    i = program.index("variables")
    p = program[i+9:].strip()
    b, qubovert_vars = parse_variables_code(next_block(p)[0])
    res += b + "\n"

    # add program to res
    i = program.index("program")
    p = program[i+7:].strip()
    res += parse_program_code(next_block(p)[0], qubovert_vars)

    res += "\n\n# run program\n"
    res += "__solution__ = qubovert.utils.solve_pubo_bruteforce(program)[1]"
    res += "\n\n"

    # add main contents to res
    i = program.index("main")
    p = program[i+4:].strip()
    res += parse_main_code(next_block(p)[0], qubovert_vars)

    return res
