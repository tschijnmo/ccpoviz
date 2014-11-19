"""
Converting bonds into a list of cylinders
=========================================

The bonds in the bonds list of the :py:class:`Structure` objects are chemical
rather than graphical objects. First it does not handel the multiple bonds. And
it does not handle partial bonds as well.

In this module, functions are defined that is able to convert a list of bonds
into a list of cylinder start and end points that is able to be used for
plotting.

"""

import math
import collections

import numpy as np
from numpy import linalg


#
# Placing multiple bonds and resolving partial bonds
# --------------------------------------------------
#
# When more than one bonds are present, they are going to be nudged from the
# line connecting the two bonded atoms to have them separated visually.
#
# Partial bonds are going to be resolved into a series of small cylinders based
# on the size of each dash.
#
# This sections contains utility functions for these purposes, but does not
# return the full bond cylinder data structure.
#


def compute_mov_dir(atms, camera, bond):

    """Computes the movement direction for a given bond

    The basic strategy here is that the multiple bonds should always be seen
    clearly by the viewer at the camera position. So for a multiple bond, the
    bonds should be separated in the direction that is perpendicular to the
    vector from the camera to the centre of the bond.

    :param atms: The list of atoms
    :param camera: The numpy array for the location of the camera
    :param bond: A bond triple for the bond to be processed
    :returns: A normalized numpy array giving the direction to translate the
        bonds in the multiple bonds

    """

    atm1c = atms[bond[0]].coord
    atm2c = atms[bond[1]].coord

    bond_centre = (atm1c + atm2c) / 2.0
    bond_direction = atm2c - atm1c

    vec_from_cam = bond_centre - camera
    cross_prod = np.cross(bond_direction, vec_from_cam)

    return cross_prod / linalg.norm(cross_prod)


def compute_mov_amts(separation, n_bonds):

    """Computes the amount of movement for the multiple bond

    The movement is computed such that the centre will always coincide with the
    original line linking the two bonded atoms.

    :param separation: A floating point number giving the separation between
        the multiple bonds.
    :param n_bonds: The number of bonds
    :returns: A list of floating-point numbers for the movement

    """

    n_pair = n_bonds // 2
    n_rem = n_bonds % 2

    # beg holds the beginning of the positive and negative directions
    if n_rem == 0:
        amts = []
        beg = (separation / 2.0, -separation / 2.0)
    else:
        amts = [0.0]
        beg = (separation, -separation)

    for i in xrange(0, n_pair):
        amts.append(beg[0] + i * separation)
        amts.append(beg[1] - i * separation)

    return amts


def resolve_multiple_bond(atms, camera, separation, bond):

    """Resolves a multiple bond into several cylinder beginning and end points

    In addition to the beginning and end coordinates in numpy array format,
    there is going to be a third boolean field indicating if the bond is going
    to be a partial one. ``True`` for partial bond.

    """

    move_dir = compute_mov_dir(atms, camera, bond)

    n_bonds = int(math.ceil(bond[2]))
    if_partial = (n_bonds - bond[2]) > 0.1
    move_amts = compute_mov_amts(separation, n_bonds)

    res = []
    for i, amt in enumerate(move_amts):
        beg = atms[bond[0]].coord + amt * move_dir
        end = atms[bond[1]].coord + amt * move_dir
        res.append((beg, end,
                    if_partial if i == len(move_amts) - 1 else False))

    return res


def to_partial(cylinder, dash_size):

    """Break a cylinder for a full bond into dashed partial bond

    :param cylinder: A pair of numpy arrays for the beginning and end of the
        cylinder for the full bond
    :param dash_size: The float for the size of a dash in the partial bond
    :returns: A list of pairs of begin and end for the dashes

    """

    vec = cylinder[1] - cylinder[0]
    vec_norm = linalg.norm(vec)
    one_step = vec / vec_norm * dash_size

    # draw the cylinders one by one until it is going to exceed the full length
    dashes = []
    if_dash = True  # if we are currently drawing a dash
    dist = 0.0  # the distance covered
    beg = cylinder[0]
    while dist + dash_size < vec_norm:

        end = beg + one_step
        if if_dash:
            dashes.append((beg, end))

        beg = end
        dist += dash_size
        if_dash = not if_dash

    # draw the last step
    if if_dash:
        dashes.append((beg, cylinder[1]))

    return dashes


#
# Bond cylinder data structure
# ----------------------------
#
# Besides the beginning and end of the cylinders, additional information might
# be needed for further processing. To facilitate the possible further
# processing of the cylinders, here a shallow data structure is defined to hold
# additional information. ``beg_coord`` and ``end_coord`` are the beginning and
# ending coordinate of the cylinder, ``beg_atm``, ``end_atm`` are the integral
# index of the beginning and end atom. ``bond_sn`` is an integer giving a zero-
# based serial number for the bond among bonds with the beginning and end atom.
# The last one is the partial one if one of the bonds are partial. And
# ``if_partial`` contains the boolean explicitly. ``total_order`` gives the
# total order of the bond.
#
# In this way, this module is able to resolve the bonds into cylinders, while
# the additional information could be used for colouring or other additional
# processing.
#


BondCylinder = collections.namedtuple(
    'BondCylinder',
    [
        'beg_coord',
        'end_coord',
        'beg_atm',
        'end_atm',
        'bond_sn',
        'total_order',
        'if_partial'
    ]
    )


def bonds2cylinders(bonds, atms, camera, separation, dash_size):

    """Convert bonds to a list of bond cylinders

    This function converts a bond list into a list of cylinders that can be
    used for plotting. The cylinders are given as :py:class:`BondCylinder`
    instances

    :param bonds: A list of bonds, as the triple
    :param atms: A list of atoms
    :param separation: The separation between multiple bonds
    :param dash_size: The size of each dash for partial bonds
    :returns: A list of BondCylinder instances

    """

    cylinders = []

    for bond_i in bonds:
        resolved_bonds = resolve_multiple_bond(
            atms, camera, separation, bond_i
            )

        for sn_i, res_bond_i in enumerate(resolved_bonds):

            if_partial = res_bond_i[2]
            if if_partial:
                dashes = to_partial(res_bond_i, dash_size)
            else:
                dashes = [res_bond_i, ]

            cylinders.extend(
                BondCylinder(beg_coord=i[0], end_coord=i[1],
                             beg_atm=bond_i[0], end_atm=bond_i[1],
                             bond_sn=sn_i, total_order=bond_i[2],
                             if_partial=if_partial)
                for i in dashes
                )

    return cylinders
