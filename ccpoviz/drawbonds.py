"""
Drawing bonds for the molecule
==============================

This module basically contains two parts, the derivation of the connectivity
information and their transformation into POV-Ray format. In the middle, the
module :py:mod`bonds2cylinder` is used for converting the connectivity to the
cylinders.

After the conversion, the list of dictionaries for rendering the POV-Ray
mustache templates is formed. Each dictionary consists of the following fields

begin, end
    The two ends of the cylinder

radius
    The radius

texture, pigment, normal, finish
    The texture attributes, with each being a list of dictionaries holding the
    actual options under the tag ``content``.

"""

import itertools
import json

import numpy as np
import pkg_resources

from .bonds2cylinder import bonds2cylinders
from .util import ensure_type, format_vector, wrap_str_list


def compute_bonds(structure, ops_dict):

    """Computes the bonds in a structure based on the covalent radius

    Any two atoms with separation less than the sum of their covalent radii
    will be considered to be connected. The results are returned as a list of
    triples for the bonds. Note that in the current implementation, the bond
    order is always set to one.

    """

    default_radii = json.reads(
        pkg_resources.resource_string(__name__, 'data/covradius.json')
        )
    default_radii.update(
        ops_dict['covalent-radii']
        )

    bonds = []
    for atm1, atm2 in itertools.combinations(enumerate(structure.atms), 2):

        idx1 = atm1[0]
        idx2 = atm2[0]
        symb1 = atm1[1].symb
        symb2 = atm2[1].symb
        coord1 = atm1[1].coord
        coord2 = atm2[1].coord

        threshold = default_radii[symb1] + default_radii[symb2]
        dist = np.norm(coord1 - coord2)

        if dist < threshold:
            bonds.append(
                (idx1, idx2, 1.0) if idx1 < idx2 else (idx2, idx1, 1.0)
                )

    return bonds


def update_bonds(existing_bonds, new_bonds):

    """Update a list of existing bonds according two the new list of bonds

    Non-existing bonds are added, existing ones are changed order according to
    the new bonds. If the new order is zero, the connection is going to be
    removed.

    """

    # make a shallow copy
    bonds = list(existing_bonds)

    for b_i in new_bonds:

        try:
            old_idx = existing_bonds.index(b_i)
        except ValueError:
            bonds.append(
                b_i if b_i[0] < b_i[1] else (b_i[1], b_i[0], b_i[2])
                )
            continue

        if abs(new_bonds[2] - 0.0) < 0.1:
            del bonds[old_idx]
        else:
            bonds[old_idx] = b_i

    return bonds


def form_bonds_list(structure, ops_dict):

    """Forms the final list of bonds

    The returned list contains the triples for each bond.

    """

    if ops_dict['compute-bonds']:
        raw_bonds = compute_bonds(structure, ops_dict)
    else:
        raw_bonds = []

    bonds = update_bonds(raw_bonds, structure.bonds)

    return bonds


def cylinder2pov(cylinders, ops_dict):

    """Converts the internal cylinder data structure to pov-ray dictionaries

    The cylinders should be in the intern data structure as defined in
    :py:mod:`bonds2cylinder` module. Here in this implementation, just the
    beginning and end points are actually used. Other fields in the structure
    were intended to be helpful for possible future features.

    The returned list of dictionaries has got the format documented in this
    module.

    """

    # Get the bond representation parameters
    radius = ops_dict['bond-cylinder-radius']
    ensure_type(radius, float, 'bond-cylinder-radius')
    texture = wrap_str_list(ops_dict['bond-texture'])
    pigment = wrap_str_list(ops_dict['bond-pigment'])
    normal = wrap_str_list(ops_dict['bond-normal'])
    finish = wrap_str_list(ops_dict['bond-finish'])

    return [
        {
            'begin': format_vector(i.beg_coord),
            'end': format_vector(i.end_coord),
            'radius': '%8.4f' % radius,
            'texture': texture,
            'pigment': pigment,
            'normal': normal,
            'finish': finish

        }
        for i in cylinders
        ]


def draw_bonds(structure, camera, ops_dict):

    """Forms the bonds list"""

    separation = ops_dict['multiple-bond-sepration']
    ensure_type(separation, float, 'multiple-bond-separation')
    dash_size = ops_dict['partial-bond-dash-size']
    ensure_type(dash_size, float, 'partial-bond-dash-size')

    bonds = compute_bonds(structure, ops_dict)
    cylinders = bonds2cylinders(
        bonds, structure.atms, camera, separation, dash_size
        )

    return cylinder2pov(cylinders, ops_dict)