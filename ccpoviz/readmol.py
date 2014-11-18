"""
Read molecules from input file
==============================

This module contains driver function for reading a molecule from a given input
file with a given reader. The reader is given as a string.

"""

from .gjfreader import parse_gjf


def read_mol(input_file, reader):

    """Reads a molecule from a input file

    :param input_file: The file name of the input file
    :param reader: A string giving the reader for reading the file
    :returns: A structure object containing the molecule that is read

    """

    if reader == 'gjf':
        return parse_gjf(input_file)
    else:
        raise ValueError('Input file unreadable')
