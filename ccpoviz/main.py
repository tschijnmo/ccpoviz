"""
The main driver module for the code
===================================

This module contains the main driver function for the code, which should be
called by the executable of the program.

"""


import argparse

from .renderdriver import render_driver


def main():

    """The main driver function"""

    parser = argparse.ArgumentParser(
        description='Plotting the molecule from an input file',
        epilog='by Tschijnmo TSCHAU <tschijnmotschau@gmail.com>'
        )
    parser.add_argument('INPUT', metavar='FILE', type=str, nargs=1,
                        help='The name of the input file')
    parser.add_argument('-r', '--reader', type=str, default='gjf',
                        choices=['gjf', ],
                        help='The reader for the input file')
    parser.add_argument('-o', '--output', type=str,
                        help='The output file, default to input file name'
                        'with extension changed to png')
    parser.add_argument('-k', '--keep', action='store_true',
                        help='Keep the pov-ray input file')
    parser.add_argument('-p', '--project-option', type=str,
                        help='The project level JSON/YAML configuration file')
    parser.add_argument('-m', '--molecule-option', type=str,
                        help='The molecule level JSON/YAML configuration file'
                        ', can be set to `input-title` to use the title of'
                        ' the input file')
    args = parser.parse_args()

    render_driver(
        args.INPUT[0], args.reader, args.molecule_option,
        args.project_option, args.output, args.keep
        )

    return 0
