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

"""_parse_helper.py.

Helpers for parsing ``qubovert`` code.

"""

__all__ = 'next_block',


def next_block(code, open_='{', close='}'):
    """next_block.

    Get the code inside the opening and closing brackets.

    Parameters
    ----------
    code : str.
    open : str (optional, defaults to ``'{'``).
        The opening bracket to look for.
    close : str (optional, defaults to ``'}'``)
        The closing bracket to look for.

    Return
    ------
    res : tuple (str, int).
        The str is the code inside the brackets. The int is the index after the
        last bracket.

    Example
    -------
    >>> code = 'if x {if y {if x {do}}}'
    >>> first = next_block(code)
    >>> second = next_block(first)
    >>> third = next_block(second)
    >>> first
    if y {if x {do}}
    >>> second
    if x {do}
    >>> third
    do

    """
    code = code[code.index(open_)+1:]
    count, i = 1, 0
    for s in code:
        if s == open_:
            count += 1
        elif s == close:
            count -= 1
        if not count:
            return code[:i], i+1
        i += 1
