"""
Invoke the POV-Ray program for the rendering the picture
========================================================

This module is able to run the main POV-Ray program to generate the final
picture. In order for this to be successful, by default the POV-Ray main
program must reside somewhere in the system ``PATH`` so that it can be invoked
with only ``povray``, or the ``povray-program`` setting can be set for an
alternative location.

"""

import subprocess
import os

from .util import terminate_program


def run_pov_core(povray_prog, input_file, output_file, width, aspect_ratio,
                 additional_arg=None):

    """Invokes the pov-ray program

    This is the core function that invokes the pov-ray program for rendering
    the pov-ray input file.

    :param povray_prog: The string for the pov-ray program
    :param output_file: The name of the output file, the pov input file should
        have the same base name just a different extension.
    :param width: The width of the render in pixels
    :param aspect_ratio: The width to height aspect ratio

    """

    # pylint: disable=too-many-arguments

    additional_arg = [] or additional_arg
    height = round(width / aspect_ratio)

    return subprocess.call(
        [
            povray_prog, '+I%s' % input_file, '+W%d' % width,
            '+H%d' % height, '+O%s' % output_file
        ] + additional_arg
        )


def run_pov(output_file, if_keep, ops_dict):

    """The driver for invoking pov-ray

    :param output_file: The name of the output file
    :param if_keep: if the pov-ray input file is going to be kept after
        rendering
    :param ops_dict: The options dictionary

    """

    input_file = output_file.split('.')[0] + '.pov'
    if ops_dict['background-colour'] == '':
        additional_arg = ['+UA']
    else:
        additional_arg = []

    ret_code = run_pov_core(
        ops_dict['pov-ray-program'], input_file, output_file,
        ops_dict['graph-width'], ops_dict['aspect-ratio'],
        additional_arg=additional_arg
        )
    if ret_code != 0:
        terminate_program('Pov-ray returned with error!')

    if not if_keep:
        os.remove(input_file)

    return None
