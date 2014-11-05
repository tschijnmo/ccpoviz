"""
Converting the colour table on the Wikipedia CPK article to JSON format
=======================================================================

The Wikipedia article on `CPK colouring`_ contains a nice table for the colours
for each element in various colouring schemes. This script aims to convert that
table into a JSON file that can be used for Pov-Ray visualization.

The table, with only the main row entries, are read from the standard input.
The JSON file are going to be written to the standard output. In the JSON file,
the root element is a dictionary with the colouring scheme as the key,
currently the keys are ``CPK``, ``Koltun``, ``Jmol``, and ``Rasmol``. For each
colouring scheme, the entry is a dictionary with the element symbol as the key
and the colour in the Pov-Ray RGB vector format as value in string.

.. _CPK colouring:,http://en.wikipedia.org/wiki/CPK_coloring>

"""

from __future__ import print_function

import json
import itertools
import re
import sys


def break_into_rows(lines):

    """Breaks the list of lines into sections for each element"""

    row_brk = re.compile(r'^ *\|- *$')
    if_brk = lambda l: row_brk.match(l) is not None

    return [
        list(g) for k, g in itertools.groupby(lines, if_brk) if not k
    ]


def get_elem_symb(line):

    """Gets the element symbol on a line

    If the symbol is for an isotope, ``None`` is going to be returned.

    """

    symb_re = re.compile(
        r'(?P<iso><sup>\d*</sup>)? *(?P<symb>[A-Z][a-z]?)'
        )
    search_res = symb_re.search(line)

    if search_res.group('iso') is not None:
        return None
    else:
        return search_res.group('symb')


def get_pov_rgb(line):

    """Converts a line from Wikipedia into a string for pov-ray rgb colour

    A ``None`` will be returned if the colour cannot be found on the given
    line.
    """

    c_re = re.compile(
        r'colorbox\|#(?P<r>.{2})(?P<g>.{2})(?P<b>.{2})\}\} *$'
        )
    color_max = 255.0

    search_res = c_re.search(line)
    if search_res is None:
        return None
    raw_intensities = (
        search_res.group(i)
        for i in ['r', 'g', 'b']
        )

    intensities = (
        int(i, 16) / color_max
        for i in raw_intensities
    )

    return 'rgb <%4.2f, %4.2f, %4.2f>' % tuple(intensities)


def to_dicts(rows, n_schemes):

    """Convert the lines into dictionaries of colours

    A list of ``n_schemes`` dictionaries are going to be returned for the
    ``n_schemes`` colouring schemes.

    :param rows: A list of rows in the table, as nested list of lines
    :param n_schemes: The number of colouring schemes on each row

    """

    ret_val = [dict() for i in xrange(0, n_schemes)]

    for row_i in rows:

        symb = get_elem_symb(row_i[1])
        if symb is None:
            continue

        for i, l in enumerate(row_i[3:3 + n_schemes]):
            colour = get_pov_rgb(l)
            if colour is not None:
                ret_val[i][symb] = colour

    return ret_val


def main():

    """The main driver function"""

    rows = break_into_rows([i for i in sys.stdin])
    dicts = to_dicts(rows, 4)

    res = {
        'CPK': dicts[0],
        'Koltun': dicts[1],
        'Jmol': dicts[2],
        'Rasmol': dicts[3]
    }

    print(json.dumps(res, indent=4))

    return 0


if __name__ == '__main__':
    main()
