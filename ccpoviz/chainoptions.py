"""
Chaining options together
=========================

Frequently we have to chain several option settings together, often from
several levels of configuration scope, like default value, system level, user
level, project level, individual file level. Although the standard
``collections`` library provides the ``ChainMap`` class for facilitating this
purpose from Python 3.3 on, it still lacks some composability and flexibility
for more complex configurations. Hence this module contains utilities for this
purpose. Also emphasis is put on verifying the correctness of the user input
and reporting the accurate position of the erroneous input.

The chaining mechanism here is mostly inspired by the usage of JSON as
configurations files, which has become more and more popular in recent years,
like the ``package.json`` used by npm, Grunt and the configuration files used
by Sublime Text and most of its add-on packages. However, it is in no way
restricted to JSON. It operates directly on a model for option configurations
that is expressible in basic Python as well as quite a wide myriad of other
common modern computer languages. So it could work in conjunction with any
file, environment variable, or command line argument readers able to translate
the configuration into this model. The model for a configuration consists of

Atom
    Atoms can be string, number, boolean, as supported in JSON. They are the
    terminal leaf nodes in the parse tree of a configuration. It needs to be
    noted that ``null`` is not a possible selection. The most frequent usage
    of null is the invocation of the default value, which is hard coded into
    the program. But here the more advocated approach is to put the default
    values together in a central place and invoke the default value by
    omitting the option in later configurations. Simple omission would be a
    much simpler way of invoking the default than having to assign a ``null``.

Map
    Mapping from **string** to values. Object in the JSON terms or dictionary
    in the Python terms,

List
    A **uniform** list of values, all values should be compliant with the same
    format,

Value
    A value can be an atom, a map, or a list.

And a configuration of the options of the program is a map acting as the root
of the parse tree. All options of the program should have got a definite
position within this tree. The recursive structure here can be seen as a
restriction of the space of valid python expressions formed from the atoms,
lists and dictionaries. Primarily, the first restriction is that the key in the
dictionary has to be string. This makes it a general model that is supported by
JSON and able to be transliterated into basically any other programming
languages, since string is a data type that is universally present and well-
suited to be used for option configurations. The second restriction is the
uniformity of the values in lists. This would greatly reduce the complexity of
the model and ease its configuration without greatly sacrificing the
flexibility of the model.

After the clearance about the definition of terms, here is the basic idea of
this module. By options usually we mean settings about the program that has
got default values hence optional. So the ``ChainOptions`` data type here
operates by semi-programmably patching the default configuration from later
input. The way that each option is updated and verified can be set by
specially-named **siblings** of the option in the map where the option is in.
Being options of options, these siblings are going to be termed meta-options.
The string tag for the meta- option is formed by appending a separator and a
meta-option tag to the tag for the option. In this way, in contrast to the
verbose `JSON schema`_, here simple configuration can be kept simple, while
complex configuration can be achievable, since no extra level in the parse
tree is added. Also, JSON schema gives the acceptable type for each option
explicitly, here the verification of the later options can be based on the
values of the default options, which serves two purposes of both default value
and data type settings here. This is more convenient for the purpose of
setting program options. Due to the scarcity of clean code supporting multiple
types for the same program option, the flexibility of the model will not be
significantly restricted.

For an example of a meta-option, if we have got an list option named
``highlight-patterns`` with the default value of ``["spam", "eggs"]``, when the
user feeds values like ``["foo", "bar"]`` for this option again, we could
append the values given by the user to the default list, or we could also just
overwrite the default list, among other ways to compose them. If we adopt a
separator of triple dots ``...`` and an option tag of ``update``, to switch
between these two kinds of behaviour, we could set in the default configuration

.. code:: Javascript

    {
        "highlight-patterns": ["spam", "eggs"],
        "highlight-patterns...update": "append"
    }

or set the meta-option to ``overwrite``. Similarly, other kinds of options for
the option can also be set in this way on the siblings. By giving sensible
default values to these meta-options, simple configurations can be easily
declared by a simple default configuration, with meta-settings added as needed.
The default can either be hard coded in a python dictionary or written in a
separate JSON or YAML file, which can be readily parsed into this model. If it
is written in a external JSON file, it might be more maintainable since it is
separated from the main program and it can be more easily adapted to other
programs. If it is written in Python, more programmability can be available,
for instance for the generation of the default values. Note that for the root
map, which has not siblings, the meta-options should be set with no setting
tag, just starting with the separator.

It needs to be noted that although the previous example is written in JSON,
this chaining mechanism just based on the model for the configuration and is
not restricted to JSON configurations at all. Small code can be written to
translate options from the ini-style configuration, environmental variables, or
even command line arguments to the nested structure elaborated above. Then they
can be chained together to form the final set of configurations. Just other
ways of configuration might lack some of the flexibility of JSON. Like it would
be hard to configure settings in nested maps from command lines arguments. The
purpose of this module is to make a code easily configurable in a variety ways
and scopes by using just a default configuration coded either in JSON or
Python.

Here are the detailed documentation of the meta-options for the options

update
    The way the value is going to be updated by the later configurations.
    Acceptable values depend on the type of the setting that it configures.
    For atoms, the only value and the default value is ``overwrite``, which
    will cause the old value to be overwritten by the new value. For lists,
    the acceptable values include ``overwrite``, which is the default and will
    make the new list overwrite the old list, and ``prepend`` and ``append``,
    which will prepend or append the new list onto the previous value.
    ``unique`` is also supported for list, which will merge the two lists but
    keep unique values only. Note that ``unique`` is for lists of atoms only.
    For maps, the default is ``modify``, which will set existing keys
    according to their ``update`` setting and issue error for any new keys not
    originally present. If it is not desired, ``extend`` can be used so that
    new keys not present in the previous configuration can be excepted. Please
    note that this assumes that the map, at least for the entries that is
    newly added, is a uniform one like a list. So prototype needs to be
    provided as explained later.

coercion
    A boolean value for atomic values. If set to true, type coercion is going
    to be attempted to convert the new value to the data type of the existing
    value. Error is issued only after the coercion is unsuccessful. If set to
    false, error is going to be immediately issued if the new value is found to
    be of a different type from the existing value.

prototype, prototype-key
    For addition to lists or maps, since it is not a direct update to a
    particular option, the meta-option ``prototype`` can be used for giving a
    default value to patch on. Or the default value can be obtained by
    ``prototype-key`` from indexing the existing value. For atomic values, the
    actual value of the prototype is actually unused. It just serve to provide
    the type for the option. For lists and maps, it serves as the basis of the
    patching. They actual way to update from the prototype, i.e. the meta-
    options for the prototype, can be provided by using a second separator
    under the tag ``prototype``. For example, to give that the prototype of a
    list named ``option`` needs to be updated by modification rather than
    extension, we can use ``"option...prototype...update": "modify"``. Note
    also that the actual tag indicating the prototype ``prototype`` can be
    changed in the actual implementation, as can the separator for the meta-
    options.

.. _JSON scheme: http://json-schema.org

"""

import functools


#
# The exception classes for error reporting
# -----------------------------------------
#

class UpdateError(Exception):

    """The class for reporting errors occurred during the update process

    This exception indicates that some user input is not compatible with the
    default. It needs to be initialized with two arguments, the first one
    should be a tuple giving the location where the problem occurs. The second
    one should be a formatted string describing the problem with that location.
    Exceptions in this class can be caught and formatted into pretty error
    message for the users.

    """

    pass


class DefaultError(Exception):

    """The class for reporting errors in the default settings

    This error is raised if there is something wrong with the default value.
    Different from the exception class :py:exc:`UpdateError`, this exception
    is mostly results of programmer error rather than user error. So it is
    advised not to catch it.

    """

    pass


#
# Type determination
# ------------------
#

# Some constants representing three kinds of node types
_NUMBER = 1
_BOOL = 2
_STRING = 3
_ATOMS = (1, 2, 3)
_LIST = 4
_MAP = 5


def _find_type(node):

    """Finds the type of a node

    :param node: The node to test
    :returns: One of the three module constants for the three types of nodes
    :raises ValueError: if the node is not of the correct acceptable type.

    """

    if isinstance(node, bool):
        return _BOOL
    elif isinstance(node, int) or isinstance(node, float):
        return _NUMBER
    elif isinstance(node, str):
        return _STRING
    elif isinstance(node, list):
        return _LIST
    elif isinstance(node, dict):
        return _MAP
    else:
        raise ValueError('unacceptable type %s' % type(node))


#
# Error reporting
# ---------------
#

def _report_type_error(tag, default):

    """Reports error caused by a mismatch of types.

    A :py:exc:`UpdateError` exception with the already-formatted second
    argument will be raised by this function.

    """

    default_type = _find_type(default)

    if default_type == _NUMBER:
        expectation = 'number'
    elif default_type == _BOOL:
        expectation = 'boolean'
    elif default_type == _STRING:
        expectation = 'string'
    elif default_type == _LIST:
        expectation = 'list'
    elif default_type == _MAP:
        expectation = 'map'
    else:
        assert 0

    raise UpdateError(
        tag,
        'a value of type %s is expected' % expectation
        )


#
# The main class
# --------------
#


class ChainOptions(object):

    """Option settings chainer

    This is an implementation of the options chainer described in this module.
    The implementation emphasizes flexibility is its usage. Basically all the
    default values for the meta-options can be set in the initializer and
    stored as attributes. Then the :py:meth:`chain_options` method can be
    invoked to do the actual job of chaining the options together.

    .. py:attribute:: separator

        The separator of the option tag with the meta-option tag. Default to
        ``...``.

    .. py:attribute:: proto_tag

       The tag for the prototype of nodes to be extended. Default to
       ``prototype``.

    .. py:attribute:: default_list_update, default_map_update

        The default update method for lists and maps, currently defaults to
        ``overwrite`` for both of them for compatibility with the standard
        library ``ChainMap`` class.

    .. py:attribute:: default_coercion

        The default value of if the type coercion is going to be performed for
        atomic input with different types. Defaults to false.

    """

    __slots__ = [
        'separator',
        'proto_tag',
        'default_list_update',
        'default_map_update',
        'default_coercion',
        ]

    def __init__(self, separator='...', proto_tag='prototype',
                 default_list_update='overwrite',
                 default_map_update='overwrite', default_coercion=False):
        # pylint: disable=too-many-arguments

        """Initializes the options chainer according to the default values"""

        self.separator = separator
        self.proto_tag = proto_tag
        self.default_list_update = default_list_update
        self.default_map_update = default_map_update
        self.default_coercion = default_coercion

    def _get_proto(self, tag, context, existing):

        """Try to get the prototype for the node with tag

        This is useful for adding new entries to list or maps. If no prototype
        or prototype update method is found in the context, the default value
        for the entries in the existing node will be used.

        Getting the prototype is generally straightforward to understand. For
        the virtual context, it is needed whenever a new node is added to the
        options tree. Generally, meta-options for each option node should be a
        sibling to the actual option node. But for new nodes added based on a
        prototype, the location of the new node added and the prototype is
        actually different, with the prototype one level higher. To make the
        settings consist towards users, the meta-options for the prototypes
        are put as siblings to the prototypes by using essentially the same
        format in the key as the normal nodes. In addition, for nodes in a
        list, since the list cannot have a special entry to hold the meta-
        options for the actual nodes, we have to put it one-level (or levels
        for nested-list) higher into the dictionary holding the list. From
        this discrepancy of the location of the prototype and the actual
        location of nodes that is added based on it, we need to pass the meta-
        options for the prototype downwards somehow. In this implementation,
        the meta-settings of the prototype is found and bundled into a special
        context called virtual context.

        :param tag: The tag for the node within the context
        :param context: The context (dictionary) in which the node is
        :param existing: The existing node
        :returns: A pair, with the first component being the prototype of the
            node. The second component is a dictionary able to serve as the
            virtual context to update the prototype.
        :raises DefaultError: if something goes wrong, like the key cannot be
            found in the existing node.

        """

        # pylint: disable=too-many-branches

        # Try to get the basis for the list elements
        proto = None  # prototype or basis
        existing_type = _find_type(existing)

        # Try to get the meta-settings from an explicitly-given prototype or
        # key
        for i in [self.proto_tag, self.proto_tag + '-key']:

            meta_tag = tag + self.separator + i
            # raise exception if more than one meta-setting is given
            if meta_tag in context and proto is not None:
                raise DefaultError(
                    'Meta-setting %s duplicates with others' % meta_tag
                    )

            if meta_tag in context:
                raw_value = context[meta_tag]

                # if it is a key, get the actual one from the existing
                if i.endswith('-key'):
                    try:
                        if existing_type == _MAP:
                            proto = existing[raw_value]
                        elif existing_type == _LIST:
                            if type(raw_value) != int:
                                raise IndexError()
                            else:
                                proto = existing[raw_value]
                        elif existing_type in _ATOMS:
                            # raise error for atomic nodes that cannot be
                            # indexed
                            raise IndexError()
                        else:
                            assert 0
                    except IndexError:
                        raise DefaultError(
                            'The prototype key %s '
                            'cannot be found for %s' % (raw_value, tag)
                            )
                # When the prototype is given explicitly
                else:
                    proto = raw_value

            # Continue to the next loop no matter what.
            # To have a check if others has also been set
            continue

        # Try to get a prototype from the existing ones when none of the meta-
        # settings are given.
        if proto is None:
            try:
                if existing_type == _LIST:
                    proto = existing[0]
                elif existing_type == _MAP:
                    proto = next(existing.itervalues())
            except (IndexError, StopIteration):
                raise DefaultError(
                    'No prototype/basis given for empty list/map %s' % tag
                    )

        # Try to get the virtual context for the prototype
        virt_prefix = tag + self.separator + self.proto_tag + self.separator
        virt_context = {
            k[len(tag + self.separator):]: v
            for k, v in context.iteritems()
            if k.startswith(virt_prefix)
            }

        return (proto, virt_context)

    def remove_proto(self, tag):

        """Removes the prototype tags from the tag path

        When adding a new node to the option tree and thus updating from the
        prototype, a dummy layer with the prototype tag is added to the tags
        path to be able to get the meta-options from the virtual context. This
        extra-layer might cause some confusion on the user when the error
        message is tried to be deciphered. So this function is added to be able
        to remove the technical layers for cleaner error position directly
        corresponding to the user input, if the pretty formatter chooses to not
        to print the special tags.

        """

        return tuple(i for i in tag if i != self.proto_tag)

    #
    # ### Node update methods ###
    #
    # The methods to update a node based on a new code. All the functions have
    # a common signature of ``existing``, ``new``, ``tag``, ``context``. The
    # ``existing`` is the old node to update. And ``new`` is the new value.
    # ``tag`` is the tuple giving the location of the **new** node is the new
    # option configuration. And ``context`` is the dictionary for finding the
    # meta-options. Usually it is the parent of the existing node in the old
    # configuration tree, or a virtual context for the prototype. The last
    # element of the tag is always used for finding the meta-options in the
    # context.
    #

    def _update_atom(self, existing, new, tag, context):

        """Updates an atom node"""

        new_type = _find_type(new)
        existing_type = _find_type(existing)
        coercion = context.get(
            tag[-1] + self.separator + 'coercion',
            self.default_coercion
            )
        try:
            if new_type == existing_type:
                return new
            elif coercion:
                return type(existing)(new)
            else:
                raise ValueError()
        except ValueError:
            _report_type_error(tag, existing)

    def _update_list(self, existing, new, tag, context):

        """Updates a list node"""

        new_type = _find_type(new)

        if new_type != _LIST:
            _report_type_error(tag, existing)

        # Get the tag of the setting
        tag_in_context = tag[-1]

        # Forward the virtual context
        proto, proto_context = self._get_proto(
            tag_in_context, context, existing
            )

        new_list = [
            self._update_node(
                proto, i, tag + (n, self.proto_tag),
                proto_context,
                )
            for n, i in enumerate(new)
            ]

        update = context.get(
            tag_in_context + self.separator + 'update',
            self.default_list_update
            )

        if update == 'overwrite':
            return new_list
        elif update == 'prepend':
            return new_list + existing
        elif update == 'append':
            return existing + new_list
        elif update == 'unique':
            try:
                return list(set(existing + new_list))
            except TypeError:
                raise DefaultError(
                    'update method `unique` is for atom lists only'
                    )
        else:
            raise DefaultError(
                'Invalid list update value %s' % update
                )

    def _update_map(self, existing, new, tag, context):

        """Updates a map node"""

        new_type = _find_type(new)
        if new_type != _MAP:
            _report_type_error(tag, existing)

        # Get the update method
        tag_in_context = tag[-1]
        update = context.get(
            tag_in_context + self.separator + 'update',
            self.default_map_update
            )

        # get the prototype for extend
        if update == 'extend':
            proto, proto_context = self._get_proto(
                tag_in_context, context, existing
                )

        # Make a shallow copy of the old map
        new_map = dict(existing)
        # Update the old ones according to the new ones
        for k, v in new.iteritems():

            # Have a check about the new mapping key
            if k.find(self.separator) != -1:
                raise UpdateError(
                    tag,
                    'users are not supposed to taint meta-options'
                    )

            # Update old value or add new value
            if k in new_map:
                new_map[k] = self._update_node(
                    existing[k], v, tag + (k, ), existing
                    )
            else:
                if update == 'extend':
                    new_map[k] = self._update_node(
                        proto, v, tag + (k, self.proto_tag), proto_context
                        )
                else:
                    raise UpdateError(
                        tag + (k, ),
                        'invalid option'
                        )
        return new_map

    def _update_node(self, existing, new, tag, context):

        """Updates an existing node according to the new node

        The updated existing node will be returned, which is going to be of the
        same type as the one. This function is going to be called recursively
        and forms the core of this class.

        :param existing: The existing node to update
        :param new: The new node to be patched onto the existing one
        :param tag: The tag for the node to be updated, used for the purpose of
            better error reporting. Rather than a plain string, the tag here
            are a tuple giving the tag from the root of the configuration tree.
            In this way, the error message could be better formatted.
        :param context: The dictionary in which the setting is in, the place to
            find its meta-options.
        :returns: The new node after the update
        :raises UpdateError: if the new value is not compatible to update the
            existing value.

        """

        existing_type = _find_type(existing)

        # The main selection
        if existing_type in _ATOMS:

            return self._update_atom(existing, new, tag, context)

        elif existing_type == _LIST:

            return self._update_list(existing, new, tag, context)

        elif existing_type == _MAP:

            return self._update_map(existing, new, tag, context)

    def chain_options(self, *ops):

        """Chains multiple set of options together

        The options should be given as the positional arguments of this method.
        The last one is the default option, and the earlier ones takes higher
        precedence. The final set of options are going to be returned in the
        same structure as the arguments.

        """

        return functools.reduce(
            lambda d, u: self._update_node(d, u, ('', ), d),
            reversed(ops[:-1]), ops[-1]
            )

    def format_update_error(self, update_error):

        """Formats an update error exception into a pretty string

        Note that this function just returns a string based on an exception
        object, it does not either catch or throw the actual exception. It will
        also not terminate the program. This is just a reference implementation
        of an error message formatter. Programs are encouraged to implement
        their own error message formatter based on individual needs or
        aesthetic taste.

        :param update_error: The :py:instance:`UpdateError` instance to format
        :returns: A string describing the error to the user

        """

        tags = [
            i if isinstance(i, str) else str(i)
            for i in self.remove_proto(update_error.args[0])[1:]
            ]
        location = ' / '.join(tags)
        error = update_error.args[1]

        return '\n'.join([
            'At option setting ',
            '   ' + location,
            'error occurred since %s' % error
            ])
