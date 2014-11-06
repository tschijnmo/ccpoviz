"""
Defining the camera for Pov-Ray visualization
=============================================

In order to hide the obsecure pov-ray camera definition from users, here
functions are provided to translate more user-friendly inputs into the pov-ray
options for the camera.

In order to specify a camera, the parameters needed are

focus
    The focus of the camera, where to look at. Normally this is going to be the
    centre of the molecule by default.

distance
    The distance from the camera to the focus.

theta, phi
    The inclination and azimuth angles for the camera, basically the camera to
    going to be placed at the position with spherical coordinate (distance,
    theta, phi) with the focus as the origin.

rotation
    The rotation of the camera within the plane of picturing.

aspect_ratio
    The aspect-ratio, default to 4:3.

"""


import math

import numpy as np

from .utils import format_vec, terminate_program, ensure_type


def compute_pos_ops(focus, distance, theta, phi, rotation, aspect_ratio):

    """Computes the camera options related to position and orientation

    The arguments are documented in the module definition. The result will be a
    list of dictionaries with the option name under the tag ``op-name`` and the
    option value under the tag ``op-value``. This can be direct used for
    rendering the pov-ray input mustache template.

    All the angles should be in radian.

    """

    camera_pos = np.array([
        math.sin(theta) * math.cos(phi), math.sin(theta) * math.sin(phi),
        math.cos(theta)
        ]) * distance + focus

    sky_vec = np.array([
        math.sin(rotation), math.cos(rotation), 0.0
        ])

    up_vec = np.array([0.0, 1.0, 0.0])
    right_vec = np.array([-aspect_ratio, 0.0, 0.0])

    ret_val = [
        ('location', format_vec(camera_pos)),
        ('up', format_vec(up_vec)),
        ('right', format_vec(right_vec)),
        ('sky', format_vec(sky_vec)),
        ('look_at', format_vec(focus))
    ]

    return [
        {'op-name': i[0], 'op-value': i[1]}
        for i in ret_val
    ]


def gen_camera_ops(ops_dict, structure):

    """Generate the list for the camera options

    This is a shallow wrapper of the above :py:func:`compute_pos_ops` where the
    reading and verification of the user input is also performed.

    :param ops_dict: The dictionary of options for the run
    :param structure: The structure to plot
    :returns: A list of dictionaries for rendering the camera in the pov-ray
        mustache template. The resulted list can be assigned to a key in the
        rendering dictionary.

    """

    # First we need to find the focus out
    focus_inp = ops_dict['camera-focus']
    if focus_inp == 'molecule-centre':
        focus = np.mean([
            i.coord for i in structure.atms
            ], axis=0)
    elif type(focus_inp) == list and len(focus_inp) == 3:
        focus = np.array(focus_inp)
    else:
        terminate_program(
            'Invalid camera-focus option: %r' % focus_inp
            )

    # Other parameters
    distance = ops_dict['camera-distance']
    ensure_type(distance, float, tag='camera-distance')

    to_radian = 2 * math.pi / 360.0
    theta = ops_dict['camera-theta']
    ensure_type(theta, float, tag='camera-theta')
    theta *= to_radian
    phi = ops_dict['camera-phi']
    ensure_type(phi, float, tag='camera-phi')
    phi *= to_radian
    rotation = ops_dict['camera-rotation']
    ensure_type(rotation, float, 'camera-rotation')
    rotation *= to_radian

    aspect_ratio = ops_dict['aspect-ratio']
    ensure_type(aspect_ratio, float, 'aspect-ratio')

    return compute_pos_ops(
        focus, distance, theta, phi, rotation, aspect_ratio
        )
