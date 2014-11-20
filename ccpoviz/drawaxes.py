"""
Coordinate axes drawing
=======================

For better setting of the theta and phi values for the camera, a tentative
rendering of the coordinate axes can be very helpful. Note that the coodinate
axes is not supposed for great publication quality, but just for aiding the
setting of the parameters only.

So the three axes will just be rendered very simply as three arrows with colour
of red, green and blue, for the x, y, and z bases respectively.

Three options will be used in the configuration, ``draw-axes`` is a boolean
setting whether the coordinates axes will be rendered at all, by default it is
false. ``axes-length`` and ``axes-radius`` sets the length and radius of the
coordinates.

"""

from .util import format_vector


# Some constants for controlling the rendering of the coordinate axes. They
# unlikely need any twicking so they are not put in the user options.
COLOURS = ['Red', 'Green', 'Blue']
TIP_LENGTH_FACTOR = 0.2
TIP_BASE_FACTOR = 3


def draw_axes(focus, ops_dict):

    """Generates the dictionary for drawing the coodinate axes

    The returned will be a list of dictionaries for rendering the axes, the
    important fields are

    begin
        The begin coodinate of the line

    end
        The end coodinate of the line

    tip
        The coordinate of the tip of the cone

    radius
        The radius of the line

    tip-base-radius
        The radius of the base of the tip

    colour
        The colour of the axis

    :param focus: The focus of the camera
    :param ops_dict: The dictionary for the options
    :returns: The list of dictionaries for rendering the coodinate axes

    """

    line_length = ops_dict['axes-length']
    tip_length = line_length * TIP_LENGTH_FACTOR
    line_radius = ops_dict['axes-radius']
    tip_radius = line_radius * TIP_BASE_FACTOR

    axes_list = []

    begin = format_vector(focus)
    for i in xrange(0, 3):
        end = [
            focus[j] + (0 if j != i else line_length)
            for j in xrange(0, 3)
            ]
        tip = [
            focus[j] + (0 if j != i else line_length + tip_length)
            for j in xrange(0, 3)
            ]
        axes_list.append(
            {
                'begin': begin,
                'end': format_vector(end),
                'tip': format_vector(tip),
                'radius': '%7.4f' % line_radius,
                'tip-base-radius': '%7.4f' % tip_radius,
                'colour': COLOURS[i]
            }
            )

    return axes_list
