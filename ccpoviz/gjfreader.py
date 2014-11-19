"""
The reader for Gaussian input files
===================================

A primitive reader for Gaussian ``.gjf`` input files is defined here. Note that
basically it just read the atomic coordinate and the connectivity if possible.
And the atomic coordinate has to be in Cartesian format.

"""

import itertools

import numpy as np

from .structure import Atm, Structure


def get_gjf_sections(file_name):

    """Gets the sections of Gaussian input file

    The Gaussian input file contains sections divided by blank lines. This
    function will read the input file given by the input file name and return
    the sections of the input file, with each section given as a list of
    strings for the lines.

    :param file_name: The name of the input file
    :raises IOError: If the input file cannot be opened.

    """

    try:
        input_file = open(file_name, 'r')
    except IOError as err:
        raise IOError(
            'The given Gaussian input file cannot be opened!\n' + err.args
            )
    lines = [i.strip() for i in input_file]
    return [
        list(g) for k, g in itertools.groupby(lines, lambda x: x == '')
        if not k
        ]


def parse_coord(lines):

    """Parses the atomic coordinate section of the gjf file

    :param lines: The section for coordinates of the atoms
    :raises ValueError: If the format is not correct
    :returns: A pair, with the first field being the list of atomic
        coordinates, the second being the lattices vectors. Empty list for
        non-periodic systems,

    """

    atms = []

    # skip the charge and spin multiplicity
    for i in lines[1:]:
        fields = i.split()
        symb = fields[0]
        try:
            coord = np.array(fields[1:4], dtype=np.float64)
        except ValueError as verr:
            raise ValueError(
                'Corrupt atomic coordinate in gjf file:\n' + verr.args
                )
        atms.append(Atm(symb=symb, coord=coord))
        continue

    latt_vecs = [i[1] for i in atms if i[0] == 'Tv']

    return (
        [i for i in atms if i[0] != 'Tv'],
        latt_vecs
        )


def parse_connectivity(lines):

    """Parses the connectivity section of the gjf file

    :param lines: The lines of the section
    :raises ValueError: if the format is not correct

    """

    bonds = []

    for l_i in lines:
        fields = l_i.split()
        try:
            # Need to convert one-based input to zero-based indices
            start = int(fields[0]) - 1
            # Parition into pairs, based on the official recipe in
            # itertools
            it1 = iter(fields[1:])
            it2 = it1
            for conn in itertools.izip_longest(it1, it2, fillvalue=None):
                end = int(conn[0]) - 1
                bond_order = float(conn[1])
                bonds.append(
                    (start, end, bond_order)
                    )
        except ValueError as verr:
            raise ValueError(
                'Corrupt connectivity in gjf file:\n' + verr.args
                )

    return bonds


def parse_gjf(file_name):

    """Parses a Gaussian gjf file based on the input file name

    :param file_name: The name of the input file
    :raises IOError: if the file cannot be opened
    :raises ValueError: if the file is not of correct format

    """

    sections = get_gjf_sections(file_name)

    if len(sections) < 3:
        raise ValueError('There is no atomic coordinate section in the input')

    title = sections[1]
    atms, latt_vecs = parse_coord(sections[2])
    if len(sections) > 3:
        bonds = parse_connectivity(sections[3])
    else:
        bonds = []

    structure = Structure(title)
    structure.extend_atms(atms)
    structure.extend_bonds(bonds)
    structure.set_latt_vecs(latt_vecs)

    return structure
