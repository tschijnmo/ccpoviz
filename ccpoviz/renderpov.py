"""
Pov-ray template rendering
==========================

This is a driver module that renders the pov-ray template for the given
molecule and user configuration based on the several other modules for
transforming molecular information into more and more primtive pov-ray objects.

"""

import pystache
import pkg_resources

from .defcamera import gen_camera_ops
from .deflightsource import gen_light_ops
from .drawatms import draw_atms
from .drawbonds import draw_bonds


def gen_render_dict(structure, ops_dict):

    """Generates the dictionary for rendering the template"""

    render_dict = {}

    cam_dict, cam_loc, cam_foc = gen_camera_ops(ops_dict, structure)
    render_dict['camera'] = cam_dict

    lightsouce_dict = gen_light_ops(cam_loc, cam_foc, ops_dict)
    render_dict.update(lightsouce_dict)

    atms_list = draw_atms(structure, ops_dict)
    render_dict['atoms'] = atms_list

    bonds_list = draw_bonds(structure, cam_loc, ops_dict)
    render_dict['bonds'] = bonds_list

    bkg_colour = ops_dict['background-colour']
    if bkg_colour == '':
        bkg_list = []
        if_bkg = False
    else:
        bkg_list = [
            'colour %s' % bkg_colour
            ]
        if_bkg = True
    render_dict['use-background'] = if_bkg
    render_dict['background-settings'] = bkg_list

    return render_dict


def render_pov(structure, output_file, ops_dict):

    """Renders the pov-ray template to output file

    :param structure: The structure to render
    :param output_file: The name of the output file
    :param ops_dict: The options dictionary

    """

    render_dict = gen_render_dict(structure, ops_dict)

    template = pkg_resources.resource_string(
        __name__, 'data/default.pov.mustache'
        )
    texture_partial = pkg_resources.resource_string(
        __name__, 'data/texturedef.pov.mustache'
        )

    renderer = pystache.Renderer(partials={'texturedef': texture_partial})
    result = renderer.render(template, render_dict)

    pov_file = open(
        output_file.split('.')[0] + '.pov',
        'w'
        )
    pov_file.write(result)

    return None
