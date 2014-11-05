"""
The structure class for ccpoviz
===============================

This module contains the class for representing a chemical structure, either in
isolated molecular form or crystal form. Just some very basic information are
stored.

"""

import collections


#
# Atom class
# ----------
#
# A simple class for atoms with just a symbol and coordinate.
#


Atom = collections.namedtuple('Atom', [
    'symbol',
    'coord',
    ])


#
# The structure class
# -------------------
#


class Structure(object):

    """Chemical structure class

    This class are for storing the enough information for plotting a structure
    out by using pov-ray. So it is at the central position of this piece of
    code, with readers generating its instances from the input file, and
    plotters writes the pov-ray files based on the information stored in its
    instances.

    .. py:attribute:: title

      An optional title for the structure, it can also be used for holding some
      instructions for plotting.

    .. py:attribute:: atms

      The list of atoms in the structure. The entries can be any type as long
      as they have got attribute ``symbol`` for the element symbol and
      ``coord`` for a numpy array of its coordinate. Any duck type works here.

    .. py:attribute:: bonds

      A list of bonds in the structure. Its entries should be tuples where the
      first two fields gives the zero-based indices of the atoms connected by
      the bond. And the next entry gives the bond order, which can be a float-
      point number to indicate partial bond.

    .. py:attribute: latt_vecs

      A list of three numpy vectors for the lattice vectors of the structure if
      it is crystalline. It should be set to ``None`` for molecules.

    """

    __slots__ = [
        'title',
        'atms',
        'bonds',
        'latt_vecs'
        ]

    def __init__(self, title):

        """Initializes a structure

        This is just a trivial initializer that initializes the title. All
        other fields are not touched. The actual content should be filled by
        individual readers.

        """

        self.title = title
        self.atms = []
        self.bonds = []
        self.latt_vecs = []

    def extend_atms(self, atms_iter):

        """Extends the atoms list by an iterator

        Any iterator iterating over a linear list of atoms objects will work.

        """

        self.atms.extend(atms_iter)

    def extend_bonds(self, bonds_iter):

        """Extends the bonding list by an iterator

        Any iterator iterating over a list of bonding triple will work.

        """

        self.bonds.extent(bonds_iter)

    def set_latt_vecs(self, latt_vecs):

        """Sets the lattice vectors"""

        self.latt_vecs = latt_vecs
