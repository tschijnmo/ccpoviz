"""
Read structures from input file
===============================

This module contains driver function for reading a molecular structures from a
given input file with a given reader. The reader is given as a string.

"""

from .gjfreader import parse_gjf


def read_structure(input_file, reader):

    """Reads a structure from a input file

    :param input_file: The file name of the input file
    :param reader: A string giving the reader for reading the file
    :returns: A structure object containing the molecule that is read

    """

    if reader == 'gjf':
        return parse_gjf(input_file)
    else:
        raise ValueError('Input file unreadable')
