"""
The driver function for rendering
=================================

This module contains the main driver function for the entire rendering process
from the template initialization to the pov-ray invocation.

"""


from .readstructure import read_structure
from .getoptions import get_options
from .renderpov import render_pov
from .runpov import run_pov


def render_driver(input_file, input_reader, molecule_option, project_option,
                  output_file, if_keep):

    """The main driver function"""

    # Read the molecule
    structure = read_structure(input_file, input_reader)

    # Get the options
    options = get_options(molecule_option, structure, project_option)

    if output_file is None:
        output_file = input_file.split('.')[0] + '.png'

    render_pov(structure, output_file, options)
    run_pov(output_file, if_keep, options)

    return 0
