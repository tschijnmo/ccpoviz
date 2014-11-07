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


def format_vector(vec, float_format='%11.6f'):

    """Formats a vector into the pov-ray format

    :param vec: A triple of floating point numbers
    :param float_format: The format for formating floating point numbers into
        string
    :returns: A string for the formatted vector

    """

    return (
        '<' + (', '.join([float_format for i in xrange(0, 3)])) + '>'
        ) % tuple(vec[i] for i in xrange(0, 3))


def ensure_type(value, expected_type, tag='', terminate=True):

    """Ensures that the given value is indeed of the expected type

    :param value: The value to examine
    :param expected_type: The expected type of the value
    :param tag: A tag can be given to the value for pretty printing of the
        error message.
    :param terminate: If true, the function will abort the program, or it will
        just return the boolean value indicating if the type mataches
        expectation.

    """

    res = type(value) == expected_type

    if terminate and (not res):
        terminate_program(
            "The value %s cannot match the expected of type %s" % expected_type
            )
    else:
        return res


def wrap_str_list(str_list, tag='content'):

    """Wraps a string list into a list of dictionaries for mustache rendering

    In mustache, the non-empty list for sections needs to have entries of
    dictionaries, where the template is able to get the information. When this
    function is given a list of strings, a list of dictionaries is going to be
    returned with the original strings stored with the tag given, which
    defaults to ``content``.

    """

    return [
        {tag: i} for i in str_list
        ]
