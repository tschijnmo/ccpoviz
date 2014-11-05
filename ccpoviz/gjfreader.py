"""
The reader for Gaussian input files
===================================

A primitive reader for Gaussian ``.gjf`` input files is defined here. Note that
basically it just read the atomic coordinate and the connectivity if possible.
And the atomic coordinate has to be in Cartesian format.

"""

import itertools

import numpy as np

from .structure import Atom, Structure


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
            'The given Gaussian input file cannot be opened!\n' + err.value
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
        coordinates, the second being the lattices vectors. ``None`` for non-
        periodic systems.

    """

    atms = []

    # skip the charge and spin multiplicity
    for i in lines[1:]:
        fields = i.split()
        symbol = fields[0]
        try:
            coord = np.array(fields[1:3], type=np.float64)
        except ValueError as ve:
            raise ValueError(
                'Corrupt atomic coordinate in gjf file:\n' + ve.value
                )
        atms.append(Atom(symbol=symbol, coord=coord))
        continue

    latt_vecs = [i[1] for i in atms if i[0] == 'Tv']

    return (
        [i for i in atms if i[0] != 'Tv'],
        None if latt_vecs == [] else latt_vecs
        )


def parse_connectivity(lines):

    """Parses the connectivity section of the gjf file

    :param lines: The lines of the section
    :raises ValueError: if the format is not correct

    """

    bonds = []

    for l in lines:
        fields = l.split()
        try:
            start = int(fields[0]) - 1
            args = [iter(fields[1:])] * 2
            for conn in itertools.izip_longest(*args, fillvalue=''):
                end = int(conn[0]) - 1
                bond_order = float(conn[1])
                bonds.append(
                    (start, end, bond_order)
                    )
        except ValueError as ve:
            raise ValueError(
                'Corrupt connectivity in gjf file:\n' + ve.value
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
        bonds = None

    struct = Structure(title)
    struct.extend_atms(atms)
    struct.extend_bonds(bonds)
    struct.set_latt_vecs(latt_vecs)
