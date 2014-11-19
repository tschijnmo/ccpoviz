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

    p = functools.partial(  # pylint: disable=invalid-name
        print, file=sys.stderr
        )

    p('')
    p('*' * 80)
    p('FATAL ERROR!')
    p('*' * 80)
    p('')
    p(err_msg)
    p('')

    sys.exit(ret_code)


def format_vector(vec, float_format='%11.6f'):

    """Formats a vector into the pov-ray format

    :param vec: A triple of floating point numbers
    :param float_format: The format for formating floating point numbers into
        string
    :returns: A string for the formatted vector

    """

    return (
        '<' + (', '.join([float_format for _ in xrange(0, 3)])) + '>'
        ) % tuple(vec[i] for i in xrange(0, 3))
