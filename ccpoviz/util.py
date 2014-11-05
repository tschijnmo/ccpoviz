"""
Utility functions
=================

This module defines some utility functions that can be used in multiple
unrelated part of the code, such as error reporting.

"""

from __future__ import print_function

import sys
import functools


def terminate_program(err_msg, ret_code=1):

    """Terminates the current program

    :param err_msg: The error message to be printed out
    :param ret_code: The return code for the termination of the program

    """

    p = functools.partial(print, file=sys.stderr)

    p('')
    p('*' * 80)
    p('FATAL ERROR!')
    p('*' * 80)
    p('')
    p(err_msg)
    p('')

    sys.exit(ret_code)

