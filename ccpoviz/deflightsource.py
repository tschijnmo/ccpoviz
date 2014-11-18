"""
Defining the light source for the Pov-ray visualization
=======================================================

In order to have natural soft shadows expected for molecular visualization, the
pov-ray ``area_light`` is going to be used by default. Different from the case
of the camera, here default values are tried to be made so that the user does
not have to intervene at all. However, some options are presented for better
visualization effect. The options are

location
    Where the centre of the light source is relative to the location of the
    camera. By default it is going to be one unit above the location of the
    camera

size
    The size of the area light. By default it is two units by two units

number
    The number of point light sources on each dimension. By default a
    :math:`5\\times 5` mesh is going to be used

focus
    Where the light is going to focus. By default it is going to focus on the
    same point as the camera. So this vector is given relative to the location
    of the camera focus.

rotation
    A roll rotation for the square area of the light source. It might not ever
    going to be changed.

Note that in the user input, both location and the focus are relative values
based on the location and focus of the camera.

"""

import math

import numpy as np
from numpy import linalg

from .util import format_vector, terminate_program


def compute_rotation(beg_vec, end_vec):

    """Computes the shorted rotation matrix based on the beginning and end

    The method is based on the first answer of this stack exchange `page`_. The
    numpy rotation array in going to be returned.

    .. _page: http://math.stackexchange.com/questions/180418

    """

    beg_n = beg_vec / linalg.norm(beg_vec)
    end_n = end_vec / linalg.norm(end_vec)

    v = np.cross(beg_n, end_n)  # pylint: disable=invalid-name
    s = linalg.norm(v)  # pylint: disable=invalid-name
    c = np.dot(beg_n, end_n)  # pylint: disable=invalid-name

    v_cross = np.array([
        [0.0, -v[2], v[1]],
        [v[2], 0.0, -v[0]],
        [-v[1], v[0], 0.0]
        ])

    return np.identity(3) + v_cross + (
        (np.dot(v_cross, v_cross) * ((1 - c) / (s ** 2)))
        )


def gen_light_ops(cam_loc, cam_foc, ops_dict):

    """Generate the options for the light source

    Note that different from the camera options, here a dictionary is going to
    be returned where the options can be extracted by tags with prefix
    ``light-``. The supported tags are

    * light-location
    * light-colour
    * light-area-vec-1
    * light-area-vec-2
    * light-number
    * light-adaptive
    * light-jitter

    The returned dictionary can be added to the rendering dictionary for
    mustache rendering.

    """

    # pylint: disable=too-many-locals

    try:
        loc_diff = np.array(ops_dict['light-location'], dtype=np.float64)
        foc_diff = np.array(ops_dict['light-focus'], dtype=np.float64)
    except ValueError:
        terminate_program('Invalid light location or focus')

    loc = cam_loc + loc_diff
    foc = cam_foc + foc_diff

    direction = foc - loc

    # In the same vein as the pov-ray camera, we rotation the z unit
    rotation = ops_dict['camera-rotation']
    rotation *= math.pi * 2.0 / 360.0
    size = ops_dict['camera-size']

    z_unit = np.array([0.0, 0.0, 1.0])
    base1 = np.array([
        math.cos(rotation), math.sin(rotation), 0.0
        ]) * size
    base2 = np.array([
        -math.sin(rotation), math.cos(rotation), 0.0
        ]) * size
    rotation_matrix = compute_rotation(z_unit, direction)
    area_vec_1 = np.dot(rotation_matrix, base1)
    area_vec_2 = np.dot(rotation_matrix, base2)

    # Process the adaptive a little bit to conform to the moustache requirement
    light_adaptive_inp = ops_dict['light-adaptive']
    if not light_adaptive_inp:
        light_adaptive_value = light_adaptive_inp
    else:
        light_adaptive_value = {'light-adaptive-value': light_adaptive_value}

    return {
        'light-location': format_vector(loc),
        'light-colour': ops_dict['light-colour'],
        'light-area-vec-1': format_vector(area_vec_1),
        'light-area-vec-2': format_vector(area_vec_2),
        'light-number': ops_dict['light-number'],
        'light-adaptive': light_adaptive_value,
        'light-jitter': ops_dict['light-jitter']
    }
