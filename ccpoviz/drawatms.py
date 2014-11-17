"""
Draw the atoms as pov-ray spheres
=================================

The core of this module will form a list of dictionaries with each entry for
each atom in the system. For each entry, the follow fields are set

location
    The Cartesian coordinate of the location in pov-ray vector format

radius
    A float giving the radius of the sphere

texture, pigment, normal, finish
    Each are going to hold a list of strings holding the settings of the
    options in Pov-ray. The strings should be put into the correct position in
    the pov-ray file.

The resulted dictionary can be used in pov-ray input file mustache template
rendering directly.

"""

import json
import pkg_resources
import copy

from .util import terminate_program, format_vector


def get_radius(elem_symb, ops_dict):

    """Gets the radius of a given element symbol from user input"""

    radius_dict = ops_dict['element-radii']
    radius = radius_dict.get(elem_symb, radius_dict['default'])

    return radius


def form_colour_dict(ops_dict):

    """Forms a dictionary for looking colours up

    It is based on the colour scheme that is selected and the user
    modifications.

    """

    default_schemes_str = pkg_resources.resource_string(
        __name__, 'data/defaultcolour.json'
        )
    default_schemes = json.loads(default_schemes_str)

    scheme = ops_dict['element-colour-scheme']
    try:
        colour_dict = default_schemes[scheme]
    except KeyError:
        terminate_program(
            'The element colour scheme %s does not exists' % scheme
            )

    colour_dict.update(ops_dict['element-colour-change'])

    return colour_dict


def get_texture(elem_symb, colour_dict, ops_dict):

    """Get the texture for a given element symbol

    The result will be of the final format, just only keys for textures will be
    present.

    """

    textures_dict = ops_dict['element-textures']
    # Make a copy, even the explicitly given ones are based on the default.
    raw_texture = copy.deepcopy(textures_dict['default'])
    if elem_symb in textures_dict:
        raw_texture.update(raw_texture[elem_symb])

    texture_list = raw_texture['texture']
    pigment_list = raw_texture['pigment']
    if raw_texture['use-color']:
        pigment_list.append('colour %s' % colour_dict[elem_symb])
    normal_list = raw_texture['normal']
    finish_list = raw_texture['finish']

    return {
        'texture': texture_list,
        'pigment': pigment_list,
        'normal': normal_list,
        'finish': finish_list
        }


def draw_atms(structure, ops_dict):

    """Draws the atoms in a structure

    The returned will be a list that can be assigned into the rendering
    dictionary under a key for rendering the mustache template.

    """

    colour_dict = form_colour_dict(ops_dict)
    atms = structure.atms

    atms_list = []
    for atm_i in atms:
        atm_dict = {
            'location': format_vector(atm_i.coord),
            'radius': get_radius(atm_i.symb, ops_dict)
            }

        atm_dict.update(
            get_texture(atm_i.symb, colour_dict, ops_dict)
            )
        atms_list.append(atm_dict)

    return atms_list
