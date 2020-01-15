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

"""Run ``qubovert.program`` as a module.

Continue

"""

from qubovert.program import compile_program
import argparse


def _compile_file(filename, **kwargs):
    """_compile_file.

    Compile the program given in the file.

    Parameters
    ----------
    filename : str.
        Filename of the file to compile.

    kwargs
    ------
    Optional keyword arguments. Coming soon.

    Return
    ------
    output_filename : str.
        The filename of the compiled output.

    """
    with open(filename) as f:
        program = f.read()
    output_filename = filename[:-filename[::-1].index('.')]
    with open(output_filename + 'pubo', 'w') as f:
        print(compile_program(program), file=f)
    return output_filename


def _run_file(filename, **kwargs):
    """_run_file.

    Run the compiled program given in the file.

    Parameters
    ----------
    filename : str.
        Filename of the file to run.

    kwargs
    ------
    Optional keyword arguments. Coming soon.

    Return
    ------
    None

    """
    with open(filename) as f:
        exec(f.read())


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        prog='qubovert.program',
        description='Programming with qubovert'
    )

    parser.add_argument('filename', type=str, help='file to use')
    parser.add_argument('-c', action="store_true", default=False, dest='c',
                        help='compile the file')
    parser.add_argument('-r', action="store_true", default=False, dest='r',
                        help='run the file after compiling')

    parsed, unknown = parser.parse_known_args()
    for arg in unknown:
        if arg.startswith(("-", "--")):
            parser.add_argument(arg, type=str)

    arguments = parser.parse_args()
    if not arguments.r and not arguments.c:
        raise ValueError("Must supply either/both -r and -c")

    filename = arguments.filename
    run, compile_ = arguments.r, arguments.c
    del arguments.r, arguments.c, arguments.filename
    kwargs = arguments.__dict__.copy()

    if compile_:
        filename = _compile_file(filename, **kwargs)
        print("File compiled to", filename)
    if run:
        _run_file(filename, **kwargs)
