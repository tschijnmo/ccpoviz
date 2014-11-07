"""
Write the covalent radius of elements
=====================================

The covalent radius are read from the `periodictable`_ module and then dumped
into a JSON file. In this way, the user does not have to install the uncommon
package any more.

.. _periodictable: http://http://www.reflectometry.org/danse/docs/elements

"""

from __future__ import print_function

import json

import periodictable as pt


def main():

    """The main driver function"""

    cov_radius = dict(
        (elem_i.symbol, elem_i.covalent_radius)
        for elem_i in pt.elements
        if elem_i.covalent_radius is not None
        )

    print(json.dumps(cov_radius, indent=4))

    return 0

 
if __name__ == '__main__':
    main()

